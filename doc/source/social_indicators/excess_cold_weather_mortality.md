---
title: Health effects linked to indoor climate
description: This page shows the equations necessary to calculate the health effects linked to improved indoor climate.
license: AGPL
---

<!--
© 2024 Fraunhofer-Gesellschaft e.V., München

SPDX-License-Identifier: AGPL-3.0-or-later
-->

Avoided excess cold weather mortality due to indoor cold
=

$`\Delta ECWD_{c, m, y} = WDIH_c \cdot N_{c, m, y} \cdot PTF_{c, y} \cdot MDRS_c`$

$`\Delta ECWD_{c, m, y}`$ = avoided excess cold weather deaths linked to indoor climate

$`WDIH_c`$ = excess cold weather deaths attributable to indoor cold per household unable to keep home adequately warm (id_parameter = 26, source: Wuppertal, /public/Wuppertal/health.xlsx)

$`N_{c, m, y}`$ = number of affected buildings (#419)

$`PTF_{c, y}`$ = energy poverty targetedness factor, percentage of improvement actions implemented among energy poor households (id_parameter = 25, table wuppertal_parameters, by default national share of population unable to keep home warm)

$`MDRS_c`$ = share of measures constituting medium and deep renovations (id_parameter = 53, source: Wuppertal, /public/Wuppertal/health.xlsx)

Calculation of $`WDIH_c`$
-

This calculation is done before the import of the data into the database:

$$
WDIH_c = ECWD_c \begin{cases}
    0.1 & \text{if } UKHM_c < 5\% \\ 
    0.2 & \text{if } UKHM_c \geq 5\% \, \& < 10\% \\
    0.3 & \text{if } UKHM_c \geq 10\%  \\
\end{cases} / HUKHW_c
$$

$`ECWD_c`$ = total excess cold weather mortality (Source: Eurostat)

$`UKHM_c`$ = share of population unable to keep home adequately warm (Source: SILC)

$`HUKHW_c`$ = number of households unable to keep home adequately warm (source: SILC)

