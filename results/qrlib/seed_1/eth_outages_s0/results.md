# eth_outages_s0

## Test part

Horizontal RMSE in m.

| method                                |   rmse_all |   rmse_heavy_15m |   rmse_outage |   rmse_recovery_30s |   rmse_outside |   nis_over_dof |   switches |   online_entries |
|:--------------------------------------|-----------:|-----------------:|--------------:|--------------------:|---------------:|---------------:|-----------:|-----------------:|
| Raw GPS                               |       5.78 |            15.2  |    nan        |                2.23 |           3.93 |        nan     |        nan |              nan |
| Baseline THETA0                       |     827    |             4.58 |      3.49e+03 |                2.4  |           4.12 |          0.54  |          0 |              nan |
| Paper 1 GWO (ground truth, offline)   |     497    |             5.72 |      2.1e+03  |                2.32 |           4.04 |          1.15  |          0 |              nan |
| Static (llm)                          |     476    |             4.06 |      2.01e+03 |                2.55 |           4.19 |          3.88  |          0 |              nan |
| Library (llm)                         |     529    |             3.77 |      2.24e+03 |                2.44 |           4.11 |          0.933 |          3 |              nan |
| Library, true condition (llm)         |     524    |             3.79 |      2.21e+03 |                2.44 |           4.11 |          0.943 |          2 |              nan |
| Library, no plausibility filter (llm) |     529    |             3.97 |      2.24e+03 |                2.44 |           4.11 |          1.04  |          4 |              nan |
| Static (gwo)                          |     403    |             3.63 |      1.7e+03  |                2.66 |           4.28 |          1.29  |          0 |              nan |
| Library (gwo)                         |     498    |             3.82 |      2.1e+03  |                2.25 |           3.97 |          0.432 |          3 |              nan |
| Library, true condition (gwo)         |     503    |             3.8  |      2.12e+03 |                2.25 |           3.97 |          0.437 |          2 |              nan |
| Library, no plausibility filter (gwo) |     560    |             4.43 |      2.37e+03 |                2.26 |           3.98 |          0.792 |          4 |              nan |
| Library + online update (llm)         |     446    |             4.32 |      1.88e+03 |                2.38 |           4.11 |          1.45  |        nan |                2 |
| Library + online update (gwo)         |     466    |             3.64 |      1.97e+03 |                2.25 |           3.97 |          0.627 |        nan |                2 |

## Training part (initialization period)

| method                    |   train_rmse_all |   train_rmse_moderate_5m |   train_rmse_moderate_5m_first10s |   train_rmse_outside |   tunings |
|:--------------------------|-----------------:|-------------------------:|----------------------------------:|---------------------:|----------:|
| THETA0                    |             3.6  |                     3.11 |                              2.83 |                 3.65 |       nan |
| Initialization mode (llm) |             3.61 |                     3.29 |                              3.21 |                 3.65 |        10 |
| Initialization mode (gwo) |             3.56 |                     3.35 |                              3.36 |                 3.58 |        10 |
