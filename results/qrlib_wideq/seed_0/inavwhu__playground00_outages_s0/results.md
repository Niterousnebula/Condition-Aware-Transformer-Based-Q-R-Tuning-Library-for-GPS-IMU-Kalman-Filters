# inavwhu/playground00_outages_s0

## Test part

Horizontal RMSE in m.

| method                                |   rmse_all |   rmse_heavy_15m |   rmse_outage |   rmse_recovery_30s |   rmse_outside |   nis_over_dof |   switches |   online_entries |
|:--------------------------------------|-----------:|-----------------:|--------------:|--------------------:|---------------:|---------------:|-----------:|-----------------:|
| Raw GPS                               |       4.74 |            17.2  |        nan    |                1.49 |           1.32 |         nan    |        nan |              nan |
| Baseline THETA0                       |      15.6  |            11.8  |         56    |               24.4  |           1.57 |           7.48 |          0 |              nan |
| Paper 1 GWO (ground truth, offline)   |       3.34 |             7.76 |          8.27 |                4.18 |           1.57 |           1.32 |          0 |              nan |
| Static (llm)                          |       8.1  |            11.6  |         27.3  |               11.7  |           1.58 |           4.91 |          0 |              nan |
| Library (llm)                         |       3.06 |             9.73 |          4.06 |                2.29 |           1.54 |           2.46 |          3 |              nan |
| Library, true condition (llm)         |       3.28 |             9.8  |          5.27 |                2.75 |           1.7  |           2.59 |          2 |              nan |
| Library, no plausibility filter (llm) |      47.8  |            14.5  |        174    |               79.9  |           1.56 |          17.5  |          3 |              nan |
| Library + online update (llm)         |       3.84 |            12    |          7.23 |                3.55 |           1.38 |           1.1  |        nan |                2 |

## Training part (initialization period)

| method                    |   train_rmse_all |   train_rmse_moderate_5m |   train_rmse_moderate_5m_first10s |   train_rmse_outside |   tunings |
|:--------------------------|-----------------:|-------------------------:|----------------------------------:|---------------------:|----------:|
| THETA0                    |             1.22 |                     2.81 |                              2.35 |                0.796 |       nan |
| Initialization mode (llm) |             1.44 |                     3.63 |                              3.4  |                0.785 |         8 |
