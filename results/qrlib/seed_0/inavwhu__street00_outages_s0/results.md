# inavwhu/street00_outages_s0

## Test part

Horizontal RMSE in m.

| method                                   |   rmse_all |   rmse_heavy_15m |   rmse_outage |   rmse_recovery_30s |   rmse_outside |   nis_over_dof |   switches |   online_entries |
|:-----------------------------------------|-----------:|-----------------:|--------------:|--------------------:|---------------:|---------------:|-----------:|-----------------:|
| Raw GPS                                  |       4.83 |            16.9  |        nan    |               0.866 |           1.2  |         nan    |        nan |              nan |
| Baseline THETA0                          |       3.68 |            10.9  |          6.92 |               1.65  |           1.32 |           5.38 |          0 |              nan |
| Paper 1 GWO (ground truth, offline)      |       3    |             7.73 |          6.41 |               1.71  |           1.43 |           1.26 |          0 |              nan |
| Static (llm)                             |       3.12 |            10.3  |          3    |               1.34  |           1.28 |           4.04 |          0 |              nan |
| Library (llm)                            |       7.55 |             9.51 |         26.1  |               7.85  |           1.25 |           3.79 |          3 |              nan |
| Library, true condition (llm)            |       7.49 |             9.5  |         25.9  |               7.83  |           1.24 |           4.25 |          2 |              nan |
| Library, no plausibility filter (llm)    |      38.2  |            16.9  |        142    |              37.3   |           1.35 |          41.4  |          3 |              nan |
| Static (random)                          |       8.29 |            10.1  |         29    |               6.58  |           1.47 |         458    |          0 |              nan |
| Library (random)                         |       7.65 |             9.69 |         26.6  |               7.21  |           1.25 |           3.86 |          3 |              nan |
| Library, true condition (random)         |       7.43 |             9.81 |         25.6  |               7.01  |           1.25 |           4.34 |          2 |              nan |
| Library, no plausibility filter (random) |      71.1  |            16.1  |        265    |              72.2   |           1.26 |          57    |          3 |              nan |
| Static (gwo)                             |       3.33 |             8.81 |          7.45 |               2.56  |           1.28 |           8.59 |          0 |              nan |
| Library (gwo)                            |       6.75 |            10.7  |         22.3  |               6.98  |           1.29 |           4.93 |          2 |              nan |
| Library, true condition (gwo)            |       6.48 |            10.7  |         21.1  |               6.78  |           1.28 |           5.53 |          2 |              nan |
| Library, no plausibility filter (gwo)    |      73.7  |            22.7  |        276    |              68.1   |           1.38 |          44.2  |          2 |              nan |
| Library + online update (llm)            |      11.1  |            30.8  |         25.9  |               7.8   |           2.73 |           1.78 |        nan |                2 |
| Library + online update (random)         |      14.8  |            46.6  |         24.5  |               6.72  |           4.65 |           1.86 |        nan |                2 |
| Library + online update (gwo)            |       6.74 |            10.7  |         22.3  |               6.97  |           1.29 |           4.93 |        nan |                2 |

## Training part (initialization period)

| method                       |   train_rmse_all |   train_rmse_moderate_5m |   train_rmse_moderate_5m_first10s |   train_rmse_outside |   tunings |
|:-----------------------------|-----------------:|-------------------------:|----------------------------------:|---------------------:|----------:|
| THETA0                       |             1.21 |                     2.81 |                              2.36 |                0.786 |       nan |
| Initialization mode (llm)    |             1.43 |                     3.65 |                              2.79 |                0.76  |         8 |
| Initialization mode (random) |             1.47 |                     3.77 |                              3.24 |                0.76  |         8 |
| Initialization mode (gwo)    |             1.48 |                     3.82 |                              3.14 |                0.763 |         8 |
