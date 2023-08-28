---
title: Import dependence
description: This page shows the equations necessary to calculate the impact of energy efficiency on import dependence.
license: AGPL
---

<!--
© 2023 Fraunhofer-Gesellschaft e.V., München

SPDX-License-Identifier: AGPL-3.0-or-later
-->

Import dependence
=

:::{admonition} Warning
This indicator currently shows unexpected behaviour. Until this is fixed, please restrain from using its results!
:::

Impact on import dependence belongs to the economic indicators and is calculated as follows:

$\Delta ID_{pe, y} = ID_{pe, y} - ID_{{\rm S}, pe, y}$

$\Delta ID_{pe, y}$ = impact on import dependence.

$ID_{pe, y}$ = import dependence without savings (see below)

$ID_{{\rm S}, pe, y}$ = import dependence with savings (see below)

Please note that the impact on import dependence is shown in the chart in %-points: 

$\Delta ID_{pe, y} * 100$. 

(=> This is different to a relative difference $-\Delta ID_{pe, y} /ID_{pe, y}$ in % !)


**A.** Import dependence without savings:

$ID_{pe, y} = 1 - \frac{ PP_{pe, y} }{ GAE_{pe, y} - PC_{\rm{NE}, pe, y}}$

$PP_{pe, y}$ = primary energy production mapped to primary energy carriers (id_parameter =1)

$GAE_{pe, y}$ = gross available energy mapped to primary energy carriers (id_parameter=2)

$PC_{\rm{NE}, pe, y}$ = primary energy consumption for non-energy uses mapped to primary energy carriers (id_parameter=3)


**B.** Import dependence with savings:

$ID_{{\rm S}, pe, y} = 1 - \frac{ PP_{pe, y} }{ GAE_{{\rm S}, pe, y} - PC_{{\rm NE}, pe, y}}$

$GAE_{{\rm S}, pe, y} = GAE_{e, y} - \sum_{ss} \sum_{a} \Delta E_{{\rm P}, pe, ss, a, y} $

$GAE_{{\rm S}, pe, y}$ = gross available energy reduced by primary energy savings

$\Delta E_{{\rm P}, pe, ss, a, y}$ = primary energy saving calculated in the [related module](../energy_mix/FEC_to_PEC.md)