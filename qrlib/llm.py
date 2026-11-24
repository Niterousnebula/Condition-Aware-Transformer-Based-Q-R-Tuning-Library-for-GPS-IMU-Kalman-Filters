"""The LLM that proposes Q/R settings: a local llama-server (default) or an in-process Hugging Face model."""
import torch

from . import config as C

_MODEL = {}


def load(path=C.LLM_PATH):
    if "model" not in _MODEL:
        from transformers import AutoModelForCausalLM, AutoTokenizer
        tok = AutoTokenizer.from_pretrained(path)
        model = AutoModelForCausalLM.from_pretrained(path, dtype=torch.bfloat16).to("cuda")
        model.eval()
        stop = [i for i in (tok.convert_tokens_to_ids("<|im_end|>"), tok.eos_token_id) if i is not None]
        _MODEL.update(model=model, tok=tok, stop=stop)
    return _MODEL["model"], _MODEL["tok"], _MODEL["stop"]


class _Done:
    """Stops generation once done(text so far) is true (checked every 8 tokens)."""

    def __init__(self, tok, n_prompt, done):
        self.tok, self.n_prompt, self.done, self.k = tok, n_prompt, done, 0

    def __call__(self, input_ids, scores, **kw):
        self.k += 1
        if self.done is None or self.k % 8:
            return torch.zeros(input_ids.shape[0], dtype=torch.bool, device=input_ids.device)
        text = self.tok.decode(input_ids[0, self.n_prompt:], skip_special_tokens=True)
        return torch.full((input_ids.shape[0],), bool(self.done(text)), dtype=torch.bool, device=input_ids.device)


def chat(system, user, seed, max_new_tokens=C.LLM_MAX_NEW_TOKENS, done=None):
    """One sampled reply from the configured backend (C.LLM_BACKEND). Returns (text, n_prompt, n_new)."""
    if C.LLM_BACKEND == "server":
        return _chat_server(system, user, seed, max_new_tokens)
    return _chat_local(system, user, seed, max_new_tokens, done)


def check_server():
    """Raise a clear error when the configured llama-server is not answering."""
    import urllib.request
    base = C.LLM_URL.split("/v1/")[0]
    try:
        with urllib.request.urlopen(base + "/health", timeout=5) as r:
            ok = r.status == 200
    except Exception as e:                                   # noqa: BLE001 - any failure means "not running"
        ok, err = False, e
    if not ok:
        raise RuntimeError(f"no LLM server at {base} (start llama-server first, see LLM_URL in qrlib/config.py)")


def _chat_server(system, user, seed, max_new_tokens):
    """llama-server's OpenAI-compatible endpoint on this machine (nothing leaves it)."""
    import json
    import urllib.request
    body = {"model": C.LLM_MODEL, "temperature": C.LLM_TEMPERATURE, "top_p": C.LLM_TOP_P, "seed": int(seed),
            "max_tokens": int(max_new_tokens), "stop": ["]]}"],
            "chat_template_kwargs": {"enable_thinking": bool(C.LLM_THINKING)},
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}
    req = urllib.request.Request(C.LLM_URL, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    out = None
    for attempt in range(C.LLM_RETRIES + 1):          # a slow or dropped call must not end an overnight run
        try:
            with urllib.request.urlopen(req, timeout=C.LLM_TIMEOUT_S) as r:
                out = json.loads(r.read())
            break
        except Exception as e:                          # noqa: BLE001 - timeout, connection reset, bad JSON
            print(f"    LLM call failed ({type(e).__name__}: {e}); attempt {attempt + 1} of {C.LLM_RETRIES + 1}",
                  flush=True)
    if out is None:
        return "", 0, 0                                 # counted as unparsed; the proposer fills near the best
    msg = out["choices"][0]["message"]
    text = (msg.get("content") or "") + "]]}"         # the server drops the stop string; give the last list its "]"
    if msg.get("reasoning_content"):
        text = msg["reasoning_content"] + "\n" + text
    use = out.get("usage", {})
    return text, int(use.get("prompt_tokens", 0)), int(use.get("completion_tokens", 0))


@torch.no_grad()
def _chat_local(system, user, seed, max_new_tokens=C.LLM_MAX_NEW_TOKENS, done=None):
    """One sampled reply from the in-process model; generation also stops at "]]}" or once done(text) holds."""
    from transformers import StoppingCriteriaList
    model, tok, stop = load()
    msgs = [{"role": "system", "content": system}, {"role": "user", "content": user}]
    ids = tok.apply_chat_template(msgs, add_generation_prompt=True, return_tensors="pt").to(model.device)
    torch.manual_seed(seed)
    out = model.generate(ids, attention_mask=torch.ones_like(ids), do_sample=True, temperature=C.LLM_TEMPERATURE,
                         top_p=C.LLM_TOP_P, max_new_tokens=max_new_tokens, eos_token_id=stop,
                         pad_token_id=stop[0], stop_strings=["]]}"], tokenizer=tok,
                         stopping_criteria=StoppingCriteriaList([_Done(tok, ids.shape[1], done)]))
    new = out[0, ids.shape[1]:]
    return tok.decode(new, skip_special_tokens=True), int(ids.shape[1]), int(len(new))


def unload():
    _MODEL.clear()
    torch.cuda.empty_cache()
