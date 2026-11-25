# Q/R library: paper tables
Root: D:\BTP2 EKF\results\qrlib; seeds 0, 1, 2; main builder llm.

## Raw GPS against our system (LLM builder), test part, mean ± std over seeds; the winner in bold

| Drive               | Metric (horizontal RMSE, m)   | Raw GPS   | Our system (LLM)     | Winner                                 |
|:--------------------|:------------------------------|:----------|:---------------------|:---------------------------------------|
| ETH                 | 15 m section                  | 15.17     | **3.87 ± 0.42**      | Our system (74 % lower)                |
| ETH                 | Normal GPS                    | **3.93**  | 4.01 ± 0.09          | Raw GPS (2 % lower)                    |
| ETH                 | 30 s after outage             | **2.23**  | 2.29 ± 0.08          | Raw GPS (3 % lower)                    |
| ETH                 | Outage                        | no fixes  | **2032.34 ± 166.36** | Our system (raw GPS gives no position) |
| iNav-WHU playground | 15 m section                  | 17.19     | **8.75 ± 0.07**      | Our system (49 % lower)                |
| iNav-WHU playground | Normal GPS                    | **1.32**  | 1.41 ± 0.03          | Raw GPS (7 % lower)                    |
| iNav-WHU playground | 30 s after outage             | **1.49**  | 3.06 ± 1.30          | Raw GPS (51 % lower)                   |
| iNav-WHU playground | Outage                        | no fixes  | **5.35 ± 3.47**      | Our system (raw GPS gives no position) |
| iNav-WHU street     | 15 m section                  | 16.91     | **7.04 ± 0.17**      | Our system (58 % lower)                |
| iNav-WHU street     | Normal GPS                    | **1.20**  | 1.25 ± 0.01          | Raw GPS (4 % lower)                    |
| iNav-WHU street     | 30 s after outage             | **0.87**  | 7.40 ± 0.13          | Raw GPS (88 % lower)                   |
| iNav-WHU street     | Outage                        | no fixes  | **25.39 ± 0.42**     | Our system (raw GPS gives no position) |
| Home drive          | 15 m section                  | **17.96** | 19.35 ± 1.44         | Raw GPS (7 % lower)                    |
| Home drive          | Normal GPS                    | **6.53**  | 7.77 ± 0.67          | Raw GPS (16 % lower)                   |
| Home drive          | 30 s after outage             | **3.73**  | 30.13 ± 2.88         | Raw GPS (88 % lower)                   |
| Home drive          | Outage                        | no fixes  | **66.26 ± 6.03**     | Our system (raw GPS gives no position) |

## Test part, horizontal RMSE (m), mean ± std over seeds

| Drive               | Method                              | 15 m section   | Normal GPS   | 30 s after outage   | Outage           | NIS / dof     |
|:--------------------|:------------------------------------|:---------------|:-------------|:--------------------|:-----------------|:--------------|
| ETH                 | Raw GPS                             | 15.17          | 3.93         | 2.23                | –                | –             |
| ETH                 | Baseline THETA0                     | 4.58           | 4.12         | 2.40                | 3493.03          | 0.54          |
| ETH                 | Paper 1 GWO (ground truth, offline) | 5.72           | 4.04         | 2.32                | 2100.28          | 1.15          |
| ETH                 | Static (llm)                        | 4.88 ± 1.38    | 4.12 ± 0.10  | 2.45 ± 0.14         | 2067.00 ± 150.42 | 3.15 ± 1.46   |
| ETH                 | Library (llm)                       | 3.87 ± 0.42    | 4.01 ± 0.09  | 2.29 ± 0.08         | 2032.34 ± 166.36 | 1.00 ± 0.40   |
| ETH                 | Static (gwo)                        | 3.73 ± 0.41    | 4.27 ± 0.11  | 2.62 ± 0.13         | 2005.30 ± 263.36 | 5.90 ± 8.65   |
| ETH                 | Library (gwo)                       | 3.48 ± 0.14    | 4.01 ± 0.04  | 2.33 ± 0.07         | 1706.74 ± 262.81 | 0.59 ± 0.06   |
| Home drive          | Raw GPS                             | 17.96          | 6.53         | 3.73                | –                | –             |
| Home drive          | Baseline THETA0                     | 18.90          | 7.06         | 59.77               | 135.42           | 1.64          |
| Home drive          | Static (llm)                        | 22.41 ± 1.04   | 6.92 ± 0.06  | 147.25 ± 83.72      | 357.75 ± 207.99  | 47.62 ± 60.70 |
| Home drive          | Library (llm)                       | 19.35 ± 1.44   | 7.77 ± 0.67  | 30.13 ± 2.88        | 66.26 ± 6.03     | 1.06 ± 0.41   |
| Home drive          | Static (gwo)                        | 23.33 ± 1.39   | 6.94 ± 0.20  | 151.25 ± 48.71      | 362.88 ± 131.91  | 56.97 ± 53.58 |
| Home drive          | Library (gwo)                       | 18.45 ± 1.12   | 7.10 ± 0.09  | 32.24 ± 3.22        | 66.71 ± 11.77    | 1.88 ± 0.14   |
| iNav-WHU playground | Raw GPS                             | 17.19          | 1.32         | 1.49                | –                | –             |
| iNav-WHU playground | Baseline THETA0                     | 11.78          | 1.57         | 24.41               | 55.99            | 7.48          |
| iNav-WHU playground | Paper 1 GWO (ground truth, offline) | 7.76           | 1.57         | 4.18                | 8.27             | 1.32          |
| iNav-WHU playground | Static (llm)                        | 10.36 ± 0.90   | 1.55 ± 0.03  | 13.47 ± 5.64        | 30.34 ± 13.17    | 5.79 ± 3.03   |
| iNav-WHU playground | Library (llm)                       | 8.75 ± 0.07    | 1.41 ± 0.03  | 3.06 ± 1.30         | 5.35 ± 3.47      | 0.21          |
| iNav-WHU playground | Static (gwo)                        | 8.97 ± 0.04    | 1.52         | 11.53 ± 0.07        | 25.37 ± 0.15     | 5.06 ± 1.25   |
| iNav-WHU playground | Library (gwo)                       | 8.66 ± 0.07    | 1.36 ± 0.02  | 4.29 ± 2.01         | 8.37 ± 4.25      | 0.32 ± 0.17   |
| iNav-WHU street     | Raw GPS                             | 16.91          | 1.20         | 0.87                | –                | –             |
| iNav-WHU street     | Baseline THETA0                     | 10.93          | 1.32         | 1.65                | 6.92             | 5.38          |
| iNav-WHU street     | Paper 1 GWO (ground truth, offline) | 7.73           | 1.43         | 1.71                | 6.41             | 1.26          |
| iNav-WHU street     | Static (llm)                        | 9.69 ± 0.20    | 1.27         | 1.69 ± 0.15         | 3.82 ± 0.61      | 2.53 ± 0.54   |
| iNav-WHU street     | Library (llm)                       | 7.04 ± 0.17    | 1.25 ± 0.01  | 7.40 ± 0.13         | 25.39 ± 0.42     | 0.41 ± 0.21   |
| iNav-WHU street     | Static (gwo)                        | 8.97 ± 0.32    | 1.28         | 2.65 ± 0.17         | 7.96 ± 0.50      | 6.49 ± 2.80   |
| iNav-WHU street     | Library (gwo)                       | 6.93 ± 0.24    | 1.24 ± 0.01  | 7.32 ± 0.66         | 25.76 ± 4.06     | 0.44 ± 0.22   |

## Ablations (LLM builder), test part RMSE (m)

| Drive               | Variant                                          | 15 m section   | Normal GPS   | 30 s after outage   | Outage           |   Seeds |
|:--------------------|:-------------------------------------------------|:---------------|:-------------|:--------------------|:-----------------|--------:|
| ETH                 | Full: library + online update                    | 3.87 ± 0.42    | 4.01 ± 0.09  | 2.29 ± 0.08         | 2032.34 ± 166.36 |       3 |
| ETH                 | Without online update                            | 3.77           | 4.01 ± 0.09  | 2.31 ± 0.11         | 2252.30 ± 237.28 |       3 |
| ETH                 | Without plausibility filter                      | 4.68 ± 0.96    | 4.01 ± 0.09  | 2.31 ± 0.11         | 2391.54 ± 188.46 |       3 |
| ETH                 | True condition instead of detector (upper bound) | 3.78 ± 0.02    | 4.01 ± 0.09  | 2.31 ± 0.11         | 2253.23 ± 287.15 |       3 |
| ETH                 | Offline build instead of initialization mode     | 3.43           | 3.93         | 2.22                | 2086.28          |       1 |
| ETH                 | One-step score (no simulated dropouts)           | 3.38           | 3.92         | 2.21                | 5489.04          |       1 |
| ETH                 | Q over THETA0 +- 3 decades                       | 3.47           | 3.96         | 2.22                | 2015.53          |       1 |
| Home drive          | Full: library + online update                    | 19.35 ± 1.44   | 7.77 ± 0.67  | 30.13 ± 2.88        | 66.26 ± 6.03     |       3 |
| Home drive          | Without online update                            | 18.20 ± 1.66   | 6.95 ± 0.24  | 27.02 ± 1.90        | 60.87 ± 5.34     |       3 |
| Home drive          | Without plausibility filter                      | 24.09 ± 6.82   | 7.27 ± 0.75  | 34.17 ± 13.08       | 76.18 ± 27.35    |       3 |
| Home drive          | True condition instead of detector (upper bound) | 16.47 ± 1.09   | 7.16 ± 0.25  | 30.44 ± 4.13        | 68.07 ± 9.26     |       3 |
| Home drive          | Offline build instead of initialization mode     | 20.51          | 7.30         | 23.78               | 54.49            |       1 |
| Home drive          | One-step score (no simulated dropouts)           | 20.98          | 7.80         | 31.60               | 70.29            |       1 |
| Home drive          | Q over THETA0 +- 3 decades                       | 18.18          | 7.07         | 28.04               | 62.28            |       1 |
| iNav-WHU playground | Full: library + online update                    | 8.75 ± 0.07    | 1.41 ± 0.03  | 3.06 ± 1.30         | 5.35 ± 3.47      |       3 |
| iNav-WHU playground | Without online update                            | 8.70 ± 0.16    | 1.44 ± 0.02  | 3.13 ± 1.33         | 5.53 ± 3.54      |       3 |
| iNav-WHU playground | Without plausibility filter                      | 47.66 ± 12.86  | 1.95 ± 0.29  | 44.81 ± 32.09       | 101.36 ± 71.18   |       3 |
| iNav-WHU playground | True condition instead of detector (upper bound) | 8.69 ± 0.16    | 1.46 ± 0.02  | 3.08 ± 1.29         | 5.43 ± 3.41      |       3 |
| iNav-WHU playground | Offline build instead of initialization mode     | 8.52           | 1.38         | 4.50                | 8.77             |       1 |
| iNav-WHU playground | One-step score (no simulated dropouts)           | 7.74           | 1.38         | 8.51                | 19.05            |       1 |
| iNav-WHU playground | Q over THETA0 +- 3 decades                       | 8.39           | 1.40         | 3.53                | 7.23             |       1 |
| iNav-WHU street     | Full: library + online update                    | 7.04 ± 0.17    | 1.25 ± 0.01  | 7.40 ± 0.13         | 25.39 ± 0.42     |       3 |
| iNav-WHU street     | Without online update                            | 7.15 ± 0.20    | 1.23         | 7.43 ± 0.13         | 25.53 ± 0.48     |       3 |
| iNav-WHU street     | Without plausibility filter                      | 37.45 ± 2.47   | 1.54 ± 0.35  | 65.06 ± 24.15       | 229.41 ± 81.96   |       3 |
| iNav-WHU street     | True condition instead of detector (upper bound) | 7.22 ± 0.19    | 1.23         | 7.41 ± 0.13         | 25.47 ± 0.45     |       3 |
| iNav-WHU street     | Offline build instead of initialization mode     | 6.94           | 1.24         | 6.80                | 24.14            |       1 |
| iNav-WHU street     | One-step score (no simulated dropouts)           | 7.51           | 1.24         | 11.54               | 46.13            |       1 |
| iNav-WHU street     | Q over THETA0 +- 3 decades                       | 7.22           | 1.25         | 7.10                | 25.00            |       1 |

## Initialization period (drive start to split), RMSE (m)

| Drive               | Method                    | Whole period   | 5 m section   | First 10 s of it   | Normal GPS   |
|:--------------------|:--------------------------|:---------------|:--------------|:-------------------|:-------------|
| ETH                 | THETA0                    | 3.60           | 3.11          | 2.83               | 3.65         |
| ETH                 | Initialization mode (llm) | 3.57 ± 0.04    | 3.26 ± 0.04   | 3.48 ± 0.32        | 3.60 ± 0.04  |
| ETH                 | Initialization mode (gwo) | 3.56 ± 0.01    | 3.27 ± 0.07   | 3.32 ± 0.04        | 3.60 ± 0.02  |
| Home drive          | THETA0                    | 9.59           | 9.86          | 8.80               | 9.51         |
| Home drive          | Initialization mode (llm) | 15.79 ± 2.80   | 14.82 ± 3.33  | 10.87 ± 4.28       | 16.01 ± 3.09 |
| Home drive          | Initialization mode (gwo) | 13.23 ± 1.55   | 13.16 ± 3.09  | 7.38 ± 2.75        | 13.22 ± 1.32 |
| iNav-WHU playground | THETA0                    | 1.22           | 2.81          | 2.35               | 0.80         |
| iNav-WHU playground | Initialization mode (llm) | 1.62 ± 0.07    | 4.21 ± 0.23   | 4.45 ± 0.50        | 0.80 ± 0.01  |
| iNav-WHU playground | Initialization mode (gwo) | 1.57 ± 0.04    | 4.04 ± 0.13   | 4.43 ± 0.54        | 0.79         |
| iNav-WHU street     | THETA0                    | 1.21           | 2.81          | 2.36               | 0.79         |
| iNav-WHU street     | Initialization mode (llm) | 1.78 ± 0.02    | 4.78 ± 0.06   | 3.55 ± 0.19        | 0.76         |
| iNav-WHU street     | Initialization mode (gwo) | 1.72 ± 0.07    | 4.58 ± 0.24   | 3.35 ± 0.36        | 0.76         |

## LLM cost

| Drive               |   LLM calls per run | Prompt tokens per call   | Reply tokens per call   | Settings parsed   | Seconds per call   | LLM minutes per run   |
|:--------------------|--------------------:|:-------------------------|:------------------------|:------------------|:-------------------|:----------------------|
| ETH                 |                  18 | 1096.11 ± 4.48           | 459.96 ± 11.89          | 94 %              | 11.77 ± 0.30       | 3.53 ± 0.09           |
| Home drive          |                  18 | 1015.52 ± 4.37           | 423.43 ± 9.39           | 98 %              | 10.97 ± 0.22       | 3.29 ± 0.07           |
| iNav-WHU playground |                  18 | 1000.35 ± 2.44           | 409.85 ± 12.85          | 92 %              | 10.60 ± 0.33       | 3.18 ± 0.10           |
| iNav-WHU street     |                  18 | 1001.07 ± 1.75           | 419.98 ± 9.24           | 93 %              | 10.84 ± 0.20       | 3.25 ± 0.06           |

## Condition detector (seed 0)

| Drive               | Agreement, test part   | Agreement, initialization   |   Onset delay, 5 m (s) |   Onset delay, 15 m (s) |   Without trigger, 15 m (s) |
|:--------------------|:-----------------------|:----------------------------|-----------------------:|------------------------:|----------------------------:|
| ETH                 | 99.1 %                 | 98.9 %                      |                      1 |                       1 |                          11 |
| Home drive          | 88.8 %                 | 88.2 %                      |                      0 |                      11 |                          11 |
| iNav-WHU playground | 97.1 %                 | 96.5 %                      |                      5 |                       4 |                           9 |
| iNav-WHU street     | 97.6 %                 | 96.9 %                      |                      7 |                       6 |                          13 |
