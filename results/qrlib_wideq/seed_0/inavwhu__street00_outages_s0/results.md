# inavwhu/street00_outages_s0

## Test part

Horizontal RMSE in m.

| method                                |   rmse_all |   rmse_heavy_15m |   rmse_outage |   rmse_recovery_30s |   rmse_outside |   nis_over_dof |   switches |   online_entries |
|:--------------------------------------|-----------:|-----------------:|--------------:|--------------------:|---------------:|---------------:|-----------:|-----------------:|
| Raw GPS                               |       4.83 |            16.9  |        nan    |               0.866 |           1.2  |         nan    |        nan |              nan |
| Baseline THETA0                       |       3.68 |            10.9  |          6.92 |               1.65  |           1.32 |           5.38 |          0 |              nan |
| Paper 1 GWO (ground truth, offline)   |       3    |             7.73 |          6.41 |               1.71  |           1.43 |           1.26 |          0 |              nan |
| Static (llm)                          |       3.26 |            10.7  |          3.31 |               1.27  |           1.3  |           5.06 |          0 |              nan |
| Library (llm)                         |       7.36 |            10.9  |         24.7  |               7.54  |           1.29 |           4.89 |          2 |              nan |
| Library, true condition (llm)         |       7    |            10.9  |         23.3  |               7.16  |           1.28 |           5.49 |          2 |              nan |
| Library, no plausibility filter (llm) |      83.5  |            22.5  |        313    |              78.4   |           1.36 |          29.6  |          2 |              nan |
| Library + online update (llm)         |      11    |            34.9  |         19.2  |               6.1   |           2.73 |           2    |        nan |                2 |

## Training part (initialization period)

| method                    |   train_rmse_all |   train_rmse_moderate_5m |   train_rmse_moderate_5m_first10s |   train_rmse_outside |   tunings |
|:--------------------------|-----------------:|-------------------------:|----------------------------------:|---------------------:|----------:|
| THETA0                    |             1.21 |                     2.81 |                              2.36 |                0.786 |       nan |
| Initialization mode (llm) |             1.5  |                     3.87 |                              3.08 |                0.762 |         8 |
