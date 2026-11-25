# home/20260927_115918_outages_s0

## Test part

Horizontal RMSE in m.

| method                                |   rmse_all |   rmse_heavy_15m |   rmse_outage |   rmse_recovery_30s |   rmse_outside |   nis_over_dof |   switches |   online_entries |
|:--------------------------------------|-----------:|-----------------:|--------------:|--------------------:|---------------:|---------------:|-----------:|-----------------:|
| Raw GPS                               |       9.33 |             18   |         nan   |                3.73 |           6.53 |         nan    |        nan |              nan |
| Baseline THETA0                       |      54.5  |             18.9 |         135   |               59.8  |           7.06 |           1.64 |          0 |              nan |
| Static (llm)                          |      43.6  |             19.3 |         107   |               46.9  |           6.96 |           4.72 |          0 |              nan |
| Library (llm)                         |      24.7  |             17.5 |          58.3 |               26.2  |           6.84 |           1.35 |          8 |              nan |
| Library, true condition (llm)         |      24.8  |             16.1 |          58.6 |               26.3  |           7.19 |           1.45 |          2 |              nan |
| Library, no plausibility filter (llm) |     174    |             43.4 |         439   |              184    |           8.5  |          30.3  |          6 |              nan |
| Library + online update (llm)         |      26.3  |             18.2 |          62.3 |               28    |           7.07 |           1.24 |        nan |                2 |

## Training part (initialization period)

| method                    |   train_rmse_all |   train_rmse_moderate_5m |   train_rmse_moderate_5m_first10s |   train_rmse_outside |   tunings |
|:--------------------------|-----------------:|-------------------------:|----------------------------------:|---------------------:|----------:|
| THETA0                    |             9.59 |                     9.86 |                              8.8  |                 9.51 |       nan |
| Initialization mode (llm) |            13.4  |                    10.2  |                              7.68 |                14.2  |         8 |
