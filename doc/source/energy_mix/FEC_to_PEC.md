---
# © 2025 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

title: FEC-to-PEC conversion
description: This page contains the equations to convert final energy (FEC) to primary energy consumption (PEC).
license: AGPL
---

<!--
© 2024, 2025 Fraunhofer-Gesellschaft e.V., München

SPDX-License-Identifier: AGPL-3.0-or-later
-->

FEC to PEC conversion
===

Default hydrogen/synthetic fuel generation mix
-

The hydrogen/synthetic fuel generation mix is currently not country-specific, but global. It is assumed that hydrogen and synthetic fuels are generated using the following shares of primary energy carriers: 

| id_primary_energy_carrier | Label                       | Share |
|---------------------------|-----------------------------|-------|
| 1                         | Oil                         | 0.00  |
| 2                         | Coal                        | 0.20  |
| 3                         | Gas                         | 0.75  |
| 4                         | Biomass And Renewable Waste | 0.00  |
| 5                         | Renewables                  | 0.00  |
| 6                         | Other                       | 0.00  |
| 7                         | Electricity                 | 0.05  |

This table is from /import/raw_data/fraunhofer/hydrogen_synthetic_fuels_generation.xlsx.

Default heat generation mix
-

From the Eurostat Complete Energy Balances [nrg_bal_c] (download already implemented, but for other data), download [nrg_bal] : [GHP_MAPH] & [GHP_APH].

Add up the two tables index-wise (so that only values with the exactly same indeces are added). Map them using import/raw_data/eurostat/mapping__siec__energy_carrier.xlsx to id_primary_energy_carrier (one of the two columns).

Then, calculate the share of each of the 7 primary energy carriers compared to the total of all 7:

$`k_{{\rm heat}, c, pe, y} = \frac{E_{\rm{heat}, c, pe, y}}{\sum_{pe} E_{\rm{heat}, c, pe, y}}`$

with $`k_{{\rm heat}, c, pe, y}`$ being the heat coefficient (id_parameter = 20) for a given country _c_, primary energy carrier _pe_, and year _y_ and $`E_{\rm{heat}, c, pe, y}`$ the heat generated from primary energy carrier _pe_ ([GHP_MAPH] + [GHP_APH]).

Default electricity generation mix
-

From the Eurostat Complete Energy Balances [nrg_bal_c] (already implemented, but for other data), download [nrg_bal] : [GEP].

Map the table using import/raw_data/eurostat/mapping__siec__energy_carrier.xlsx to id_primary_energy_carrier (one of the two columns).

Then, calculate the share of each of the 7 primary energy carriers compared to the total of all 7:

$`k_{{\rm elec}, c, pe, y} = \frac{E_{\rm{elec}, c, pe, y}}{\sum_{pe} E_{\rm{elec}, c, pe, y}}`$

with $`k_{{\rm elec}, c, pe, y}`$ being the electricity coefficient (id_parameter = 21) for a given country _c_, primary energy carrier _pe_, and year _y_ and $`E_{\rm{elec}, c, pe, y}`$ the electricity generated from primary energy carrier _pe_ ([GEP]).

The tables for heat and electricity generation mix can be combined, using their id_final_energy_carrier (elec = 1, heat = 6). For ex-ante analysis, analogous but confidential tables from the EU Reference Scenario 2020 are used instead (with data stored in the confidential database).

Import conversion efficiency data
-

The data on conversion efficiency is in the table /import/raw_data/fraunhofer/conversion_efficiency.xlsx. The data is not country-specific, but global. It contains the conversion efficiencies from primary energy carriers to final energy carriers electricity (id_final_energy_carrier = 1), heat (id_final_energy_carrier = 6), and hydrogen/synthetic fuels (id_final_energy_carrier = 7). The efficiency values for electricity and heat stem from the PRIMES Technology Assumptions (https://circabc.europa.eu/ui/group/8f5f9424-a7ef-4dbf-b914-1af1d12ff5d2/library/336c6844-6ee8-4861-91e9-7e86107c35ad/details?download=true), whereas the figures for H2 come from the Hydrogen Analysis Resource Center (https://h2tools.org/hyarc/hydrogen-data/hydrogen-production-energy-conversion-efficiencies).

Rewire primary energy saving calculation
=

This script is necessary to convert final energy savings to primary energy savings. Some energy carriers can merely be remapped (oil, coal, gas, biomass and waste; $`\Delta E_{{\rm map}, c, pe, y}`$). Others need to be converted (electricity, heat, hydrogen and synthetic fuels; $`\Delta E_{{\rm con}, c, pe, y}`$). 

Remapping energy carriers
-

The savings from the final energy carriers oil, gas, coal, and biomass and waste can be carried over into primary energy savings, by remapping them accordingly:

| Energy carrier| id_final_energy_carrier | id_primary_energy_carrier |
| ------ | ------ | ------ |
| Oil | 2 | 1 |
| Coal | 3 | 2 |
| Gas | 4   | 3 |
| Biomass | 5 | 4 |

This mapping is also available under import/raw_data/mapping__final_energy_carrier__primary_energy_carrier.xlsx.

_The conversion process should start with the conversion of hydrogen, then heat, and finally electricity. This is due to the fact, that for both hydrogen and heat conversion electricity might be used, which then has to be converted into its sources._

Conversion of hydrogen/synthetic fuel
-

All energy savings attributed to id_final_energy_carrier = 7 (id_fec7) need to be allocated to primary energy carriers and electricity. This is done by multiplying the energy savings for id_fec7 with the values in the imported hydrogen_synthetic_fuels_generation. Then, to account for conversion losses, each resulting value has to be divided by the related value from the table conversion_efficiency table:

$`\Delta E_{\rm{H2}, c, pe, y} = \Delta E_{c, e=7, y} \cdot \lambda_{\rm{H2}, pe, y} / \eta_{e=7, pe, y}`$

$`\Delta E_{\rm{H2}, c, pe, y}`$ = primary energy savings for primary energy carrier _pe_, in country _c_, and year _y_.

$`\Delta E_{c, e=7, y}`$ = final energy savings of hydrogen in country _c_ and year _y_.

$`\lambda_{\rm{H2}, pe, y}`$ = share of primary energy carrier _pe_ in generation of hydrogen in year _y_.

$`\eta_{e=7, pe, y}`$ = conversion efficiency from primary energy carrier _pe_ to final energy carrier = 7 (hydrogen) in year y.

Conversion of heat
-

All energy savings attributed to id_final_energy_carrier = 6 (id_fec6) need to be allocated to primary energy carriers and electricity. This is done by multiplying the energy savings for id_fec6 with the values in the table created above for electricity and heat generation mix. Then, to account for conversion losses, each resulting value has to be divided by the related value from the table conversion_efficiency table:

$`\Delta E_{\rm{heat}, c, pe, y} = \Delta E_{c, e=6, y} \cdot \lambda_{c, e=6, pe, y} / \eta_{e=6, pe, y}`$

$`\Delta E_{\rm{heat}, c, pe, y}`$ = primary energy savings for primary energy carrier _pe_, in country _c_, and year _y_.

$`\Delta E_{c, e=6, y}`$ = final energy savings of heat in country _c_ and year _y_.

$`\lambda_{c, e=6, pe, y}`$ = share of primary energy carrier _pe_ in generation of heat in country _c_ and year _y_.

$`\eta_{e=6, pe, y}`$ = conversion efficiency from primary energy carrier _pe_ to final energy carrier = 6 (heat) in year y.

Conversion of electricity
-

All electricity savings need to be converted to primary energy carriers now: this includes final energy savings attributed to id_final_energy_carrier = 1 (id_fec1, $`\Delta E_{c, e=1, y}`$), as well as electricity savings from avoided hydrogen and heat generation calculated above:

$`\Delta E_{\rm{elec tot}, c, y} = \Delta E_{c, e=1, y} + \Delta E_{\rm{H2}, c, pe=7, y} + \Delta E_{\rm{heat}, c, pe=7, y}`$

This is done by multiplying the energy savings for id_fec1 with the values in the table created above for electricity and heat generation mix. Then, to account for conversion losses, each resulting value has to be divided by the related value from the table conversion_efficiency table:

$`\Delta E_{\rm{elec}, c, pe, y} = \Delta E_{\rm{elec tot}, c, y} \cdot \lambda_{c, e=1, pe, y} / \eta_{e=1, pe, y}`$

$`\Delta E_{\rm{elec}, c, pe, y}`$ = primary energy savings for primary energy carrier _pe_, in country _c_, and year _y_.

$`\Delta E_{c, e=1, y}`$ = final energy savings of electricity in country _c_ and year _y_.

$`\lambda_{c, e=1, pe, y}`$ = share of primary energy carrier _pe_ in generation of electricity in country _c_ and year _y_.

$`\eta_{e=1, pe, y}`$ = conversion efficiency from primary energy carrier _pe_ to final energy carrier = 1 (electricity) in year y.

Summing up all primary energy savings
-

Finally, the sum of all these conversions and remappings gives us the primary energy savings:

$`\Delta E_{c, pe, y} = \Delta E_{{\rm map}, c, pe, y} + \Delta E_{{\rm con}, c, pe, y} = \Delta E_{{\rm map}, c, pe, y} + \Delta E_{{\rm H2}, c, pe, y} + \Delta E_{{\rm heat}, c, pe, y} + \Delta E_{{\rm elec}, c, pe, y}`$