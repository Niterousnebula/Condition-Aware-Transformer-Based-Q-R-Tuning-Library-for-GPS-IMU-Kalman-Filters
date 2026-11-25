# inavwhu/playground00_outages_s0

## Test part

Horizontal RMSE in m.

| method                                |   rmse_all |   rmse_heavy_15m |   rmse_outage |   rmse_recovery_30s |   rmse_outside |   nis_over_dof |   switches |   online_entries |
|:--------------------------------------|-----------:|-----------------:|--------------:|--------------------:|---------------:|---------------:|-----------:|-----------------:|
| Raw GPS                               |       4.74 |            17.2  |        nan    |                1.49 |           1.32 |        nan     |        nan |              nan |
| Baseline THETA0                       |      15.6  |            11.8  |         56    |               24.4  |           1.57 |          7.48  |          0 |              nan |
| Paper 1 GWO (ground truth, offline)   |       3.34 |             7.76 |          8.27 |                4.18 |           1.57 |          1.32  |          0 |              nan |
| Static (llm)                          |       8.03 |            10.1  |         27.4  |               12.1  |           1.56 |          8.3   |          0 |              nan |
| Library (llm)                         |       3.5  |             8.51 |          8.76 |                4.49 |           1.43 |          0.243 |          3 |              nan |
| Library, true condition (llm)         |       3.51 |             8.47 |          8.83 |                4.52 |           1.44 |          0.259 |          2 |              nan |
| Library, no plausibility filter (llm) |      22    |            77.6  |         34.4  |               16.2  |           2.38 |         37.2   |          3 |              nan |
| Library + online update (llm)         |       3.49 |             8.52 |          8.77 |                4.5  |           1.38 |          0.256 |        nan |                2 |

## Training part (initialization period)

| method   |   train_rmse_all |   train_rmse_moderate_5m |   train_rmse_moderate_5m_first10s |   train_rmse_outside |
|:---------|-----------------:|-------------------------:|----------------------------------:|---------------------:|
| THETA0   |             1.22 |                     2.81 |                              2.35 |                0.796 |
