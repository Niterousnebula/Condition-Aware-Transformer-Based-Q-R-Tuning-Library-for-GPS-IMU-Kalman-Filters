# inavwhu/street00_outages_s0

## Test part

Horizontal RMSE in m.

| method                                |   rmse_all |   rmse_heavy_15m |   rmse_outage |   rmse_recovery_30s |   rmse_outside |   nis_over_dof |   switches |   online_entries |
|:--------------------------------------|-----------:|-----------------:|--------------:|--------------------:|---------------:|---------------:|-----------:|-----------------:|
| Raw GPS                               |       4.83 |            16.9  |        nan    |               0.866 |           1.2  |        nan     |        nan |              nan |
| Baseline THETA0                       |       3.68 |            10.9  |          6.92 |               1.65  |           1.32 |          5.38  |          0 |              nan |
| Paper 1 GWO (ground truth, offline)   |       3    |             7.73 |          6.41 |               1.71  |           1.43 |          1.26  |          0 |              nan |
| Static (llm)                          |       3.02 |             9.81 |          3.11 |               1.52  |           1.27 |          2.41  |          0 |              nan |
| Library (llm)                         |       7.34 |             7.21 |         26.1  |               7.55  |           1.23 |          0.315 |          3 |              nan |
| Library, true condition (llm)         |       7.31 |             7.27 |         26    |               7.52  |           1.23 |          0.342 |          2 |              nan |
| Library, no plausibility filter (llm) |      78.6  |            37.8  |        291    |              82.8   |           1.34 |         42.1   |          3 |              nan |
| Static (gwo)                          |       3.33 |             8.81 |          7.45 |               2.56  |           1.28 |          8.59  |          0 |              nan |
| Library (gwo)                         |       6.45 |             7.2  |         22.5  |               7.04  |           1.23 |          0.328 |          3 |              nan |
| Library, true condition (gwo)         |       6.4  |             7.23 |         22.3  |               6.98  |           1.22 |          0.356 |          2 |              nan |
| Library, no plausibility filter (gwo) |      79.5  |            47    |        294    |              76.4   |           4.43 |         38.9   |          3 |              nan |
| Library + online update (llm)         |       7.26 |             6.85 |         25.9  |               7.5   |           1.27 |          0.648 |        nan |                2 |
| Library + online update (gwo)         |       6.45 |             7.2  |         22.5  |               7.04  |           1.23 |          0.327 |        nan |                2 |

## Training part (initialization period)

| method                    |   train_rmse_all |   train_rmse_moderate_5m |   train_rmse_moderate_5m_first10s |   train_rmse_outside |   tunings |
|:--------------------------|-----------------:|-------------------------:|----------------------------------:|---------------------:|----------:|
| THETA0                    |             1.21 |                     2.81 |                              2.36 |                0.786 |       nan |
| Initialization mode (llm) |             1.78 |                     4.78 |                              3.68 |                0.759 |         8 |
| Initialization mode (gwo) |             1.77 |                     4.76 |                              3.66 |                0.762 |         8 |
