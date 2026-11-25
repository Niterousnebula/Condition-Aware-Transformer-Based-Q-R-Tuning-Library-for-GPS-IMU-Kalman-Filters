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
