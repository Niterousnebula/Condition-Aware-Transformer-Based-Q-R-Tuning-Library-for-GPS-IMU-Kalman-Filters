# inavwhu/street00_outages_s0

## Test part

Horizontal RMSE in m.

| method                                |   rmse_all |   rmse_heavy_15m |   rmse_outage |   rmse_recovery_30s |   rmse_outside |   nis_over_dof |   switches |   online_entries |
|:--------------------------------------|-----------:|-----------------:|--------------:|--------------------:|---------------:|---------------:|-----------:|-----------------:|
| Raw GPS                               |       4.83 |            16.9  |        nan    |               0.866 |           1.2  |        nan     |        nan |              nan |
| Baseline THETA0                       |       3.68 |            10.9  |          6.92 |               1.65  |           1.32 |          5.38  |          0 |              nan |
| Paper 1 GWO (ground truth, offline)   |       3    |             7.73 |          6.41 |               1.71  |           1.43 |          1.26  |          0 |              nan |
| Static (llm)                          |       3.07 |            10    |          3.27 |               1.33  |           1.27 |          3.22  |          0 |              nan |
| Library (llm)                         |       7.06 |             6.8  |         25.1  |               7.13  |           1.23 |          0.363 |          3 |              nan |
| Library, true condition (llm)         |       7.06 |             6.87 |         25.1  |               7.12  |           1.23 |          0.391 |          2 |              nan |
| Library, no plausibility filter (llm) |      42    |            44.6  |        151    |              41.7   |           1.43 |         62.1   |          3 |              nan |
| Library + online update (llm)         |       7.06 |             7.22 |         25    |               7.1   |           1.25 |          0.298 |        nan |                2 |

## Training part (initialization period)

| method                    |   train_rmse_all |   train_rmse_moderate_5m |   train_rmse_moderate_5m_first10s |   train_rmse_outside |   tunings |
|:--------------------------|-----------------:|-------------------------:|----------------------------------:|---------------------:|----------:|
| THETA0                    |             1.21 |                     2.81 |                              2.36 |                0.786 |       nan |
| Initialization mode (llm) |             1.83 |                     4.94 |                              3.66 |                0.76  |         8 |
