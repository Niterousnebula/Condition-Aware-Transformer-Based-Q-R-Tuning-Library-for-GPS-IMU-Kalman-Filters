# inavwhu/street00_outages_s0

## Test part

Horizontal RMSE in m.

| method                                |   rmse_all |   rmse_heavy_15m |   rmse_outage |   rmse_recovery_30s |   rmse_outside |   nis_over_dof |   switches |   online_entries |
|:--------------------------------------|-----------:|-----------------:|--------------:|--------------------:|---------------:|---------------:|-----------:|-----------------:|
| Raw GPS                               |       4.83 |            16.9  |        nan    |               0.866 |           1.2  |         nan    |        nan |              nan |
| Baseline THETA0                       |       3.68 |            10.9  |          6.92 |               1.65  |           1.32 |           5.38 |          0 |              nan |
| Paper 1 GWO (ground truth, offline)   |       3    |             7.73 |          6.41 |               1.71  |           1.43 |           1.26 |          0 |              nan |
| Static (llm)                          |       3.07 |            10.1  |          3.06 |               1.18  |           1.28 |           3.06 |          0 |              nan |
| Library (llm)                         |      12.2  |            10.8  |         44.3  |              10.7   |           1.3  |           5.38 |          3 |              nan |
| Library, true condition (llm)         |      10.3  |            10.9  |         36.7  |               8.46  |           1.3  |           5.99 |          2 |              nan |
| Library, no plausibility filter (llm) |      25.3  |            46.6  |         82.3  |              19.9   |           1.3  |         422    |          3 |              nan |
| Library + online update (llm)         |      10.9  |            11.6  |         39.1  |               9.16  |           1.25 |           3.44 |        nan |                2 |

## Training part (initialization period)

| method                    |   train_rmse_all |   train_rmse_moderate_5m |   train_rmse_moderate_5m_first10s |   train_rmse_outside |   tunings |
|:--------------------------|-----------------:|-------------------------:|----------------------------------:|---------------------:|----------:|
| THETA0                    |             1.21 |                     2.81 |                              2.36 |                0.786 |       nan |
| Initialization mode (llm) |             1.85 |                     5    |                              6.63 |                0.759 |         8 |
