# Q/R library: paper tables
Root: D:\BTP2 EKF\results\qrlib; seeds 0, 1, 2; main builder llm.

## Raw GPS against our system (LLM builder), test part, mean ± std over seeds; the winner in bold

| Drive               | Metric (horizontal RMSE, m)   | Raw GPS   | Our system (LLM)     | Winner                                 |
|:--------------------|:------------------------------|:----------|:---------------------|:---------------------------------------|
| ETH                 | 15 m section                  | 15.17     | **4.80 ± 1.23**      | Our system (68 % lower)                |
| ETH                 | Normal GPS                    | **3.93**  | 4.02 ± 0.07          | Raw GPS (2 % lower)                    |
| ETH                 | 30 s after outage             | **2.23**  | 2.30 ± 0.10          | Raw GPS (3 % lower)                    |
| ETH                 | Outage                        | no fixes  | **2001.75 ± 232.00** | Our system (raw GPS gives no position) |
| iNav-WHU playground | 15 m section                  | 17.19     | **14.64 ± 0.76**     | Our system (15 % lower)                |
| iNav-WHU playground | Normal GPS                    | **1.32**  | 1.62 ± 0.23          | Raw GPS (19 % lower)                   |
| iNav-WHU playground | 30 s after outage             | **1.49**  | 3.28 ± 1.02          | Raw GPS (55 % lower)                   |
| iNav-WHU playground | Outage                        | no fixes  | **6.12 ± 2.46**      | Our system (raw GPS gives no position) |
| iNav-WHU street     | 15 m section                  | **16.91** | 34.67 ± 11.82        | Raw GPS (51 % lower)                   |
| iNav-WHU street     | Normal GPS                    | **1.20**  | 2.70 ± 1.30          | Raw GPS (56 % lower)                   |
| iNav-WHU street     | 30 s after outage             | **0.87**  | 7.18 ± 0.55          | Raw GPS (88 % lower)                   |
| iNav-WHU street     | Outage                        | no fixes  | **24.95 ± 0.92**     | Our system (raw GPS gives no position) |

## Test part, horizontal RMSE (m), mean ± std over seeds

| Drive               | Method                              | 15 m section   | Normal GPS   | 30 s after outage   | Outage           | NIS / dof       |
|:--------------------|:------------------------------------|:---------------|:-------------|:--------------------|:-----------------|:----------------|
| ETH                 | Raw GPS                             | 15.17          | 3.93         | 2.23                | –                | –               |
| ETH                 | Baseline THETA0                     | 4.58           | 4.12         | 2.40                | 3493.03          | 0.54            |
| ETH                 | Paper 1 GWO (ground truth, offline) | 5.72           | 4.04         | 2.32                | 2100.28          | 1.15            |
| ETH                 | Static (llm)                        | 6.11 ± 0.52    | 4.02 ± 0.02  | 2.31 ± 0.01         | 2610.96 ± 326.94 | 2.90 ± 2.16     |
| ETH                 | Library (llm)                       | 4.80 ± 1.23    | 4.02 ± 0.07  | 2.30 ± 0.10         | 2001.75 ± 232.00 | 1.70 ± 1.33     |
| ETH                 | Static (random)                     | 3.86 ± 0.50    | 4.26 ± 0.12  | 2.60 ± 0.12         | 2241.98 ± 391.80 | 4.84 ± 2.52     |
| ETH                 | Library (random)                    | 3.81 ± 0.37    | 3.98 ± 0.01  | 2.27 ± 0.01         | 1900.74 ± 601.06 | 1.60 ± 1.40     |
| ETH                 | Static (gwo)                        | 3.73 ± 0.41    | 4.27 ± 0.11  | 2.62 ± 0.13         | 2005.30 ± 263.36 | 5.90 ± 8.65     |
| ETH                 | Library (gwo)                       | 4.06 ± 0.11    | 4.01 ± 0.04  | 2.30 ± 0.05         | 1876.95 ± 334.76 | 1.32 ± 0.15     |
| iNav-WHU playground | Raw GPS                             | 17.19          | 1.32         | 1.49                | –                | –               |
| iNav-WHU playground | Baseline THETA0                     | 11.78          | 1.57         | 24.41               | 55.99            | 7.48            |
| iNav-WHU playground | Paper 1 GWO (ground truth, offline) | 7.76           | 1.57         | 4.18                | 8.27             | 1.32            |
| iNav-WHU playground | Static (llm)                        | 10.36 ± 0.90   | 1.55 ± 0.03  | 13.47 ± 5.64        | 30.34 ± 13.17    | 5.79 ± 3.03     |
| iNav-WHU playground | Library (llm)                       | 14.64 ± 0.76   | 1.62 ± 0.23  | 3.28 ± 1.02         | 6.12 ± 2.46      | 2.02 ± 1.70     |
| iNav-WHU playground | Static (random)                     | 10.09 ± 0.74   | 1.55 ± 0.03  | 12.83 ± 1.31        | 28.86 ± 3.22     | 2.55 ± 0.55     |
| iNav-WHU playground | Library (random)                    | 12.93 ± 4.58   | 1.63 ± 0.21  | 3.26 ± 0.32         | 6.48 ± 0.74      | 1.96 ± 1.35     |
| iNav-WHU playground | Static (gwo)                        | 8.97 ± 0.04    | 1.52         | 11.53 ± 0.07        | 25.37 ± 0.15     | 5.06 ± 1.25     |
| iNav-WHU playground | Library (gwo)                       | 10.48 ± 0.38   | 1.51 ± 0.03  | 4.78 ± 2.14         | 9.58 ± 4.47      | 4.61 ± 2.95     |
| iNav-WHU street     | Raw GPS                             | 16.91          | 1.20         | 0.87                | –                | –               |
| iNav-WHU street     | Baseline THETA0                     | 10.93          | 1.32         | 1.65                | 6.92             | 5.38            |
| iNav-WHU street     | Paper 1 GWO (ground truth, offline) | 7.73           | 1.43         | 1.71                | 6.41             | 1.26            |
| iNav-WHU street     | Static (llm)                        | 22.74 ± 22.37  | 2.39 ± 1.93  | 27.69 ± 44.99       | 105.57 ± 175.59  | 348.67 ± 598.35 |
| iNav-WHU street     | Library (llm)                       | 34.67 ± 11.82  | 2.70 ± 1.30  | 7.18 ± 0.55         | 24.95 ± 0.92     | 1.75 ± 0.12     |
| iNav-WHU street     | Static (random)                     | 9.89 ± 0.26    | 1.34 ± 0.11  | 3.75 ± 2.48         | 14.23 ± 12.83    | 155.09 ± 261.95 |
| iNav-WHU street     | Library (random)                    | 40.46 ± 9.92   | 3.91 ± 2.21  | 7.64 ± 0.86         | 26.54 ± 2.51     | 2.20 ± 0.44     |
| iNav-WHU street     | Static (gwo)                        | 8.97 ± 0.32    | 1.28         | 2.65 ± 0.17         | 7.96 ± 0.50      | 6.49 ± 2.80     |
| iNav-WHU street     | Library (gwo)                       | 9.96 ± 0.80    | 1.26 ± 0.03  | 7.36 ± 0.78         | 25.92 ± 4.56     | 5.79 ± 4.25     |

## Ablations (LLM builder), test part RMSE (m)

| Drive               | Variant                                          | 15 m section   | Normal GPS   | 30 s after outage   | Outage           |   Seeds |
|:--------------------|:-------------------------------------------------|:---------------|:-------------|:--------------------|:-----------------|--------:|
| ETH                 | Full: library + online update                    | 4.80 ± 1.23    | 4.02 ± 0.07  | 2.30 ± 0.10         | 2001.75 ± 232.00 |       3 |
| ETH                 | Without online update                            | 4.13 ± 0.32    | 4.01 ± 0.10  | 2.31 ± 0.11         | 2232.67 ± 223.22 |       3 |
| ETH                 | Without plausibility filter                      | 4.99 ± 0.73    | 4.01 ± 0.09  | 2.31 ± 0.11         | 2425.99 ± 149.26 |       3 |
| ETH                 | True condition instead of detector (upper bound) | 4.13 ± 0.33    | 4.01 ± 0.09  | 2.31 ± 0.11         | 2238.61 ± 276.14 |       3 |
| ETH                 | Offline build instead of initialization mode     | 3.41           | 3.93         | 2.22                | 2137.09          |       1 |
| ETH                 | One-step score (no simulated dropouts)           | 3.56           | 3.92         | 2.21                | 4846.36          |       1 |
| ETH                 | Q over THETA0 +- 3 decades                       | 4.92           | 3.96         | 2.23                | 1932.26          |       1 |
| iNav-WHU playground | Full: library + online update                    | 14.64 ± 0.76   | 1.62 ± 0.23  | 3.28 ± 1.02         | 6.12 ± 2.46      |       3 |
| iNav-WHU playground | Without online update                            | 10.37 ± 0.37   | 1.54 ± 0.01  | 3.23 ± 0.67         | 6.09 ± 1.29      |       3 |
| iNav-WHU playground | Without plausibility filter                      | 17.26 ± 3.81   | 1.63 ± 0.09  | 31.83 ± 19.98       | 73.46 ± 45.35    |       3 |
| iNav-WHU playground | True condition instead of detector (upper bound) | 10.39 ± 0.45   | 1.68 ± 0.04  | 2.82 ± 0.96         | 4.96 ± 2.31      |       3 |
| iNav-WHU playground | Offline build instead of initialization mode     | 14.34          | 1.40         | 4.60                | 9.01             |       1 |
| iNav-WHU playground | One-step score (no simulated dropouts)           | 10.34          | 1.61         | 9.03                | 20.17            |       1 |
| iNav-WHU playground | Q over THETA0 +- 3 decades                       | 11.96          | 1.38         | 3.55                | 7.23             |       1 |
| iNav-WHU street     | Full: library + online update                    | 34.67 ± 11.82  | 2.70 ± 1.30  | 7.18 ± 0.55         | 24.95 ± 0.92     |       3 |
| iNav-WHU street     | Without online update                            | 9.90 ± 0.34    | 1.27 ± 0.02  | 7.30 ± 0.50         | 25.46 ± 0.76     |       3 |
| iNav-WHU street     | Without plausibility filter                      | 15.95 ± 1.13   | 1.32 ± 0.05  | 53.36 ± 37.20       | 200.37 ± 127.83  |       3 |
| iNav-WHU street     | True condition instead of detector (upper bound) | 10.00 ± 0.43   | 1.26 ± 0.02  | 7.13 ± 0.60         | 24.61 ± 1.13     |       3 |
| iNav-WHU street     | Offline build instead of initialization mode     | 28.43          | 2.58         | 7.29                | 26.14            |       1 |
| iNav-WHU street     | One-step score (no simulated dropouts)           | 11.63          | 1.25         | 9.16                | 39.11            |       1 |
| iNav-WHU street     | Q over THETA0 +- 3 decades                       | 34.94          | 2.73         | 6.10                | 19.19            |       1 |

## Initialization period (drive start to split), RMSE (m)

| Drive               | Method                       | Whole period   | 5 m section   | First 10 s of it   | Normal GPS   |
|:--------------------|:-----------------------------|:---------------|:--------------|:-------------------|:-------------|
| ETH                 | THETA0                       | 3.60           | 3.11          | 2.83               | 3.65         |
| ETH                 | Initialization mode (llm)    | 3.57 ± 0.04    | 3.29 ± 0.04   | 3.48 ± 0.32        | 3.60 ± 0.04  |
| ETH                 | Initialization mode (random) | 3.56 ± 0.01    | 3.32 ± 0.06   | 3.31 ± 0.07        | 3.58 ± 0.01  |
| ETH                 | Initialization mode (gwo)    | 3.56 ± 0.02    | 3.26 ± 0.07   | 3.32 ± 0.04        | 3.60 ± 0.02  |
| iNav-WHU playground | THETA0                       | 1.22           | 2.81          | 2.35               | 0.80         |
| iNav-WHU playground | Initialization mode (llm)    | 1.48 ± 0.06    | 3.75 ± 0.20   | 3.71 ± 0.29        | 0.79 ± 0.02  |
| iNav-WHU playground | Initialization mode (random) | 1.44 ± 0.11    | 3.62 ± 0.37   | 3.46 ± 0.60        | 0.78 ± 0.01  |
| iNav-WHU playground | Initialization mode (gwo)    | 1.54 ± 0.03    | 3.94 ± 0.08   | 3.88 ± 0.22        | 0.80         |
| iNav-WHU street     | THETA0                       | 1.21           | 2.81          | 2.36               | 0.79         |
| iNav-WHU street     | Initialization mode (llm)    | 1.45 ± 0.02    | 3.69 ± 0.07   | 2.92 ± 0.19        | 0.76         |
| iNav-WHU street     | Initialization mode (random) | 1.49 ± 0.02    | 3.83 ± 0.08   | 3.21 ± 0.08        | 0.76         |
| iNav-WHU street     | Initialization mode (gwo)    | 1.44 ± 0.04    | 3.68 ± 0.12   | 2.94 ± 0.22        | 0.76         |

## LLM cost

| Drive               |   LLM calls per run | Prompt tokens per call   | Reply tokens per call   | Settings parsed   | Seconds per call   | LLM minutes per run   |
|:--------------------|--------------------:|:-------------------------|:------------------------|:------------------|:-------------------|:----------------------|
| ETH                 |                  18 | 1248.07 ± 5.45           | 515.72 ± 16.44          | 90 %              | 13.15 ± 0.38       | 3.94 ± 0.11           |
| iNav-WHU playground |                  18 | 1150.83 ± 4.02           | 465.63 ± 21.50          | 92 %              | 11.97 ± 0.55       | 3.59 ± 0.17           |
| iNav-WHU street     |                  18 | 1156.59 ± 1.89           | 477.39 ± 7.00           | 90 %              | 12.24 ± 0.20       | 3.67 ± 0.06           |

## Condition detector (seed 0)

| Drive               | Agreement, test part   | Agreement, initialization   |   Onset delay, 5 m (s) |   Onset delay, 15 m (s) |   Without trigger, 15 m (s) |
|:--------------------|:-----------------------|:----------------------------|-----------------------:|------------------------:|----------------------------:|
| ETH                 | 99.1 %                 | 98.9 %                      |                      1 |                       1 |                          11 |
| iNav-WHU playground | 97.1 %                 | 96.5 %                      |                      5 |                       4 |                           9 |
| iNav-WHU street     | 97.6 %                 | 96.9 %                      |                      7 |                       6 |                          13 |
