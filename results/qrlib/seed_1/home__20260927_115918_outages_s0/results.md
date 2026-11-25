# home/20260927_115918_outages_s0

## Test part

Horizontal RMSE in m.

| method                                |   rmse_all |   rmse_heavy_15m |   rmse_outage |   rmse_recovery_30s |   rmse_outside |   nis_over_dof |   switches |   online_entries |
|:--------------------------------------|-----------:|-----------------:|--------------:|--------------------:|---------------:|---------------:|-----------:|-----------------:|
| Raw GPS                               |       9.33 |             18   |    nan        |                3.73 |           6.53 |        nan     |        nan |              nan |
| Baseline THETA0                       |      54.5  |             18.9 |    135        |               59.8  |           7.06 |          1.64  |          0 |              nan |
| Static (llm)                          |     178    |             21.7 |    452        |              184    |           6.88 |         14.8   |          0 |              nan |
| Library (llm)                         |      28.2  |             19.8 |     66.9      |               29.2  |           7.23 |          1.01  |          8 |              nan |
| Library, true condition (llm)         |      30.3  |             17.1 |     73.2      |               32.4  |           7.18 |          0.965 |          2 |              nan |
| Library, no plausibility filter (llm) |      27    |             18.5 |     63.8      |               27.6  |           8.14 |          3.98  |          6 |              nan |
| Static (gwo)                          |     194    |             21.8 |    490        |              199    |           6.72 |        119     |          0 |              nan |
| Library (gwo)                         |      25.2  |             18.4 |     58.4      |               30.4  |           6.9  |          2.18  |          8 |              nan |
| Library, true condition (gwo)         |      20.8  |             16.3 |     48.1      |               21.4  |           6.86 |          1.86  |          2 |              nan |
| Library, no plausibility filter (gwo) |     506    |             54.8 |      1.27e+03 |              585    |          13.5  |        121     |          6 |              nan |
| Library + online update (llm)         |      30.1  |             20.7 |     71.1      |               32.1  |           8.35 |          0.745 |        nan |                2 |
| Library + online update (gwo)         |      23.5  |             19   |     53.4      |               28.5  |           7.16 |          1.82  |        nan |                2 |

## Training part (initialization period)

| method                    |   train_rmse_all |   train_rmse_moderate_5m |   train_rmse_moderate_5m_first10s |   train_rmse_outside |   tunings |
|:--------------------------|-----------------:|-------------------------:|----------------------------------:|---------------------:|----------:|
| THETA0                    |             9.59 |                     9.86 |                              8.8  |                 9.51 |       nan |
| Initialization mode (llm) |            18.8  |                    15.9  |                             15.8  |                19.5  |         8 |
| Initialization mode (gwo) |            11.5  |                     9.94 |                              4.56 |                11.9  |         8 |
