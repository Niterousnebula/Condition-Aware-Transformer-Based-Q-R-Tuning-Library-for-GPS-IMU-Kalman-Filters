# eth_outages_s0

## Test part

Horizontal RMSE in m.

| method                                   |   rmse_all |   rmse_heavy_15m |   rmse_outage |   rmse_recovery_30s |   rmse_outside |   nis_over_dof |   switches |   online_entries |
|:-----------------------------------------|-----------:|-----------------:|--------------:|--------------------:|---------------:|---------------:|-----------:|-----------------:|
| Raw GPS                                  |       5.78 |            15.2  |    nan        |                2.23 |           3.93 |        nan     |        nan |              nan |
| Baseline THETA0                          |     827    |             4.58 |      3.49e+03 |                2.4  |           4.12 |          0.54  |          0 |              nan |
| Paper 1 GWO (ground truth, offline)      |     497    |             5.72 |      2.1e+03  |                2.32 |           4.04 |          1.15  |          0 |              nan |
| Static (llm)                             |     652    |             5.52 |      2.75e+03 |                2.32 |           4.04 |          1.86  |          0 |              nan |
| Library (llm)                            |     517    |             4.49 |      2.19e+03 |                2.43 |           4.11 |          1.07  |          3 |              nan |
| Library, true condition (llm)            |     513    |             4.5  |      2.17e+03 |                2.43 |           4.11 |          1.08  |          2 |              nan |
| Library, no plausibility filter (llm)    |     551    |             4.56 |      2.33e+03 |                2.43 |           4.11 |          1.18  |          4 |              nan |
| Static (random)                          |     510    |             4.23 |      2.16e+03 |                2.51 |           4.17 |          5.4   |          0 |              nan |
| Library (random)                         |     215    |             4.52 |    910        |                2.27 |           3.98 |          0.953 |          3 |              nan |
| Library, true condition (random)         |     207    |             4.52 |    874        |                2.27 |           3.98 |          0.962 |          2 |              nan |
| Library, no plausibility filter (random) |     326    |             5.16 |      1.38e+03 |                2.27 |           3.98 |          1.69  |          4 |              nan |
| Static (gwo)                             |     403    |             3.63 |      1.7e+03  |                2.66 |           4.28 |          1.29  |          0 |              nan |
| Library (gwo)                            |     470    |             4.53 |      1.99e+03 |                2.25 |           3.97 |          0.558 |          3 |              nan |
| Library, true condition (gwo)            |     472    |             4.52 |      2e+03    |                2.25 |           3.97 |          0.565 |          2 |              nan |
| Library, no plausibility filter (gwo)    |     515    |             4.98 |      2.18e+03 |                2.25 |           3.97 |          0.907 |          4 |              nan |
| Library + online update (llm)            |     411    |             5.2  |      1.74e+03 |                2.41 |           4.11 |          3.23  |        nan |                2 |
| Library + online update (random)         |     286    |             3.57 |      1.21e+03 |                2.27 |           3.98 |          3.21  |        nan |                2 |
| Library + online update (gwo)            |     515    |             3.94 |      2.18e+03 |                2.26 |           3.97 |          1.29  |        nan |                2 |

## Training part (initialization period)

| method                       |   train_rmse_all |   train_rmse_moderate_5m |   train_rmse_moderate_5m_first10s |   train_rmse_outside |   tunings |
|:-----------------------------|-----------------:|-------------------------:|----------------------------------:|---------------------:|----------:|
| THETA0                       |             3.6  |                     3.11 |                              2.83 |                 3.65 |       nan |
| Initialization mode (llm)    |             3.61 |                     3.27 |                              3.21 |                 3.65 |        10 |
| Initialization mode (random) |             3.55 |                     3.27 |                              3.29 |                 3.58 |        10 |
| Initialization mode (gwo)    |             3.55 |                     3.34 |                              3.36 |                 3.58 |        10 |
