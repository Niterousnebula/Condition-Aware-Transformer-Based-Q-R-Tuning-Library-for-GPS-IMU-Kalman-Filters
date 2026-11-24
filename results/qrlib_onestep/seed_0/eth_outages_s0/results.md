# eth_outages_s0

## Test part

Horizontal RMSE in m.

| method                                |   rmse_all |   rmse_heavy_15m |   rmse_outage |   rmse_recovery_30s |   rmse_outside |   nis_over_dof |   switches |   online_entries |
|:--------------------------------------|-----------:|-----------------:|--------------:|--------------------:|---------------:|---------------:|-----------:|-----------------:|
| Raw GPS                               |   5.78     |            15.2  |    nan        |                2.23 |           3.93 |        nan     |        nan |              nan |
| Baseline THETA0                       | 827        |             4.58 |      3.49e+03 |                2.4  |           4.12 |          0.54  |          0 |              nan |
| Paper 1 GWO (ground truth, offline)   | 497        |             5.72 |      2.1e+03  |                2.32 |           4.04 |          1.15  |          0 |              nan |
| Static (llm)                          | 715        |             5.84 |      3.02e+03 |                2.32 |           4.03 |          2.61  |          0 |              nan |
| Library (llm)                         |   1.18e+03 |             4.62 |      4.98e+03 |                2.21 |           3.92 |          0.481 |          3 |              nan |
| Library, true condition (llm)         |   1.17e+03 |             4.59 |      4.94e+03 |                2.21 |           3.92 |          0.488 |          2 |              nan |
| Library, no plausibility filter (llm) |   1.25e+03 |             6.6  |      5.29e+03 |                2.22 |           3.93 |          4.46  |          4 |              nan |
| Library + online update (llm)         |   1.15e+03 |             3.56 |      4.85e+03 |                2.21 |           3.92 |          0.314 |        nan |                2 |

## Training part (initialization period)

| method                    |   train_rmse_all |   train_rmse_moderate_5m |   train_rmse_moderate_5m_first10s |   train_rmse_outside |   tunings |
|:--------------------------|-----------------:|-------------------------:|----------------------------------:|---------------------:|----------:|
| THETA0                    |             3.6  |                     3.11 |                              2.83 |                 3.65 |       nan |
| Initialization mode (llm) |             3.53 |                     3.3  |                              3.47 |                 3.55 |        10 |
