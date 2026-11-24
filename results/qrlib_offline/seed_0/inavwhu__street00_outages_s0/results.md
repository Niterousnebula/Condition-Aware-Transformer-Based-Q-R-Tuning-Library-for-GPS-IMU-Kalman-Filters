# inavwhu/street00_outages_s0

## Test part

Horizontal RMSE in m.

| method                                |   rmse_all |   rmse_heavy_15m |   rmse_outage |   rmse_recovery_30s |   rmse_outside |   nis_over_dof |   switches |   online_entries |
|:--------------------------------------|-----------:|-----------------:|--------------:|--------------------:|---------------:|---------------:|-----------:|-----------------:|
| Raw GPS                               |       4.83 |            16.9  |        nan    |               0.866 |           1.2  |        nan     |        nan |              nan |
| Baseline THETA0                       |       3.68 |            10.9  |          6.92 |               1.65  |           1.32 |          5.38  |          0 |              nan |
| Paper 1 GWO (ground truth, offline)   |       3    |             7.73 |          6.41 |               1.71  |           1.43 |          1.26  |          0 |              nan |
| Static (llm)                          |       3.22 |            10.5  |          3.65 |               1.14  |           1.29 |          4.02  |          0 |              nan |
| Library (llm)                         |       7.57 |             9.03 |         26.5  |               7.36  |           1.25 |          1.84  |          2 |              nan |
| Library, true condition (llm)         |       7.58 |             9.23 |         26.4  |               7.37  |           1.24 |          2.05  |          2 |              nan |
| Library, no plausibility filter (llm) |      33    |            14.3  |        122    |              36.1   |           1.3  |         26.9   |          2 |              nan |
| Library + online update (llm)         |      10.6  |            28.4  |         26.1  |               7.29  |           2.58 |          0.775 |        nan |                2 |

## Training part (initialization period)

| method   |   train_rmse_all |   train_rmse_moderate_5m |   train_rmse_moderate_5m_first10s |   train_rmse_outside |
|:---------|-----------------:|-------------------------:|----------------------------------:|---------------------:|
| THETA0   |             1.21 |                     2.81 |                              2.36 |                0.786 |
