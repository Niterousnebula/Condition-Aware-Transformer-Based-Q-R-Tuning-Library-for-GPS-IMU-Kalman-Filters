# eth_outages_s0

## Test part

Horizontal RMSE in m.

| method                                   |   rmse_all |   rmse_heavy_15m |   rmse_outage |   rmse_recovery_30s |   rmse_outside |   nis_over_dof |   switches |   online_entries |
|:-----------------------------------------|-----------:|-----------------:|--------------:|--------------------:|---------------:|---------------:|-----------:|-----------------:|
| Raw GPS                                  |       5.78 |            15.2  |    nan        |                2.23 |           3.93 |        nan     |        nan |              nan |
| Baseline THETA0                          |     827    |             4.58 |      3.49e+03 |                2.4  |           4.12 |          0.54  |          0 |              nan |
| Paper 1 GWO (ground truth, offline)      |     497    |             5.72 |      2.1e+03  |                2.32 |           4.04 |          1.15  |          0 |              nan |
| Static (llm)                             |     673    |             6.34 |      2.84e+03 |                2.31 |           4.01 |          5.38  |          0 |              nan |
| Library (llm)                            |     586    |             3.99 |      2.48e+03 |                2.28 |           3.99 |          0.648 |          3 |              nan |
| Library, true condition (llm)            |     602    |             4.01 |      2.54e+03 |                2.28 |           3.99 |          0.657 |          2 |              nan |
| Library, no plausibility filter (llm)    |     615    |             4.57 |      2.6e+03  |                2.29 |           3.99 |          0.888 |          4 |              nan |
| Static (random)                          |     632    |             3.3  |      2.67e+03 |                2.74 |           4.4  |          2.1   |          0 |              nan |
| Library (random)                         |     551    |             4.12 |      2.33e+03 |                2.25 |           3.97 |          0.69  |          3 |              nan |
| Library, true condition (random)         |     570    |             4.06 |      2.41e+03 |                2.25 |           3.97 |          0.7   |          2 |              nan |
| Library, no plausibility filter (random) |     622    |             4.95 |      2.63e+03 |                2.25 |           3.97 |          1.79  |          4 |              nan |
| Static (gwo)                             |     501    |             4.18 |      2.11e+03 |                2.47 |           4.15 |          0.538 |          0 |              nan |
| Library (gwo)                            |     329    |             4.52 |      1.39e+03 |                2.29 |           4.01 |          0.68  |          3 |              nan |
| Library, true condition (gwo)            |     328    |             4.5  |      1.39e+03 |                2.29 |           4    |          0.688 |          2 |              nan |
| Library, no plausibility filter (gwo)    |     322    |             4.68 |      1.36e+03 |                2.29 |           4    |          0.938 |          4 |              nan |
| Library + online update (llm)            |     513    |             3.42 |      2.17e+03 |                2.26 |           3.99 |          0.953 |        nan |                2 |
| Library + online update (random)         |     544    |             3.62 |      2.3e+03  |                2.26 |           3.97 |          0.774 |        nan |                2 |
| Library + online update (gwo)            |     359    |             4.15 |      1.51e+03 |                2.3  |           4    |          1.48  |        nan |                2 |

## Training part (initialization period)

| method                       |   train_rmse_all |   train_rmse_moderate_5m |   train_rmse_moderate_5m_first10s |   train_rmse_outside |   tunings |
|:-----------------------------|-----------------:|-------------------------:|----------------------------------:|---------------------:|----------:|
| THETA0                       |             3.6  |                     3.11 |                              2.83 |                 3.65 |       nan |
| Initialization mode (llm)    |             3.56 |                     3.26 |                              3.4  |                 3.59 |        10 |
| Initialization mode (random) |             3.56 |                     3.39 |                              3.26 |                 3.58 |        10 |
| Initialization mode (gwo)    |             3.56 |                     3.22 |                              3.33 |                 3.6  |        10 |
