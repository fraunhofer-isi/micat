---
title: Avoided investments in additional capacity
description: This page shows the equations necessary to calculate avoided investments in additional capacity due to energy efficiency.
license: AGPL
---

<!--
© 2023 - 2024 Fraunhofer-Gesellschaft e.V., München

SPDX-License-Identifier: AGPL-3.0-or-later
-->

Avoided investments in additional capacity
=

```{warning}
This indicator currently shows unexpected behaviour. Until this is fixed, please restrain from using its results!
```

Quantification
-

The indicator "Reduction of additional capacities in grid" belongs to ecologic indicators and is calculated as: 

$\Delta C_{c, t, y} = \Delta E_{c, \rm{el}, y} \cdot r_{c, t, y}$

$\Delta C_{c, t, y} = $  Reduction of additional capacities in grid

$\Delta E_{c, \rm{el}, y} = \Delta E_{c, e=1, y} = $  final energy saving for electricity, id_final_energy_carrier = 1, 
stemming from the [indicator "Energy (cost) savings"](../ecologic_indicators/PEC_FEC_savings.md).

$r_{c, t, y} = $  capacity reduction factor (id_parameter = 47), sources: 
1) ex-post (id_mode = 3,4) : eurostat From 2000 to 2020 (every year): \micat\back_end\import_public\raw_data\eurostat\renewable_energy_system_utilization_eurostat.xlsx
2) ex-ante (id_mode = 1,2) : PRIMES From 2005 to 2050 (every 5 years): \micat\back_end\import_public\raw_data\primes\renewable_energy_system_utilization.xlsx

Monetisation
-

To monetize the reduction of additional capacities in grid, the reduction of additional capacities in grid is multiplied by the technologies' marginal investment prices:

$ M_{\Delta C_{c}} = \sum_t \Delta C_{c, t} \cdot P_{t} $     

$ M_{\Delta C_{c}} = $ monetization of the reduction of additional capacities in grid, unit: euro

$\Delta C_{c, t}$ = reduction of additional capacities in grid, unit: MWh (id_indicator_chart = 17, id_indicator = 23), resulted from the equation above

$P_{t}$ = investment costs of renewable energy system technologies, unit: euro/MWh (id_parameter = 44), source: \micat\back_end\import_public\raw_data\irena\investment_costs_of_renewable_energy_system_technologies.xlsx

$c$ = region in the European Union from table id_region

$t$ = technology from table id_technology