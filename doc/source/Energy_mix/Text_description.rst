..This file describes the logic behind the selected energy mixes 
  and how they are calculated

Energy mix
===

Generally, the energy mix describes of which energy carriers and to which shares
 a total energy quantity is constituted. 
 In the MICATool, a differentiation is made between final energy consumption (FEC, energy consumed by end users)
 and its relevant carriers, and primary energy consumption (PEC, total energy entering the system)
 and its relevant carriers.

Final energy carriers
===

In order to simplify the gathering of data, the final energy carriers have been grouped 
into 7 main groups, shown in the table below:

+----+-------------------+--------------------------+
| Id | Label             | Description              |
+====+===================+==========================+
| 1  | Electricity       | Electricity              |
+----+-------------------+--------------------------+
| 2  | Oil               | Oil                      |
+----+-------------------+--------------------------+
| 3  | Coal              | Coal                     |
+----+-------------------+--------------------------+
| 4  | Gas               | Gas                      |
+----+-------------------+--------------------------+
| 5  | Biomass And Waste | Biomass And Waste        |
+----+-------------------+--------------------------+
| 6  | Heat              | District Heating And CHP |
+----+-------------------+--------------------------+
| 7  | H2 And E-Fuels    | H2 And Synthetic Fuels   |
+----+-------------------+--------------------------+

This table is from back_end/import/public/id_final_energy_carriers.xlsx.
Details about the mapping of energy carriers to these groups can be found in
back_end/import/public/mapping__final_energy_carrier__primary_energy_carrier.xlsx.

Primary energy carriers
===

The primary energy carriers have been grouped into 6 overarching energy carrier types:

+----+-----------------------------+--------------------------------------------------+
| Id | Label                       | Description                                      |
+====+=============================+==================================================+
| 1  | Oil                         | Oil (incl. Biodiesel)                            |
+----+-----------------------------+--------------------------------------------------+
| 2  | Coal                        | Coal                                             |
+----+-----------------------------+--------------------------------------------------+
| 3  | Gas                         | Gas (incl. Biogas)                               |
+----+-----------------------------+--------------------------------------------------+
| 4  | Biomass And Renewable Waste | Biomass And Non-Renewable Waste                  |
+----+-----------------------------+--------------------------------------------------+
| 5  | Renewables                  | PV, Wind, Geothermal, Tidal, Etc                 |
+----+-----------------------------+--------------------------------------------------+
| 6  | Other                       | Other (incl. Nuclear, Non-Renewable Waste, etc.) |
+----+-----------------------------+--------------------------------------------------+

This table is from back_end/import/public/id_primary_energy_carriers.xlsx.
Details about the mapping of energy carriers to these groups can be found in
back_end/import/public/mapping__final_energy_carrier__primary_energy_carrier.xlsx.

Given the fact that electricity, heat, and H2 and synthetic fuels need to be generated
from primary energy carriers (see Chapter below), they are not listed among 
primary energy carriers.

Conversion of final to primary energy consumption
===

Since some indicators need values in primary and not final energy consumption, a module
in the MICATool converts these values.

Final energy carrier groups that are also existent among primary energy carriers 
(oil, coal, gas, biomass and renewable waste) are allocated to that category. For 
now, no factor accounts for the transformation of these products between primary
and final energy consumption.

For H2 and synthetic fuels, a conversion from electricity with an efficiency coefficient
is chosen, assuming the national energy mix for electricity generation. Once the 
relevant market has grown in significance, this will be adapted to
account for more ways to produce hydrogen, in all its colours.

The energy quantities of primary energy carriers necessary to generate one energy 
unit of electricity or heat are described in one vector each. These vectors are
calculated taking into account dedicated electricity or heat
generation, as well as cogeneration (CHP). For all dedicated electricity and heat 
generation sources, the total input quantities from the six primary energy carriers are 
divided by the total transformed energy output.

In the case of cogeneration, the complexity lies in the allocation of the inputs to the 
two different outputs. Among the different methods that are used in such cases, an
"equivalence number method" has been chosen. This is mainly due to the fact, that this
approach does not require additional exogenous values or assumptions. It is merely
assumed that the average (national) efficiency of dedicated electricity and heat
generation is improved proportionally for both energy carriers when generated in a
cogeneration process in order to reach the CHP's higher efficiency. 

These two components are weighted with the share of energy generated by dedicated and
cogeneration power plants with the final to primary energy carriers conversion vectors
as result. The input values stem from the Eurostat complete energy balances and from
the EU Reference Scenario 2020.
