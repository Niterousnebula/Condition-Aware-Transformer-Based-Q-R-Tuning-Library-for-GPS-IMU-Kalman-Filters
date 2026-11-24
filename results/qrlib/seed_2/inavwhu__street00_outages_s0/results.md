# inavwhu/street00_outages_s0

## Test part

Horizontal RMSE in m.

| method                                   |   rmse_all |   rmse_heavy_15m |   rmse_outage |   rmse_recovery_30s |   rmse_outside |   nis_over_dof |   switches |   online_entries |
|:-----------------------------------------|-----------:|-----------------:|--------------:|--------------------:|---------------:|---------------:|-----------:|-----------------:|
| Raw GPS                                  |       4.83 |            16.9  |        nan    |               0.866 |           1.2  |     nan        |        nan |              nan |
| Baseline THETA0                          |       3.68 |            10.9  |          6.92 |               1.65  |           1.32 |       5.38     |          0 |              nan |
| Paper 1 GWO (ground truth, offline)      |       3    |             7.73 |          6.41 |               1.71  |           1.43 |       1.26     |          0 |              nan |
| Static (llm)                             |      83.4  |            48.6  |        308    |              79.6   |           4.61 |       1.04e+03 |          0 |              nan |
| Library (llm)                            |       7.22 |            10.1  |         24.6  |               6.89  |           1.28 |       3.62     |          3 |              nan |
| Library, true condition (llm)            |       7.14 |            10.2  |         24.2  |               6.81  |           1.28 |       4.07     |          2 |              nan |
| Library, no plausibility filter (llm)    |      30.2  |            14.7  |        112    |              26.9   |           1.35 |      35.5      |          3 |              nan |
| Static (random)                          |       3.26 |             9.61 |          5.95 |               1.97  |           1.28 |       5.7      |          0 |              nan |
| Library (random)                         |       7.67 |            10.6  |         26.2  |               7.86  |           1.29 |       4.92     |          2 |              nan |
| Library, true condition (random)         |       7.5  |            10.6  |         25.5  |               7.77  |           1.29 |       5.51     |          2 |              nan |
| Library, no plausibility filter (random) |      70.8  |            19.2  |        264    |              73.7   |           1.37 |      53.6      |          2 |              nan |
| Static (gwo)                             |       3.51 |             9.34 |          7.98 |               2.55  |           1.28 |       7.57     |          0 |              nan |
| Library (gwo)                            |       8.69 |             9.21 |         30.9  |               8.23  |           1.25 |       4.06     |          3 |              nan |
| Library, true condition (gwo)            |       8.9  |             9.43 |         31.6  |               8.43  |           1.24 |       4.55     |          2 |              nan |
| Library, no plausibility filter (gwo)    |      46.7  |            12.8  |        174    |              49.8   |           1.28 |      32.9      |          3 |              nan |
| Library + online update (llm)            |       9.48 |            25.3  |         24.1  |               6.77  |           1.38 |       1.85     |        nan |                2 |
| Library + online update (random)         |      15.1  |            45.7  |         25.8  |               7.77  |           5.66 |       2.69     |        nan |                2 |
| Library + online update (gwo)            |       8.8  |            10.1  |         31    |               8.26  |           1.25 |       2.04     |        nan |                2 |

## Training part (initialization period)

| method                       |   train_rmse_all |   train_rmse_moderate_5m |   train_rmse_moderate_5m_first10s |   train_rmse_outside |   tunings |
|:-----------------------------|-----------------:|-------------------------:|----------------------------------:|---------------------:|----------:|
| THETA0                       |             1.21 |                     2.81 |                              2.36 |                0.786 |       nan |
| Initialization mode (llm)    |             1.44 |                     3.66 |                              2.81 |                0.76  |         8 |
| Initialization mode (random) |             1.48 |                     3.8  |                              3.12 |                0.759 |         8 |
| Initialization mode (gwo)    |             1.42 |                     3.58 |                              2.71 |                0.766 |         8 |
