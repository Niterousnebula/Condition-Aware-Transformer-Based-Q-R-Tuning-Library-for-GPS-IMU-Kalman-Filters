# eth_outages_s0

## Test part

Horizontal RMSE in m.

| method                                   |   rmse_all |   rmse_heavy_15m |   rmse_outage |   rmse_recovery_30s |   rmse_outside |   nis_over_dof |   switches |   online_entries |
|:-----------------------------------------|-----------:|-----------------:|--------------:|--------------------:|---------------:|---------------:|-----------:|-----------------:|
| Raw GPS                                  |       5.78 |            15.2  |    nan        |                2.23 |           3.93 |        nan     |        nan |              nan |
| Baseline THETA0                          |     827    |             4.58 |      3.49e+03 |                2.4  |           4.12 |          0.54  |          0 |              nan |
| Paper 1 GWO (ground truth, offline)      |     497    |             5.72 |      2.1e+03  |                2.32 |           4.04 |          1.15  |          0 |              nan |
| Static (llm)                             |     529    |             6.47 |      2.24e+03 |                2.29 |           4.01 |          1.46  |          0 |              nan |
| Library (llm)                            |     482    |             3.9  |      2.04e+03 |                2.22 |           3.93 |          0.511 |          3 |              nan |
| Library, true condition (llm)            |     474    |             3.88 |      2e+03    |                2.22 |           3.93 |          0.518 |          2 |              nan |
| Library, no plausibility filter (llm)    |     556    |             5.83 |      2.35e+03 |                2.22 |           3.93 |          7.1   |          4 |              nan |
| Static (random)                          |     450    |             4.07 |      1.9e+03  |                2.56 |           4.2  |          7.04  |          0 |              nan |
| Library (random)                         |     516    |             4.56 |      2.18e+03 |                2.27 |           3.99 |          0.539 |          3 |              nan |
| Library, true condition (random)         |     508    |             4.51 |      2.15e+03 |                2.27 |           3.99 |          0.55  |          2 |              nan |
| Library, no plausibility filter (random) |     523    |             4.8  |      2.21e+03 |                2.27 |           3.99 |          0.814 |          4 |              nan |
| Static (gwo)                             |     520    |             3.38 |      2.2e+03  |                2.73 |           4.38 |         15.9   |          0 |              nan |
| Library (gwo)                            |     358    |             4.51 |      1.51e+03 |                2.34 |           4.05 |          0.683 |          3 |              nan |
| Library, true condition (gwo)            |     363    |             4.52 |      1.53e+03 |                2.34 |           4.05 |          0.691 |          2 |              nan |
| Library, no plausibility filter (gwo)    |     388    |             4.6  |      1.64e+03 |                2.33 |           4.05 |          0.84  |          4 |              nan |
| Library + online update (llm)            |     497    |             5.78 |      2.1e+03  |                2.22 |           3.97 |          0.904 |        nan |                2 |
| Library + online update (random)         |     520    |             4.24 |      2.2e+03  |                2.28 |           3.99 |          0.805 |        nan |                2 |
| Library + online update (gwo)            |     459    |             4.08 |      1.94e+03 |                2.35 |           4.06 |          1.18  |        nan |                2 |

## Training part (initialization period)

| method                       |   train_rmse_all |   train_rmse_moderate_5m |   train_rmse_moderate_5m_first10s |   train_rmse_outside |   tunings |
|:-----------------------------|-----------------:|-------------------------:|----------------------------------:|---------------------:|----------:|
| THETA0                       |             3.6  |                     3.11 |                              2.83 |                 3.65 |       nan |
| Initialization mode (llm)    |             3.54 |                     3.33 |                              3.83 |                 3.57 |        10 |
| Initialization mode (random) |             3.56 |                     3.3  |                              3.39 |                 3.59 |        10 |
| Initialization mode (gwo)    |             3.58 |                     3.22 |                              3.29 |                 3.62 |        10 |
