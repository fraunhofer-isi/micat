---
title: Energy mix and how it's calculated within the MICATool
license: AGPL
---

<!--
© 2024, 2025 Fraunhofer-Gesellschaft e.V., München

SPDX-License-Identifier: AGPL-3.0-or-later
-->

Energy mix and how it's calculated
============

Generally, the energy mix describes of which energy carriers and to which shares
a total energy quantity is constituted. 
In the MICATool, a differentiation is made between final energy consumption (FEC, energy consumed by end users)
and its relevant carriers, and primary energy consumption (PEC, total energy entering the system)
and its relevant carriers.

Final energy carriers
-----

In order to simplify the gathering of data, the final energy carriers have been grouped 
into 7 main groups, shown in the table below:

| **Id** | **Label**         | **Description**          |
|--------|-------------------|--------------------------|
| **1**  | Electricity       | Electricity              |
| **2**  | Oil               | Oil                      |
| **3**  | Coal              | Coal                     |
| **4**  | Gas               | Gas                      |
| **5**  | Biomass And Waste | Biomass And Waste        |
| **6**  | Heat              | District Heating And CHP |
| **7**  | H2 And E\-Fuels   | H2 And Synthetic Fuels   |

This table is from back_end/import/public/id_final_energy_carriers.xlsx.
Details about the mapping of energy carriers to these groups can be found in
back_end/import/public/mapping__final_energy_carrier__primary_energy_carrier.xlsx.

Primary energy carriers
-----

The primary energy carriers have been grouped into 6 overarching energy carrier types:

| **Id** | **Label**                   | **Description**                                       |
|--------|-----------------------------|-------------------------------------------------------|
| **1**  | Oil                         | Oil \(incl\. Biodiesel\)                              |
| **2**  | Coal                        | Coal                                                  |
| **3**  | Gas                         | Gas \(incl\. Biogas\)                                 |
| **4**  | Biomass And Renewable Waste | Biomass And Non\-Renewable Waste                      |
| **5**  | Renewables                  | PV, Wind, Geothermal, Tidal, Etc                      |
| **6**  | Other                       | Other \(incl\. Nuclear, Non\-Renewable Waste, etc\.\) |


This table is from back_end/import/public/id_primary_energy_carriers.xlsx.
Details about the mapping of energy carriers to these groups can be found in
back_end/import/public/mapping__final_energy_carrier__primary_energy_carrier.xlsx.

Given the fact that electricity, heat, and H2 and synthetic fuels need to be generated
from primary energy carriers (see Chapter below), they are not listed among 
primary energy carriers in the table above. However, since H2 and heat can and often are generated from electricity, the id_primary_energy_carrier table includes an id = 7 for electricity, which is used in the conversion process.

Conversion of final to primary energy consumption
-----

Since some indicators need values in primary and not final energy consumption, a module
in the MICATool converts these values.

Final energy carrier groups that are also existent among primary energy carriers 
(oil, coal, gas, biomass and renewable waste) are allocated to that category. For 
now, no factor accounts for the transformation of these products between primary
and final energy consumption.

| Energy carrier| id_final_energy_carrier | id_primary_energy_carrier |
| ------ | ------ | ------ |
| Oil | 2 | 1 |
| Coal | 3 | 2 |
| Gas | 4   | 3 |
| Biomass | 5 | 4 |

The conversion of final energy carriers H2, heat, and electricity includes two steps: the allocation to primary energy carriers (and electricity), from which they are generated and calculating the necessary inputs to generate the energy considering plants' efficiency.
The process is implemented as a cascade through the three relevant final energy carriers and starts with the allocation and conversion of hydrogen, then heat, and finally electricity. This is due to the fact, that both hydrogen and heat might be generated from electricity, which then has to be converted into its sources.

Thus, the final energy savings attributed to one of these three energy carriers are first multiplied with the relevant generation mix, which describes the share of each primary energy carrier (and electricity) in the generation of the respective final energy carrier. Then, to account for conversion losses, each resulting value has to be divided by the related conversion efficiency from primary energy carrier (or electricity) to the respective final energy carrier to get primary energy savings while also accounting for transformation losses.

Given the available data from the EU Reference Scenario 2020 for ex-ante evaluations, the inputs to cogeneration power plants are solely allocated to electricity generation. Thus, the input to cogeneration plants is not accounted for in the generation of heat, resulting in heat being accounted as a "free" add-on to the generated electricity. This approach has been chosen, since the ex-ante data available for cogeneration plants does not allow a more detailed allocation of primary energy inputs to electricity and heat generation or even to dedicated electricity and cogeneration power plants. As a consequence, heat from cogeneration is not accounted for in the conversion of final to primary energy consumption. Thus, unless default values are altered, heat savings only affect dedicated heat generation, not cogeneration. This also makes sense, since cogeneration is generally more efficient than dedicated heat generation, so that savings in heat demand should primarily affect the latter.

The input values stem from the Eurostat Complete Energy Balances and from
the EU Reference Scenario 2020.

*The functioning of the FEC-to-PEC-conversion module can be found [here](./FEC_to_PEC.md). Since the calculation has been changed in August 2025, the previous (now obsolete) calculation approach can be found [here](FEC_to_PEC_old.md).*

Calculation of final energy mix
----
If no data is provided by the user, default assumptions are made in order to provide
a plausible energy mix.
When assuming the energy mix affected by improvement actions selectable in the MICATool,
no such data is available across the sectors and subsectors. Instead, energy mixes are 
generally issued by statistical offices or the EU Reference Scenario 2020 per subsector
or end-use, which differs from MICAT's improvement actions. Thus, the tool uses a 
workaround, in order to be able to use the available datasets. 

For each country and combination of sector (or subsector) and improvement action, 
a vector containing a coefficient for each final energy carrier is stored in the database. 
This vector is multiplied elementwise with the sector's (or subsector's) energy mix vector.
After normalising the vector, the improvement action energy mix is obtained.

*The equations behind the multiplication and normalisation are described [here](./lambda_chi.md).*

This process has the benefit of allowing the use of widely available sectoral energy mix
data. Since the coefficient vector is rather time-constant, merely the sectoral data needs
regular updating. Moreover, this allows users to adjust the data to fit their use case by
merely altering sectoral data, which is significantly easier to gather, whether on EU,
national, regional, or local level.

The calculation of the vectors containing the coefficients is done using a combination of
past statistical and scenario data. They are gathered by dividing the improvement actions' 
energy mix by the (sub-)sectoral energy mix, with the data needing to stem from one 
consistent source or scenario. Since some of these sources and scenarios are not public, 
merely the coefficients are stored in the database, not the underlying datasets and scenarios.

*How these vectors of coefficients are calculated is shown [here](./chi_calc.md).*













