# inavwhu/street00_outages_s0

## Test part

Horizontal RMSE in m.

| method                                |   rmse_all |   rmse_heavy_15m |   rmse_outage |   rmse_recovery_30s |   rmse_outside |   nis_over_dof |   switches |   online_entries |
|:--------------------------------------|-----------:|-----------------:|--------------:|--------------------:|---------------:|---------------:|-----------:|-----------------:|
| Raw GPS                               |       4.83 |            16.9  |        nan    |               0.866 |           1.2  |        nan     |        nan |              nan |
| Baseline THETA0                       |       3.68 |            10.9  |          6.92 |               1.65  |           1.32 |          5.38  |          0 |              nan |
| Paper 1 GWO (ground truth, offline)   |       3    |             7.73 |          6.41 |               1.71  |           1.43 |          1.26  |          0 |              nan |
| Static (llm)                          |       3.28 |             9.7  |          5.98 |               1.97  |           1.26 |         10.1   |          0 |              nan |
| Library (llm)                         |       6.84 |             7.17 |         24.2  |               6.8   |           1.23 |          0.257 |          3 |              nan |
| Library, true condition (llm)         |       6.86 |             7.27 |         24.2  |               6.81  |           1.23 |          0.284 |          2 |              nan |
| Library, no plausibility filter (llm) |      19.1  |            17    |         69.1  |              19.3   |           1.38 |         14.1   |          3 |              nan |
| Library + online update (llm)         |       6.82 |             6.94 |         24.1  |               6.8   |           1.24 |          0.197 |        nan |                2 |

## Training part (initialization period)

| method   |   train_rmse_all |   train_rmse_moderate_5m |   train_rmse_moderate_5m_first10s |   train_rmse_outside |
|:---------|-----------------:|-------------------------:|----------------------------------:|---------------------:|
| THETA0   |             1.21 |                     2.81 |                              2.36 |                0.786 |
