# inavwhu/playground00_outages_s0

## Test part

Horizontal RMSE in m.

| method                                |   rmse_all |   rmse_heavy_15m |   rmse_outage |   rmse_recovery_30s |   rmse_outside |   nis_over_dof |   switches |   online_entries |
|:--------------------------------------|-----------:|-----------------:|--------------:|--------------------:|---------------:|---------------:|-----------:|-----------------:|
| Raw GPS                               |       4.74 |            17.2  |        nan    |                1.49 |           1.32 |        nan     |        nan |              nan |
| Baseline THETA0                       |      15.6  |            11.8  |         56    |               24.4  |           1.57 |          7.48  |          0 |              nan |
| Paper 1 GWO (ground truth, offline)   |       3.34 |             7.76 |          8.27 |                4.18 |           1.57 |          1.32  |          0 |              nan |
| Static (llm)                          |      10.3  |            11    |         36    |               15.9  |           1.57 |          3.09  |          0 |              nan |
| Library (llm)                         |       5.68 |             7.65 |         19    |                8.5  |           1.4  |          0.693 |          3 |              nan |
| Library, true condition (llm)         |       5.67 |             7.54 |         19    |                8.48 |           1.42 |          0.716 |          2 |              nan |
| Library, no plausibility filter (llm) |      36.7  |            90.1  |        104    |               44.4  |           6    |        872     |          3 |              nan |
| Library + online update (llm)         |       5.69 |             7.74 |         19.1  |                8.51 |           1.38 |          0.665 |        nan |                2 |

## Training part (initialization period)

| method                    |   train_rmse_all |   train_rmse_moderate_5m |   train_rmse_moderate_5m_first10s |   train_rmse_outside |   tunings |
|:--------------------------|-----------------:|-------------------------:|----------------------------------:|---------------------:|----------:|
| THETA0                    |             1.22 |                     2.81 |                              2.35 |                0.796 |       nan |
| Initialization mode (llm) |             2.81 |                     7.94 |                              9.75 |                0.782 |         8 |
