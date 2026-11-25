# home/20260927_115918_outages_s0

## Test part

Horizontal RMSE in m.

| method                                |   rmse_all |   rmse_heavy_15m |   rmse_outage |   rmse_recovery_30s |   rmse_outside |   nis_over_dof |   switches |   online_entries |
|:--------------------------------------|-----------:|-----------------:|--------------:|--------------------:|---------------:|---------------:|-----------:|-----------------:|
| Raw GPS                               |       9.33 |             18   |         nan   |                3.73 |           6.53 |        nan     |        nan |              nan |
| Baseline THETA0                       |      54.5  |             18.9 |         135   |               59.8  |           7.06 |          1.64  |          0 |              nan |
| Static (llm)                          |     249    |             22.3 |         630   |              257    |           6.84 |         18.9   |          0 |              nan |
| Library (llm)                         |      28.4  |             20.2 |          67.2 |               29.4  |           7.23 |          0.965 |          8 |              nan |
| Library, true condition (llm)         |      28.6  |             17.5 |          68.6 |               29.7  |           7.67 |          0.919 |          2 |              nan |
| Library, no plausibility filter (llm) |      28.5  |             18.4 |          68.1 |               29.3  |           7.5  |          3.1   |          6 |              nan |
| Library + online update (llm)         |      29.7  |             21   |          70.3 |               31.6  |           7.8  |          0.747 |        nan |                2 |

## Training part (initialization period)

| method                    |   train_rmse_all |   train_rmse_moderate_5m |   train_rmse_moderate_5m_first10s |   train_rmse_outside |   tunings |
|:--------------------------|-----------------:|-------------------------:|----------------------------------:|---------------------:|----------:|
| THETA0                    |             9.59 |                     9.86 |                               8.8 |                 9.51 |       nan |
| Initialization mode (llm) |            21.2  |                    16.7  |                              17.4 |                22.4  |         8 |
