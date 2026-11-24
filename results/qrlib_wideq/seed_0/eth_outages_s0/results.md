# eth_outages_s0

## Test part

Horizontal RMSE in m.

| method                                |   rmse_all |   rmse_heavy_15m |   rmse_outage |   rmse_recovery_30s |   rmse_outside |   nis_over_dof |   switches |   online_entries |
|:--------------------------------------|-----------:|-----------------:|--------------:|--------------------:|---------------:|---------------:|-----------:|-----------------:|
| Raw GPS                               |       5.78 |            15.2  |    nan        |                2.23 |           3.93 |        nan     |        nan |              nan |
| Baseline THETA0                       |     827    |             4.58 |      3.49e+03 |                2.4  |           4.12 |          0.54  |          0 |              nan |
| Paper 1 GWO (ground truth, offline)   |     497    |             5.72 |      2.1e+03  |                2.32 |           4.04 |          1.15  |          0 |              nan |
| Static (llm)                          |     407    |             6.04 |      1.72e+03 |                2.31 |           4.02 |          1.27  |          0 |              nan |
| Library (llm)                         |     465    |             4.52 |      1.97e+03 |                2.22 |           3.96 |          0.803 |          3 |              nan |
| Library, true condition (llm)         |     454    |             4.5  |      1.92e+03 |                2.22 |           3.96 |          0.813 |          2 |              nan |
| Library, no plausibility filter (llm) |     533    |             5.09 |      2.25e+03 |                2.23 |           3.97 |          1.35  |          4 |              nan |
| Library + online update (llm)         |     457    |             4.92 |      1.93e+03 |                2.23 |           3.96 |          1.14  |        nan |                2 |

## Training part (initialization period)

| method                    |   train_rmse_all |   train_rmse_moderate_5m |   train_rmse_moderate_5m_first10s |   train_rmse_outside |   tunings |
|:--------------------------|-----------------:|-------------------------:|----------------------------------:|---------------------:|----------:|
| THETA0                    |             3.6  |                     3.11 |                              2.83 |                 3.65 |       nan |
| Initialization mode (llm) |             3.54 |                     3.29 |                              3.59 |                 3.57 |        10 |
