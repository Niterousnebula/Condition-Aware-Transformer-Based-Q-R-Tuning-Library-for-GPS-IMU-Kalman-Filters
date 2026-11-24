# inavwhu/playground00_outages_s0

## Test part

Horizontal RMSE in m.

| method                                   |   rmse_all |   rmse_heavy_15m |   rmse_outage |   rmse_recovery_30s |   rmse_outside |   nis_over_dof |   switches |   online_entries |
|:-----------------------------------------|-----------:|-----------------:|--------------:|--------------------:|---------------:|---------------:|-----------:|-----------------:|
| Raw GPS                                  |       4.74 |            17.2  |        nan    |                1.49 |           1.32 |        nan     |        nan |              nan |
| Baseline THETA0                          |      15.6  |            11.8  |         56    |               24.4  |           1.57 |          7.48  |          0 |              nan |
| Paper 1 GWO (ground truth, offline)      |       3.34 |             7.76 |          8.27 |                4.18 |           1.57 |          1.32  |          0 |              nan |
| Static (llm)                             |       5.03 |             9.44 |         15.4  |                7.05 |           1.52 |          9.21  |          0 |              nan |
| Library (llm)                            |       3.35 |            10.1  |          6.02 |                3.08 |           1.53 |          3.15  |          3 |              nan |
| Library, true condition (llm)            |       3.34 |            10.1  |          5.61 |                2.92 |           1.63 |          3.4   |          2 |              nan |
| Library, no plausibility filter (llm)    |      11.6  |            16.1  |         39.5  |               17.8  |           1.7  |         21.4   |          3 |              nan |
| Static (random)                          |       7.39 |             9.25 |         25.2  |               11.3  |           1.53 |          1.92  |          0 |              nan |
| Library (random)                         |       3.43 |            10.2  |          6.31 |                3.15 |           1.55 |          0.481 |          2 |              nan |
| Library, true condition (random)         |       3.57 |            10.4  |          6.51 |                3.24 |           1.76 |          0.54  |          2 |              nan |
| Library, no plausibility filter (random) |      29.3  |            20    |        106    |               48.1  |           1.49 |         17.8   |          2 |              nan |
| Static (gwo)                             |       7.38 |             9.01 |         25.2  |               11.4  |           1.52 |          4.5   |          0 |              nan |
| Library (gwo)                            |       4.97 |            10.2  |         14.5  |                7.1  |           1.54 |          2.71  |          2 |              nan |
| Library, true condition (gwo)            |       4.81 |            10.1  |         13.7  |                6.76 |           1.63 |          2.88  |          2 |              nan |
| Library, no plausibility filter (gwo)    |      21.2  |            24.9  |         75.3  |               27.7  |           2.01 |         36.2   |          2 |              nan |
| Library + online update (llm)            |       4.5  |            14.2  |          7.91 |                3.85 |           1.74 |          3.93  |        nan |                2 |
| Library + online update (random)         |       3.48 |            10.5  |          6.63 |                3.27 |           1.43 |          0.431 |        nan |                2 |
| Library + online update (gwo)            |       4.97 |            10.2  |         14.5  |                7.1  |           1.54 |          2.71  |        nan |                2 |

## Training part (initialization period)

| method                       |   train_rmse_all |   train_rmse_moderate_5m |   train_rmse_moderate_5m_first10s |   train_rmse_outside |   tunings |
|:-----------------------------|-----------------:|-------------------------:|----------------------------------:|---------------------:|----------:|
| THETA0                       |             1.22 |                     2.81 |                              2.35 |                0.796 |       nan |
| Initialization mode (llm)    |             1.42 |                     3.54 |                              3.39 |                0.787 |         8 |
| Initialization mode (random) |             1.56 |                     4.05 |                              3.53 |                0.779 |         8 |
| Initialization mode (gwo)    |             1.53 |                     3.91 |                              4.07 |                0.797 |         8 |
