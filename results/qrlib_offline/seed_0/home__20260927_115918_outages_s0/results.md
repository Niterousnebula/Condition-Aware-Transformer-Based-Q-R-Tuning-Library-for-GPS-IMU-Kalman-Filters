# home/20260927_115918_outages_s0

## Test part

Horizontal RMSE in m.

| method                                |   rmse_all |   rmse_heavy_15m |   rmse_outage |   rmse_recovery_30s |   rmse_outside |   nis_over_dof |   switches |   online_entries |
|:--------------------------------------|-----------:|-----------------:|--------------:|--------------------:|---------------:|---------------:|-----------:|-----------------:|
| Raw GPS                               |       9.33 |             18   |    nan        |                3.73 |           6.53 |         nan    |        nan |              nan |
| Baseline THETA0                       |      54.5  |             18.9 |    135        |               59.8  |           7.06 |           1.64 |          0 |              nan |
| Static (llm)                          |      45.6  |             23.5 |    112        |               47.5  |           6.99 |          94.3  |          0 |              nan |
| Library (llm)                         |      24.9  |             20   |     57.6      |               27.2  |           6.92 |           1.66 |          8 |              nan |
| Library, true condition (llm)         |      56.1  |             17.2 |    139        |               63.8  |           7.01 |           1.61 |          2 |              nan |
| Library, no plausibility filter (llm) |     425    |             44.8 |      1.07e+03 |              469    |           7.53 |          61.1  |          6 |              nan |
| Library + online update (llm)         |      23.7  |             20.5 |     54.5      |               23.8  |           7.3  |           1.48 |        nan |                2 |

## Training part (initialization period)

| method   |   train_rmse_all |   train_rmse_moderate_5m |   train_rmse_moderate_5m_first10s |   train_rmse_outside |
|:---------|-----------------:|-------------------------:|----------------------------------:|---------------------:|
| THETA0   |             9.59 |                     9.86 |                               8.8 |                 9.51 |
