# inavwhu/playground00_outages_s0

## Test part

Horizontal RMSE in m.

| method                                |   rmse_all |   rmse_heavy_15m |   rmse_outage |   rmse_recovery_30s |   rmse_outside |   nis_over_dof |   switches |   online_entries |
|:--------------------------------------|-----------:|-----------------:|--------------:|--------------------:|---------------:|---------------:|-----------:|-----------------:|
| Raw GPS                               |       4.74 |            17.2  |        nan    |                1.49 |           1.32 |        nan     |        nan |              nan |
| Baseline THETA0                       |      15.6  |            11.8  |         56    |               24.4  |           1.57 |          7.48  |          0 |              nan |
| Paper 1 GWO (ground truth, offline)   |       3.34 |             7.76 |          8.27 |                4.18 |           1.57 |          1.32  |          0 |              nan |
| Static (llm)                          |      10.1  |            10.4  |         35.6  |               15.7  |           1.57 |          4.71  |          0 |              nan |
| Library (llm)                         |       3.3  |             8.78 |          7.31 |                4    |           1.46 |          0.241 |          3 |              nan |
| Library, true condition (llm)         |       3.3  |             8.78 |          7.27 |                3.97 |           1.47 |          0.257 |          2 |              nan |
| Library, no plausibility filter (llm) |      27.2  |            62.5  |         81.4  |               34.3  |           1.64 |         32.6   |          3 |              nan |
| Static (gwo)                          |       7.43 |             8.97 |         25.4  |               11.6  |           1.52 |          6.49  |          0 |              nan |
| Library (gwo)                         |       2.91 |             8.78 |          4.74 |                2.47 |           1.45 |          0.222 |          3 |              nan |
| Library, true condition (gwo)         |       2.9  |             8.74 |          4.63 |                2.44 |           1.47 |          0.237 |          2 |              nan |
| Library, no plausibility filter (gwo) |      10.2  |            33.1  |         19.3  |                8.88 |           2.63 |         13.2   |          3 |              nan |
| Library + online update (llm)         |       3.27 |             8.77 |          7.27 |                3.98 |           1.39 |          0.215 |        nan |                2 |
| Library + online update (gwo)         |       2.83 |             8.68 |          4.63 |                2.45 |           1.34 |          0.517 |        nan |                2 |

## Training part (initialization period)

| method                    |   train_rmse_all |   train_rmse_moderate_5m |   train_rmse_moderate_5m_first10s |   train_rmse_outside |   tunings |
|:--------------------------|-----------------:|-------------------------:|----------------------------------:|---------------------:|----------:|
| THETA0                    |             1.22 |                     2.81 |                              2.35 |                0.796 |       nan |
| Initialization mode (llm) |             1.7  |                     4.46 |                              4.92 |                0.801 |         8 |
| Initialization mode (gwo) |             1.53 |                     3.91 |                              3.89 |                0.792 |         8 |
