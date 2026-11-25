# inavwhu/street00_outages_s0

## Test part

Horizontal RMSE in m.

| method                                |   rmse_all |   rmse_heavy_15m |   rmse_outage |   rmse_recovery_30s |   rmse_outside |   nis_over_dof |   switches |   online_entries |
|:--------------------------------------|-----------:|-----------------:|--------------:|--------------------:|---------------:|---------------:|-----------:|-----------------:|
| Raw GPS                               |       4.83 |            16.9  |        nan    |               0.866 |           1.2  |        nan     |        nan |              nan |
| Baseline THETA0                       |       3.68 |            10.9  |          6.92 |               1.65  |           1.32 |          5.38  |          0 |              nan |
| Paper 1 GWO (ground truth, offline)   |       3    |             7.73 |          6.41 |               1.71  |           1.43 |          1.26  |          0 |              nan |
| Static (llm)                          |       3.03 |             9.46 |          4.23 |               1.77  |           1.27 |          3.12  |          0 |              nan |
| Library (llm)                         |       7.14 |             6.93 |         25.4  |               7.29  |           1.23 |          0.321 |          3 |              nan |
| Library, true condition (llm)         |       7.13 |             7.01 |         25.3  |               7.28  |           1.22 |          0.349 |          2 |              nan |
| Library, no plausibility filter (llm) |      70.6  |            39.7  |        261    |              74.9   |           1.33 |         48     |          3 |              nan |
| Static (gwo)                          |       3.51 |             9.34 |          7.98 |               2.55  |           1.28 |          7.57  |          0 |              nan |
| Library (gwo)                         |       8.37 |             6.75 |         30.3  |               8.08  |           1.24 |          0.294 |          3 |              nan |
| Library, true condition (gwo)         |       8.39 |             6.77 |         30.4  |               8.1   |           1.23 |          0.322 |          2 |              nan |
| Library, no plausibility filter (gwo) |      44.5  |            26.3  |        164    |              46.8   |           1.62 |         29.4   |          3 |              nan |
| Library + online update (llm)         |       7.13 |             7.19 |         25.3  |               7.25  |           1.25 |          0.313 |        nan |                2 |
| Library + online update (gwo)         |       8.37 |             6.75 |         30.3  |               8.08  |           1.24 |          0.294 |        nan |                2 |

## Training part (initialization period)

| method                    |   train_rmse_all |   train_rmse_moderate_5m |   train_rmse_moderate_5m_first10s |   train_rmse_outside |   tunings |
|:--------------------------|-----------------:|-------------------------:|----------------------------------:|---------------------:|----------:|
| THETA0                    |             1.21 |                     2.81 |                              2.36 |                0.786 |       nan |
| Initialization mode (llm) |             1.8  |                     4.84 |                              3.64 |                0.76  |         8 |
| Initialization mode (gwo) |             1.63 |                     4.31 |                              2.96 |                0.765 |         8 |
