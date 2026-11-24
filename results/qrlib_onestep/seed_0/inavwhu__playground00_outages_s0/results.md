# inavwhu/playground00_outages_s0

## Test part

Horizontal RMSE in m.

| method                                |   rmse_all |   rmse_heavy_15m |   rmse_outage |   rmse_recovery_30s |   rmse_outside |   nis_over_dof |   switches |   online_entries |
|:--------------------------------------|-----------:|-----------------:|--------------:|--------------------:|---------------:|---------------:|-----------:|-----------------:|
| Raw GPS                               |       4.74 |            17.2  |        nan    |                1.49 |           1.32 |         nan    |        nan |              nan |
| Baseline THETA0                       |      15.6  |            11.8  |         56    |               24.4  |           1.57 |           7.48 |          0 |              nan |
| Paper 1 GWO (ground truth, offline)   |       3.34 |             7.76 |          8.27 |                4.18 |           1.57 |           1.32 |          0 |              nan |
| Static (llm)                          |      10.9  |            10.5  |         38.5  |               16.9  |           1.57 |           6.26 |          0 |              nan |
| Library (llm)                         |       6.15 |            10.3  |         19.8  |                8.84 |           1.54 |           6.87 |          3 |              nan |
| Library, true condition (llm)         |       6.18 |            10.6  |         19.5  |                8.75 |           1.76 |           7.62 |          2 |              nan |
| Library, no plausibility filter (llm) |      27.5  |            20.4  |         99.4  |               42.3  |           1.63 |         879    |          3 |              nan |
| Library + online update (llm)         |       6.27 |            10.3  |         20.2  |                9.03 |           1.61 |           3.51 |        nan |                2 |

## Training part (initialization period)

| method                    |   train_rmse_all |   train_rmse_moderate_5m |   train_rmse_moderate_5m_first10s |   train_rmse_outside |   tunings |
|:--------------------------|-----------------:|-------------------------:|----------------------------------:|---------------------:|----------:|
| THETA0                    |             1.22 |                     2.81 |                              2.35 |                0.796 |       nan |
| Initialization mode (llm) |             1.74 |                     4.6  |                              7.25 |                0.791 |         8 |
