"""LLM-built library of Q/R settings, one entry per GPS condition, switched online (research/research_map.md, G1+G2).

Pipeline per dataset:
  train part (normal GPS + the 5 m section)  --builder (LLM / random / DE)-->  library {condition: Q/R}
  test part (normal GPS, the 15 m section, the outage)  --GPS condition detector + library-->  Q/R in force
  unseen condition on the test part  --builder on the last seconds, GPS-only score-->  new library entry

Nothing in building or switching sees ground truth: settings are scored by how well the filter predicts the
next GPS fix (score.py). Ground truth is used only by evaluate.py.
"""
