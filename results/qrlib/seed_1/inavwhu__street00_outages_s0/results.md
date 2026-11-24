# inavwhu/street00_outages_s0

## Test part

Horizontal RMSE in m.

| method                                   |   rmse_all |   rmse_heavy_15m |   rmse_outage |   rmse_recovery_30s |   rmse_outside |   nis_over_dof |   switches |   online_entries |
|:-----------------------------------------|-----------:|-----------------:|--------------:|--------------------:|---------------:|---------------:|-----------:|-----------------:|
| Raw GPS                                  |       4.83 |            16.9  |        nan    |               0.866 |           1.2  |         nan    |        nan |              nan |
| Baseline THETA0                          |       3.68 |            10.9  |          6.92 |               1.65  |           1.32 |           5.38 |          0 |              nan |
| Paper 1 GWO (ground truth, offline)      |       3    |             7.73 |          6.41 |               1.71  |           1.43 |           1.26 |          0 |              nan |
| Static (llm)                             |       3.14 |             9.35 |          5.39 |               2.09  |           1.27 |           2.39 |          0 |              nan |
| Library (llm)                            |       7.47 |            10.1  |         25.6  |               7.17  |           1.27 |           3.95 |          3 |              nan |
| Library, true condition (llm)            |       7.03 |            10.2  |         23.7  |               6.76  |           1.27 |           4.43 |          2 |              nan |
| Library, no plausibility filter (llm)    |      92.9  |            16.3  |        347    |              95.9   |           1.26 |          45.6  |          3 |              nan |
| Static (random)                          |       3.59 |             9.95 |          7.72 |               2.7   |           1.27 |           2.02 |          0 |              nan |
| Library (random)                         |       8.58 |            10.9  |         29.8  |               8.53  |           1.29 |           4.88 |          2 |              nan |
| Library, true condition (random)         |       7.82 |            10.9  |         26.7  |               7.79  |           1.29 |           5.47 |          2 |              nan |
| Library, no plausibility filter (random) |      49.6  |            15.9  |        186    |              42.5   |           1.37 |          37.6  |          2 |              nan |
| Static (gwo)                             |       3.49 |             8.77 |          8.45 |               2.84  |           1.28 |           3.32 |          0 |              nan |
| Library (gwo)                            |       7.08 |             9.1  |         24.5  |               6.85  |           1.24 |           4.4  |          3 |              nan |
| Library, true condition (gwo)            |       7.02 |             9.2  |         24.2  |               6.8   |           1.23 |           4.93 |          2 |              nan |
| Library, no plausibility filter (gwo)    |      54.6  |            14.9  |        203    |              58.7   |           1.31 |          53.3  |          3 |              nan |
| Library + online update (llm)            |      15    |            48    |         24.8  |               6.97  |           3.99 |           1.61 |        nan |                2 |
| Library + online update (random)         |      11.2  |            29    |         29.3  |               8.42  |           1.42 |           2.04 |        nan |                2 |
| Library + online update (gwo)            |       7.09 |             9.11 |         24.5  |               6.85  |           1.24 |          10.4  |        nan |                2 |

## Training part (initialization period)

| method                       |   train_rmse_all |   train_rmse_moderate_5m |   train_rmse_moderate_5m_first10s |   train_rmse_outside |   tunings |
|:-----------------------------|-----------------:|-------------------------:|----------------------------------:|---------------------:|----------:|
| THETA0                       |             1.21 |                     2.81 |                              2.36 |                0.786 |       nan |
| Initialization mode (llm)    |             1.47 |                     3.77 |                              3.14 |                0.759 |         8 |
| Initialization mode (random) |             1.51 |                     3.91 |                              3.28 |                0.76  |         8 |
| Initialization mode (gwo)    |             1.43 |                     3.64 |                              2.96 |                0.762 |         8 |
