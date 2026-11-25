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
