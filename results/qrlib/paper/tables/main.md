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
