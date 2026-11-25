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
