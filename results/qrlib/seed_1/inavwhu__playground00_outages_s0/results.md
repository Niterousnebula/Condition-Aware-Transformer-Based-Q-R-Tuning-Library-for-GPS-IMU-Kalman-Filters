# inavwhu/playground00_outages_s0

## Test part

Horizontal RMSE in m.

| method                                |   rmse_all |   rmse_heavy_15m |   rmse_outage |   rmse_recovery_30s |   rmse_outside |   nis_over_dof |   switches |   online_entries |
|:--------------------------------------|-----------:|-----------------:|--------------:|--------------------:|---------------:|---------------:|-----------:|-----------------:|
| Raw GPS                               |       4.74 |            17.2  |        nan    |                1.49 |           1.32 |        nan     |        nan |              nan |
| Baseline THETA0                       |      15.6  |            11.8  |         56    |               24.4  |           1.57 |          7.48  |          0 |              nan |
| Paper 1 GWO (ground truth, offline)   |       3.34 |             7.76 |          8.27 |                4.18 |           1.57 |          1.32  |          0 |              nan |
| Static (llm)                          |      11.4  |            11.2  |         40.1  |               17.7  |           1.57 |          3.44  |          0 |              nan |
| Library (llm)                         |       2.64 |             8.8  |          1.45 |                1.6  |           1.45 |          0.238 |          3 |              nan |
| Library, true condition (llm)         |       2.65 |             8.79 |          1.49 |                1.61 |           1.46 |          0.254 |          2 |              nan |
| Library, no plausibility filter (llm) |      50.3  |            40.1  |        180    |               80.8  |           2.22 |         23.6   |          3 |              nan |
| Static (gwo)                          |       7.45 |             8.93 |         25.5  |               11.6  |           1.52 |          4.19  |          0 |              nan |
| Library (gwo)                         |       3.33 |             8.74 |          7.54 |                3.99 |           1.44 |          0.226 |          3 |              nan |
| Library, true condition (gwo)         |       3.32 |             8.7  |          7.49 |                3.97 |           1.47 |          0.242 |          2 |              nan |
| Library, no plausibility filter (gwo) |      15.1  |            53.5  |         22.8  |                9.72 |           2.11 |         20.4   |          3 |              nan |
| Library + online update (llm)         |       2.62 |             8.81 |          1.35 |                1.58 |           1.4  |          0.213 |        nan |                2 |
| Library + online update (gwo)         |       3.29 |             8.72 |          7.5  |                3.98 |           1.37 |          0.219 |        nan |                2 |

## Training part (initialization period)

| method                    |   train_rmse_all |   train_rmse_moderate_5m |   train_rmse_moderate_5m_first10s |   train_rmse_outside |   tunings |
|:--------------------------|-----------------:|-------------------------:|----------------------------------:|---------------------:|----------:|
| THETA0                    |             1.22 |                     2.81 |                              2.35 |                0.796 |       nan |
| Initialization mode (llm) |             1.61 |                     4.18 |                              4.51 |                0.791 |         8 |
| Initialization mode (gwo) |             1.56 |                     4.03 |                              4.43 |                0.788 |         8 |
