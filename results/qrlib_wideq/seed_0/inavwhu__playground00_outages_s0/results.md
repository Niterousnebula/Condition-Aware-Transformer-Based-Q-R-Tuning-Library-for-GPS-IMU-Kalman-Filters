# inavwhu/playground00_outages_s0

## Test part

Horizontal RMSE in m.

| method                                |   rmse_all |   rmse_heavy_15m |   rmse_outage |   rmse_recovery_30s |   rmse_outside |   nis_over_dof |   switches |   online_entries |
|:--------------------------------------|-----------:|-----------------:|--------------:|--------------------:|---------------:|---------------:|-----------:|-----------------:|
| Raw GPS                               |       4.74 |            17.2  |        nan    |                1.49 |           1.32 |        nan     |        nan |              nan |
| Baseline THETA0                       |      15.6  |            11.8  |         56    |               24.4  |           1.57 |          7.48  |          0 |              nan |
| Paper 1 GWO (ground truth, offline)   |       3.34 |             7.76 |          8.27 |                4.18 |           1.57 |          1.32  |          0 |              nan |
| Static (llm)                          |      13.9  |            11.8  |         49.3  |               23    |           1.53 |          6.67  |          0 |              nan |
| Library (llm)                         |       3.19 |             8.4  |          7.06 |                3.46 |           1.48 |          0.224 |          3 |              nan |
| Library, true condition (llm)         |       3.13 |             8.37 |          6.63 |                3.29 |           1.52 |          0.239 |          2 |              nan |
| Library, no plausibility filter (llm) |      48.7  |            26.5  |        176    |               80.9  |           2.57 |         15.4   |          3 |              nan |
| Library + online update (llm)         |       3.18 |             8.39 |          7.23 |                3.53 |           1.4  |          0.196 |        nan |                2 |

## Training part (initialization period)

| method                    |   train_rmse_all |   train_rmse_moderate_5m |   train_rmse_moderate_5m_first10s |   train_rmse_outside |   tunings |
|:--------------------------|-----------------:|-------------------------:|----------------------------------:|---------------------:|----------:|
| THETA0                    |             1.22 |                     2.81 |                              2.35 |                0.796 |       nan |
| Initialization mode (llm) |             1.52 |                     3.88 |                              3.82 |                0.79  |         8 |
