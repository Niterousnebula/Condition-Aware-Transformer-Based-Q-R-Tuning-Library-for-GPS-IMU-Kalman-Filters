# Figure captions

Shaded bands mark the injected GPS sections (5 m noise, 15 m noise, outage) and are drawn 50 % wider than the
sections, centred, so the short sections stay visible at the scale of a whole drive.

- **fig1_pipeline**: the system. The condition detector works on GPS fixes only; the library holds one Q/R
  setting per GPS condition; the builder (an LLM, or random search / GWO at the same budget) proposes
  settings scored on GPS only, from the drive start (initialization mode) and when a new condition appears.
- **fig2_detector**: estimated GPS noise and the detected condition against the true sections, whole drive.
- **fig3_onset**: horizontal error at the start of the 15 m section (solid line: where the noise starts):
  THETA0, the library without the plausibility filter, with the true condition, and as deployed (detected
  condition).
- **fig4_test_error**: horizontal error over the test part: THETA0, paper 1's truth-tuned GWO setting and the
  library with online update.
- **fig5_score_check**: top, the GPS-only score against the true error over R settings on the noise sections;
  bottom, on normal-GPS windows, the score against the true drift over 30 s without GPS (Q settings included).
- **fig6_library**: the library's horizontal GPS noise setting per condition, in decades above THETA0, per
  builder and seed (R rises with the GPS noise).
- **fig7_initialization**: horizontal error from the drive start to the split, THETA0 against the
  initialization mode; ticks mark re-tunings.
- **fig8_headline**: RMSE in the 15 m section, on normal GPS and in the 30 s after the outage, mean and
  standard deviation over seeds.
