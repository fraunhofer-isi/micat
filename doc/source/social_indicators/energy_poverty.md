---
title: Energy poverty alleviation
description: This page shows the equations necessary to calculate the reduction in energy poverty.
license: AGPL
---

<!--
© 2024 Fraunhofer-Gesellschaft e.V., München

SPDX-License-Identifier: AGPL-3.0-or-later
-->

Energy poverty
===

**Note 1:** The indicator merely applies to subsector = 17 (Average residential)

**Note 2:** The vast majority of mentioned data can be imported from wuppertal/energy_poverty.xlsx in the public import folder.
The sheet names are the id_parameter (from 25 to 36 excluding 26).

**Note 3:** The indicator considers only the id_action_type (1, 2, 3, 4), for the rest it is Zero.

Calculate the number of people lifted out of energy poverty $\Delta EP$
-


$\Delta EP =  N \cdot PTF / 100 \cdot SHH  \cdot
 \left( IF_{owner} \cdot OOR + IF_{tenant} \cdot (1 - OOR) \right)$

$\Delta EP = $ Energy poverty (the number of people lifted out of energy poverty)

$N$ = number of affected dwellings (id_parameter = 45), calculation in the [related module](../modules/N_affected_dwellings.md)

$PTF$ = policy targetedness factor, percentage of improvement actions implemented among energy poor households (id_parameter = 25, table 25_29_30_31_32_33_34_35_energy_poverty_coefficients)  

$SHH$ = average size of energy poor households (id_parameter = 30, table wuppertal_parameters)

$OOR$ = owner-occupier rate among national population (id_parameter = 33, table 25_29_30_31_32_33_34_35_energy_poverty_coefficients)

$IF_{owner/tenant}$ = share of energy poor population affected by a specific measure among owner-occupiers and tenants, respectively. Calculation described below.

Determination of IF (share of energy poor population affected by a specific measure among owner-occupiers and tenants, respectively) 
-

### For id_action_type 1, 2, and 3


The impact factor describes the share of the population in a decile where $`\Delta DI_{tenant/owner}`$ is higher than the decile's $`EPG_{\mathrm{M2}, tenant/owner, d, y}`$:

$`IF = (\rm{number\,of\,deciles\,where\,} \Delta DI > EPG_{\mathrm{M2}, d, y})/10`$

(Could alternatively be calculated as $`(\rm{highest\,decile\,where\,} \Delta DI > EPG_{d, y})/10`$)

$`\Delta DI_{tenant} = ( EC_{ss, a, y} / EQC_{M2} - RRP / 100 \cdot REP ) / N`$

$`\Delta DI_{owner} = ( EC_{ss, a, y} / EQC_{M2} - I_{ss, a, y} / EQC_{M2} / IAL \cdot (100 - SR) / 100 ) / N`$

$`REP`$ = average rent of energy poor households (id_parameter = 29, table 25_29_30_31_32_33_34_35_energy_poverty_coefficients **and** measure specific parameters table, tab residential)

$`RRP`$ = average renovation rent premium as percent of rent (id_parameter = 34, table 25_29_30_31_32_33_34_35_energy_poverty_coefficients **and** measure specific parameters table, tab residential )

$`IAL`$ = lifetitem ("Lifetime of improvement actions", "Average technology lifetime") (id_parameter = 36, table 36_action_lifetime **and** measure specific parameter table, tab main)

$`SR`$ = subsidy rate covered by any given scheme in percent of investments costs (id_parameter = 35, table 25_29_30_31_32_33_34_35_energy_poverty_coefficients)

$`EPG_{\mathrm{M2}, d, y}`$ = energy poverty gap (id_parameter = 27 for owner-occupiers and 28 for tenants, table 27_28_57_58_energy_poverty_gaps)

$`EC_{ss, a, y}`$ = energy cost savings as calculated in #34

$`I_{ss, a, y}`$ = investments for a given row in the front end (id_parameter=40, calculated in #38)

$`EQC_{M2}`$ = OECD equivalence coefficient, in order to convert household expenditures into personal expenditures and account for the lower per capita costs of larger households (id_parameter = 59, source: OECD, table 59_60_M2_2M_equivalence_coefficients)

### For id_action_type 4

The impact factor describes the share of the population in a decile where $`\Delta DI_{tenant/owner}`$ is higher than the decile's $`EPG_{tenant/owner, d, y}`$:

$`IF = (\rm{number\,of\,deciles\,where\,} \Delta DI > EPG_{d, y})/10`$

$`\Delta DI_{tenant/owner, ss, a, y} = (EC_{ss, a, y}/ EQC_{M2} - I_{ss, a, y}/ EQC_{M2} / IAL \cdot (100 - SR) / 100) / N`$

### For other values of id_action_type and other subsectors

$`IF = 0`$