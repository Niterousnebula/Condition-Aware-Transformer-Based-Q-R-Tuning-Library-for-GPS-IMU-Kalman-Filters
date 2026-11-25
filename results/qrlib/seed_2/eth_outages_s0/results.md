# eth_outages_s0

## Test part

Horizontal RMSE in m.

| method                                |   rmse_all |   rmse_heavy_15m |   rmse_outage |   rmse_recovery_30s |   rmse_outside |   nis_over_dof |   switches |   online_entries |
|:--------------------------------------|-----------:|-----------------:|--------------:|--------------------:|---------------:|---------------:|-----------:|-----------------:|
| Raw GPS                               |       5.78 |            15.2  |    nan        |                2.23 |           3.93 |        nan     |        nan |              nan |
| Baseline THETA0                       |     827    |             4.58 |      3.49e+03 |                2.4  |           4.12 |          0.54  |          0 |              nan |
| Paper 1 GWO (ground truth, offline)   |     497    |             5.72 |      2.1e+03  |                2.32 |           4.04 |          1.15  |          0 |              nan |
| Static (llm)                          |     462    |             4.12 |      1.95e+03 |                2.52 |           4.17 |          4.1   |          0 |              nan |
| Library (llm)                         |     591    |             3.77 |      2.5e+03  |                2.28 |           3.99 |          0.611 |          3 |              nan |
| Library, true condition (llm)         |     605    |             3.79 |      2.56e+03 |                2.28 |           3.99 |          0.618 |          2 |              nan |
| Library, no plausibility filter (llm) |     616    |             4.3  |      2.6e+03  |                2.29 |           3.99 |          0.861 |          4 |              nan |
| Static (gwo)                          |     501    |             4.18 |      2.11e+03 |                2.47 |           4.15 |          0.538 |          0 |              nan |
| Library (gwo)                         |     324    |             3.82 |      1.37e+03 |                2.29 |           4.01 |          0.554 |          3 |              nan |
| Library, true condition (gwo)         |     324    |             3.79 |      1.37e+03 |                2.29 |           4    |          0.56  |          2 |              nan |
| Library, no plausibility filter (gwo) |     315    |             4.01 |      1.33e+03 |                2.29 |           4.01 |          0.824 |          4 |              nan |
| Library + online update (llm)         |     523    |             3.51 |      2.21e+03 |                2.26 |           3.99 |          0.887 |        nan |                2 |
| Library + online update (gwo)         |     342    |             3.42 |      1.44e+03 |                2.39 |           4    |          0.612 |        nan |                2 |

## Training part (initialization period)

| method                    |   train_rmse_all |   train_rmse_moderate_5m |   train_rmse_moderate_5m_first10s |   train_rmse_outside |   tunings |
|:--------------------------|-----------------:|-------------------------:|----------------------------------:|---------------------:|----------:|
| THETA0                    |             3.6  |                     3.11 |                              2.83 |                 3.65 |       nan |
| Initialization mode (llm) |             3.55 |                     3.21 |                              3.4  |                 3.59 |        10 |
| Initialization mode (gwo) |             3.56 |                     3.22 |                              3.33 |                 3.6  |        10 |
