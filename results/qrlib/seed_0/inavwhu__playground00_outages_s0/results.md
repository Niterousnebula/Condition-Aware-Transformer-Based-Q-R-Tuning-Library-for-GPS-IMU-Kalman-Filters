# inavwhu/playground00_outages_s0

## Test part

Horizontal RMSE in m.

| method                                   |   rmse_all |   rmse_heavy_15m |   rmse_outage |   rmse_recovery_30s |   rmse_outside |   nis_over_dof |   switches |   online_entries |
|:-----------------------------------------|-----------:|-----------------:|--------------:|--------------------:|---------------:|---------------:|-----------:|-----------------:|
| Raw GPS                                  |       4.74 |            17.2  |        nan    |                1.49 |           1.32 |        nan     |        nan |              nan |
| Baseline THETA0                          |      15.6  |            11.8  |         56    |               24.4  |           1.57 |          7.48  |          0 |              nan |
| Paper 1 GWO (ground truth, offline)      |       3.34 |             7.76 |          8.27 |                4.18 |           1.57 |          1.32  |          0 |              nan |
| Static (llm)                             |      10.1  |            10.4  |         35.6  |               15.7  |           1.57 |          4.71  |          0 |              nan |
| Library (llm)                            |       3.62 |            10.3  |          7.41 |                3.96 |           1.55 |          1.46  |          2 |              nan |
| Library, true condition (llm)            |       3.57 |            10.2  |          6.87 |                3.72 |           1.69 |          1.6   |          2 |              nan |
| Library, no plausibility filter (llm)    |      34.5  |            21.5  |        125    |               54.7  |           1.53 |         34.3   |          2 |              nan |
| Static (random)                          |       8.8  |            10.4  |         30.4  |               13.5  |           1.56 |          2.9   |          0 |              nan |
| Library (random)                         |       2.97 |             8.86 |          4.72 |                2.56 |           1.55 |          0.621 |          2 |              nan |
| Library, true condition (random)         |       3.12 |             9.12 |          4.98 |                2.67 |           1.71 |          0.692 |          2 |              nan |
| Library, no plausibility filter (random) |      10.9  |            15.6  |         36.6  |               17.4  |           1.56 |         11.1   |          2 |              nan |
| Static (gwo)                             |       7.43 |             8.97 |         25.4  |               11.6  |           1.52 |          6.49  |          0 |              nan |
| Library (gwo)                            |       3.06 |            10.4  |          1.82 |                1.63 |           1.54 |          2.62  |          3 |              nan |
| Library, true condition (gwo)            |       3.17 |            10.5  |          2.75 |                1.87 |           1.67 |          2.78  |          2 |              nan |
| Library, no plausibility filter (gwo)    |      50.1  |            16.5  |        183    |               83.2  |           1.8  |         15.8   |          3 |              nan |
| Library + online update (llm)            |       4.3  |            14.2  |          7.13 |                3.88 |           1.36 |          0.668 |        nan |                2 |
| Library + online update (random)         |       3.35 |            10.1  |          5.68 |                2.94 |           1.61 |          2.97  |        nan |                2 |
| Library + online update (gwo)            |       3.48 |            10.9  |          5.85 |                2.9  |           1.48 |          8     |        nan |                2 |

## Training part (initialization period)

| method                       |   train_rmse_all |   train_rmse_moderate_5m |   train_rmse_moderate_5m_first10s |   train_rmse_outside |   tunings |
|:-----------------------------|-----------------:|-------------------------:|----------------------------------:|---------------------:|----------:|
| THETA0                       |             1.22 |                     2.81 |                              2.35 |                0.796 |       nan |
| Initialization mode (llm)    |             1.54 |                     3.92 |                              3.95 |                0.813 |         8 |
| Initialization mode (random) |             1.36 |                     3.4  |                              2.83 |                0.766 |         8 |
| Initialization mode (gwo)    |             1.52 |                     3.87 |                              3.65 |                0.799 |         8 |
