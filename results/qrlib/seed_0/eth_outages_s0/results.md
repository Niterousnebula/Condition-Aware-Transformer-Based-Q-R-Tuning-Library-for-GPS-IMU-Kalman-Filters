# eth_outages_s0

## Test part

Horizontal RMSE in m.

| method                                |   rmse_all |   rmse_heavy_15m |   rmse_outage |   rmse_recovery_30s |   rmse_outside |   nis_over_dof |   switches |   online_entries |
|:--------------------------------------|-----------:|-----------------:|--------------:|--------------------:|---------------:|---------------:|-----------:|-----------------:|
| Raw GPS                               |       5.78 |            15.2  |    nan        |                2.23 |           3.93 |        nan     |        nan |              nan |
| Baseline THETA0                       |     827    |             4.58 |      3.49e+03 |                2.4  |           4.12 |          0.54  |          0 |              nan |
| Paper 1 GWO (ground truth, offline)   |     497    |             5.72 |      2.1e+03  |                2.32 |           4.04 |          1.15  |          0 |              nan |
| Static (llm)                          |     529    |             6.47 |      2.24e+03 |                2.29 |           4.01 |          1.46  |          0 |              nan |
| Library (llm)                         |     479    |             3.77 |      2.02e+03 |                2.22 |           3.93 |          0.565 |          3 |              nan |
| Library, true condition (llm)         |     471    |             3.75 |      1.99e+03 |                2.22 |           3.93 |          0.573 |          2 |              nan |
| Library, no plausibility filter (llm) |     553    |             5.77 |      2.34e+03 |                2.22 |           3.93 |          7.16  |          4 |              nan |
| Static (gwo)                          |     520    |             3.38 |      2.2e+03  |                2.73 |           4.38 |         15.9   |          0 |              nan |
| Library (gwo)                         |     424    |             3.78 |      1.79e+03 |                2.33 |           4.05 |          0.556 |          3 |              nan |
| Library, true condition (gwo)         |     441    |             3.81 |      1.87e+03 |                2.34 |           4.05 |          0.562 |          2 |              nan |
| Library, no plausibility filter (gwo) |     484    |             3.95 |      2.04e+03 |                2.35 |           4.06 |          0.726 |          4 |              nan |
| Library + online update (llm)         |     474    |             3.79 |      2e+03    |                2.22 |           3.93 |          0.667 |        nan |                2 |
| Library + online update (gwo)         |     404    |             3.37 |      1.71e+03 |                2.35 |           4.05 |          0.518 |        nan |                2 |

## Training part (initialization period)

| method                    |   train_rmse_all |   train_rmse_moderate_5m |   train_rmse_moderate_5m_first10s |   train_rmse_outside |   tunings |
|:--------------------------|-----------------:|-------------------------:|----------------------------------:|---------------------:|----------:|
| THETA0                    |             3.6  |                     3.11 |                              2.83 |                 3.65 |       nan |
| Initialization mode (llm) |             3.54 |                     3.29 |                              3.83 |                 3.57 |        10 |
| Initialization mode (gwo) |             3.58 |                     3.23 |                              3.29 |                 3.62 |        10 |
