# eth_outages_s0

## Test part

Horizontal RMSE in m.

| method                                |   rmse_all |   rmse_heavy_15m |   rmse_outage |   rmse_recovery_30s |   rmse_outside |   nis_over_dof |   switches |   online_entries |
|:--------------------------------------|-----------:|-----------------:|--------------:|--------------------:|---------------:|---------------:|-----------:|-----------------:|
| Raw GPS                               |       5.78 |            15.2  |    nan        |                2.23 |           3.93 |         nan    |        nan |              nan |
| Baseline THETA0                       |     827    |             4.58 |      3.49e+03 |                2.4  |           4.12 |           0.54 |          0 |              nan |
| Paper 1 GWO (ground truth, offline)   |     497    |             5.72 |      2.1e+03  |                2.32 |           4.04 |           1.15 |          0 |              nan |
| Static (llm)                          |     471    |             5.77 |      1.99e+03 |                2.34 |           4.03 |           1.77 |          0 |              nan |
| Library (llm)                         |     494    |             4.43 |      2.09e+03 |                2.22 |           3.93 |           1.3  |          3 |              nan |
| Library, true condition (llm)         |     487    |             4.43 |      2.06e+03 |                2.22 |           3.93 |           1.31 |          2 |              nan |
| Library, no plausibility filter (llm) |     540    |             5.92 |      2.28e+03 |                2.22 |           3.93 |          10.6  |          4 |              nan |
| Library + online update (llm)         |     506    |             3.41 |      2.14e+03 |                2.22 |           3.93 |           1.19 |        nan |                2 |

## Training part (initialization period)

| method   |   train_rmse_all |   train_rmse_moderate_5m |   train_rmse_moderate_5m_first10s |   train_rmse_outside |
|:---------|-----------------:|-------------------------:|----------------------------------:|---------------------:|
| THETA0   |              3.6 |                     3.11 |                              2.83 |                 3.65 |
