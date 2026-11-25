# inavwhu/street00_outages_s0

## Test part

Horizontal RMSE in m.

| method                                |   rmse_all |   rmse_heavy_15m |   rmse_outage |   rmse_recovery_30s |   rmse_outside |   nis_over_dof |   switches |   online_entries |
|:--------------------------------------|-----------:|-----------------:|--------------:|--------------------:|---------------:|---------------:|-----------:|-----------------:|
| Raw GPS                               |       4.83 |            16.9  |        nan    |               0.866 |           1.2  |        nan     |        nan |              nan |
| Baseline THETA0                       |       3.68 |            10.9  |          6.92 |               1.65  |           1.32 |          5.38  |          0 |              nan |
| Paper 1 GWO (ground truth, offline)   |       3    |             7.73 |          6.41 |               1.71  |           1.43 |          1.26  |          0 |              nan |
| Static (llm)                          |       3.09 |             9.22 |          5.2  |               2.03  |           1.27 |          3.09  |          0 |              nan |
| Library (llm)                         |      12.5  |             7.39 |         46.2  |              11.6   |           1.23 |          0.807 |          3 |              nan |
| Library, true condition (llm)         |      12.6  |             7.41 |         46.4  |              11.6   |           1.23 |          0.836 |          2 |              nan |
| Library, no plausibility filter (llm) |      87.2  |           295    |        117    |              28.8   |          17.7  |        418     |          3 |              nan |
| Library + online update (llm)         |      12.5  |             7.51 |         46.1  |              11.5   |           1.24 |          0.757 |        nan |                2 |

## Training part (initialization period)

| method                    |   train_rmse_all |   train_rmse_moderate_5m |   train_rmse_moderate_5m_first10s |   train_rmse_outside |   tunings |
|:--------------------------|-----------------:|-------------------------:|----------------------------------:|---------------------:|----------:|
| THETA0                    |             1.21 |                     2.81 |                              2.36 |                0.786 |       nan |
| Initialization mode (llm) |             2.67 |                     7.56 |                              8.76 |                0.768 |         8 |
