# inavwhu/street00_outages_s0

## Test part

Horizontal RMSE in m.

| method                                |   rmse_all |   rmse_heavy_15m |   rmse_outage |   rmse_recovery_30s |   rmse_outside |   nis_over_dof |   switches |   online_entries |
|:--------------------------------------|-----------:|-----------------:|--------------:|--------------------:|---------------:|---------------:|-----------:|-----------------:|
| Raw GPS                               |       4.83 |            16.9  |        nan    |               0.866 |           1.2  |        nan     |        nan |              nan |
| Baseline THETA0                       |       3.68 |            10.9  |          6.92 |               1.65  |           1.32 |          5.38  |          0 |              nan |
| Paper 1 GWO (ground truth, offline)   |       3    |             7.73 |          6.41 |               1.71  |           1.43 |          1.26  |          0 |              nan |
| Static (llm)                          |       3.1  |             9.8  |          4.11 |               1.78  |           1.27 |          2.06  |          0 |              nan |
| Library (llm)                         |       7.11 |             7.31 |         25.1  |               7.45  |           1.23 |          0.326 |          3 |              nan |
| Library, true condition (llm)         |       7.11 |             7.38 |         25.1  |               7.44  |           1.23 |          0.354 |          2 |              nan |
| Library, no plausibility filter (llm) |      37.7  |            34.8  |        136    |              37.5   |           1.94 |         39.7   |          3 |              nan |
| Static (gwo)                          |       3.49 |             8.77 |          8.45 |               2.84  |           1.28 |          3.32  |          0 |              nan |
| Library (gwo)                         |       6.91 |             6.75 |         24.6  |               6.87  |           1.24 |          0.322 |          3 |              nan |
| Library, true condition (gwo)         |       6.92 |             6.81 |         24.6  |               6.87  |           1.22 |          0.35  |          2 |              nan |
| Library, no plausibility filter (gwo) |      61.8  |            40.3  |        227    |              63.1   |           1.58 |         48.9   |          3 |              nan |
| Library + online update (llm)         |       7.08 |             7.08 |         25.1  |               7.44  |           1.24 |          0.262 |        nan |                2 |
| Library + online update (gwo)         |       6.9  |             6.84 |         24.5  |               6.85  |           1.25 |          0.698 |        nan |                2 |

## Training part (initialization period)

| method                    |   train_rmse_all |   train_rmse_moderate_5m |   train_rmse_moderate_5m_first10s |   train_rmse_outside |   tunings |
|:--------------------------|-----------------:|-------------------------:|----------------------------------:|---------------------:|----------:|
| THETA0                    |             1.21 |                     2.81 |                              2.36 |                0.786 |       nan |
| Initialization mode (llm) |             1.76 |                     4.73 |                              3.33 |                0.76  |         8 |
| Initialization mode (gwo) |             1.75 |                     4.68 |                              3.43 |                0.761 |         8 |
