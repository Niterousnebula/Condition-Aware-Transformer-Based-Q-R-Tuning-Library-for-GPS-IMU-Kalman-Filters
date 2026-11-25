# home/20260927_115918_outages_s0

## Test part

Horizontal RMSE in m.

| method                                |   rmse_all |   rmse_heavy_15m |   rmse_outage |   rmse_recovery_30s |   rmse_outside |   nis_over_dof |   switches |   online_entries |
|:--------------------------------------|-----------:|-----------------:|--------------:|--------------------:|---------------:|---------------:|-----------:|-----------------:|
| Raw GPS                               |       9.33 |             18   |         nan   |                3.73 |           6.53 |        nan     |        nan |              nan |
| Baseline THETA0                       |      54.5  |             18.9 |         135   |               59.8  |           7.06 |          1.64  |          0 |              nan |
| Static (llm)                          |     198    |             21.9 |         502   |              206    |           6.88 |         10.4   |          0 |              nan |
| Library (llm)                         |      25    |             18.3 |          58.8 |               26.4  |           6.85 |          0.959 |          8 |              nan |
| Library, true condition (llm)         |      30.6  |             17.1 |          73.6 |               33.2  |           7.41 |          0.997 |          2 |              nan |
| Library, no plausibility filter (llm) |      44    |             22   |         108   |               49.2  |           6.81 |          6.72  |          6 |              nan |
| Static (gwo)                          |      90.9  |             23.7 |         227   |              102    |           7.02 |         20.7   |          0 |              nan |
| Library (gwo)                         |      31.2  |             19.4 |          74.3 |               35.7  |           7.2  |          2.11  |          8 |              nan |
| Library, true condition (gwo)         |      48.1  |             16.9 |         119   |               54.1  |           6.96 |          1.88  |          2 |              nan |
| Library, no plausibility filter (gwo) |     216    |             42.6 |         541   |              242    |           6.96 |         56     |          6 |              nan |
| Library + online update (llm)         |      28.7  |             19.5 |          68.2 |               31.5  |           7.03 |          0.908 |        nan |                2 |
| Library + online update (gwo)         |      29.9  |             19.2 |          71.2 |               34.3  |           7.15 |          2.04  |        nan |                2 |

## Training part (initialization period)

| method                    |   train_rmse_all |   train_rmse_moderate_5m |   train_rmse_moderate_5m_first10s |   train_rmse_outside |   tunings |
|:--------------------------|-----------------:|-------------------------:|----------------------------------:|---------------------:|----------:|
| THETA0                    |             9.59 |                     9.86 |                              8.8  |                 9.51 |       nan |
| Initialization mode (llm) |            15.4  |                    17.5  |                              8.34 |                14.7  |         8 |
| Initialization mode (gwo) |            14    |                    16.1  |                              7.53 |                13.3  |         8 |
