# inavwhu/playground00_outages_s0

## Test part

Horizontal RMSE in m.

| method                                |   rmse_all |   rmse_heavy_15m |   rmse_outage |   rmse_recovery_30s |   rmse_outside |   nis_over_dof |   switches |   online_entries |
|:--------------------------------------|-----------:|-----------------:|--------------:|--------------------:|---------------:|---------------:|-----------:|-----------------:|
| Raw GPS                               |       4.74 |            17.2  |        nan    |                1.49 |           1.32 |        nan     |        nan |              nan |
| Baseline THETA0                       |      15.6  |            11.8  |         56    |               24.4  |           1.57 |          7.48  |          0 |              nan |
| Paper 1 GWO (ground truth, offline)   |       3.34 |             7.76 |          8.27 |                4.18 |           1.57 |          1.32  |          0 |              nan |
| Static (llm)                          |       5.03 |             9.44 |         15.4  |                7.05 |           1.52 |          9.21  |          0 |              nan |
| Library (llm)                         |       3.31 |             8.51 |          7.82 |                3.79 |           1.41 |          0.231 |          3 |              nan |
| Library, true condition (llm)         |       3.26 |             8.51 |          7.52 |                3.66 |           1.43 |          0.247 |          2 |              nan |
| Library, no plausibility filter (llm) |      15.6  |            40.4  |         42.3  |               19.3  |           2    |         18.5   |          3 |              nan |
| Static (gwo)                          |       7.38 |             9.01 |         25.2  |               11.4  |           1.52 |          4.5   |          0 |              nan |
| Library (gwo)                         |       4.39 |             8.6  |         13    |                6.45 |           1.41 |          0.239 |          3 |              nan |
| Library, true condition (gwo)         |       4.38 |             8.57 |         13    |                6.43 |           1.42 |          0.254 |          2 |              nan |
| Library, no plausibility filter (gwo) |      20.2  |            70.2  |         33.1  |               15.4  |           2.94 |         33.4   |          3 |              nan |
| Library + online update (llm)         |       3.29 |             8.67 |          7.44 |                3.63 |           1.45 |          0.208 |        nan |                2 |
| Library + online update (gwo)         |       4.38 |             8.59 |         13    |                6.44 |           1.38 |          0.223 |        nan |                2 |

## Training part (initialization period)

| method                    |   train_rmse_all |   train_rmse_moderate_5m |   train_rmse_moderate_5m_first10s |   train_rmse_outside |   tunings |
|:--------------------------|-----------------:|-------------------------:|----------------------------------:|---------------------:|----------:|
| THETA0                    |             1.22 |                     2.81 |                              2.35 |                0.796 |       nan |
| Initialization mode (llm) |             1.56 |                     4    |                              3.92 |                0.796 |         8 |
| Initialization mode (gwo) |             1.61 |                     4.18 |                              4.96 |                0.789 |         8 |
