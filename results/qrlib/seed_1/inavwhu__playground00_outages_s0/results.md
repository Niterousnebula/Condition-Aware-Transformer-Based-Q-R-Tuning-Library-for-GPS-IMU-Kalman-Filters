# inavwhu/playground00_outages_s0

## Test part

Horizontal RMSE in m.

| method                                   |   rmse_all |   rmse_heavy_15m |   rmse_outage |   rmse_recovery_30s |   rmse_outside |   nis_over_dof |   switches |   online_entries |
|:-----------------------------------------|-----------:|-----------------:|--------------:|--------------------:|---------------:|---------------:|-----------:|-----------------:|
| Raw GPS                                  |       4.74 |            17.2  |        nan    |                1.49 |           1.32 |         nan    |        nan |              nan |
| Baseline THETA0                          |      15.6  |            11.8  |         56    |               24.4  |           1.57 |           7.48 |          0 |              nan |
| Paper 1 GWO (ground truth, offline)      |       3.34 |             7.76 |          8.27 |                4.18 |           1.57 |           1.32 |          0 |              nan |
| Static (llm)                             |      11.4  |            11.2  |         40.1  |               17.7  |           1.57 |           3.44 |          0 |              nan |
| Library (llm)                            |       3.37 |            10.8  |          4.83 |                2.64 |           1.55 |           2.32 |          2 |              nan |
| Library, true condition (llm)            |       3.25 |            10.9  |          2.39 |                1.82 |           1.7  |           2.56 |          2 |              nan |
| Library, no plausibility filter (llm)    |      15.6  |            14.2  |         56    |               22.9  |           1.65 |          25.5  |          2 |              nan |
| Static (random)                          |       8.99 |            10.6  |         31    |               13.7  |           1.58 |           2.84 |          0 |              nan |
| Library (random)                         |       3.11 |             9.79 |          4.36 |                2.45 |           1.55 |           5.29 |          3 |              nan |
| Library, true condition (random)         |       3.54 |             9.95 |          6.95 |                3.5  |           1.72 |           5.78 |          2 |              nan |
| Library, no plausibility filter (random) |      35.4  |            15.4  |        129    |               59.3  |           1.52 |          92.1  |          3 |              nan |
| Static (gwo)                             |       7.45 |             8.93 |         25.5  |               11.6  |           1.52 |           4.19 |          0 |              nan |
| Library (gwo)                            |       3.96 |            10.3  |          9.45 |                4.77 |           1.54 |           2.51 |          3 |              nan |
| Library, true condition (gwo)            |       3.87 |            10.3  |          8.69 |                4.46 |           1.67 |           2.65 |          2 |              nan |
| Library, no plausibility filter (gwo)    |      19.8  |            21.6  |         69.5  |               30.6  |           1.64 |          22.7  |          3 |              nan |
| Library + online update (llm)            |       4.36 |            15.5  |          3.32 |                2.1  |           1.76 |           1.46 |        nan |                2 |
| Library + online update (random)         |       5.31 |            18.2  |          7.14 |                3.59 |           1.85 |           2.48 |        nan |                2 |
| Library + online update (gwo)            |       3.76 |            10.3  |          8.35 |                4.33 |           1.52 |           3.12 |        nan |                2 |

## Training part (initialization period)

| method                       |   train_rmse_all |   train_rmse_moderate_5m |   train_rmse_moderate_5m_first10s |   train_rmse_outside |   tunings |
|:-----------------------------|-----------------:|-------------------------:|----------------------------------:|---------------------:|----------:|
| THETA0                       |             1.22 |                     2.81 |                              2.35 |                0.796 |       nan |
| Initialization mode (llm)    |             1.49 |                     3.8  |                              3.79 |                0.781 |         8 |
| Initialization mode (random) |             1.38 |                     3.42 |                              4.03 |                0.79  |         8 |
| Initialization mode (gwo)    |             1.57 |                     4.03 |                              3.92 |                0.8   |         8 |
