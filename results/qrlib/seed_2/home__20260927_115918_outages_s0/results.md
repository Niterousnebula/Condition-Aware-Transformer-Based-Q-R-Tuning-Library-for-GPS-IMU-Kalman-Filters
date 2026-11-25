# home/20260927_115918_outages_s0

## Test part

Horizontal RMSE in m.

| method                                |   rmse_all |   rmse_heavy_15m |   rmse_outage |   rmse_recovery_30s |   rmse_outside |   nis_over_dof |   switches |   online_entries |
|:--------------------------------------|-----------:|-----------------:|--------------:|--------------------:|---------------:|---------------:|-----------:|-----------------:|
| Raw GPS                               |       9.33 |             18   |         nan   |                3.73 |           6.53 |         nan    |        nan |              nan |
| Baseline THETA0                       |      54.5  |             18.9 |         135   |               59.8  |           7.06 |           1.64 |          0 |              nan |
| Static (llm)                          |      48.4  |             23.6 |         119   |               51.4  |           6.99 |         118    |          0 |              nan |
| Library (llm)                         |      24.1  |             16.5 |          56.8 |               25.5  |           6.79 |           1.63 |          8 |              nan |
| Library, true condition (llm)         |      24.2  |             15.2 |          57.4 |               25.7  |           6.9  |           1.67 |          2 |              nan |
| Library, no plausibility filter (llm) |      26.3  |             31.7 |          57.2 |               25.7  |           6.86 |          30.7  |          6 |              nan |
| Static (gwo)                          |     147    |             24.5 |         371   |              152    |           7.09 |          31.8  |          0 |              nan |
| Library (gwo)                         |      29.7  |             17.5 |          71.5 |               32.2  |           7.05 |           1.82 |          8 |              nan |
| Library, true condition (gwo)         |      32.8  |             14.7 |          80.2 |               36.1  |           6.85 |           1.67 |          2 |              nan |
| Library, no plausibility filter (gwo) |      25.3  |             24.4 |          57   |               25.6  |           7.85 |          19.1  |          6 |              nan |
| Library + online update (llm)         |      25.4  |             17.8 |          59.5 |               26.8  |           7.92 |           1.52 |        nan |                2 |
| Library + online update (gwo)         |      31.3  |             17.2 |          75.6 |               33.9  |           7    |           1.78 |        nan |                2 |

## Training part (initialization period)

| method                    |   train_rmse_all |   train_rmse_moderate_5m |   train_rmse_moderate_5m_first10s |   train_rmse_outside |   tunings |
|:--------------------------|-----------------:|-------------------------:|----------------------------------:|---------------------:|----------:|
| THETA0                    |             9.59 |                     9.86 |                              8.8  |                 9.51 |       nan |
| Initialization mode (llm) |            13.2  |                    11.1  |                              8.45 |                13.8  |         8 |
| Initialization mode (gwo) |            14.3  |                    13.4  |                             10    |                14.5  |         8 |
