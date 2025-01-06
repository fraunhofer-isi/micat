---
title: The indices in the MICATool
description: This page describes the different indices used in the characterisation and coding of the MICATool.
license: AGPL
---

<!--
© 2024 - 2025 Fraunhofer-Gesellschaft e.V., München

SPDX-License-Identifier: AGPL-3.0-or-later
-->

The indices in the MICATool
====

The MICATool assesses Multiple Impacts for different contexts, which are differentiated
within equation using indices. This section shortly describes these indices, which are
shown in the overview table below:

| **Index** | **Label**                    | **Description**                                              |
|-----------|------------------------------|--------------------------------------------------------------|
| **c**     | id\_region                   | Member States or EU27\_2020                                  |
| **y**     | year                         | Years                                                        |
| **s**     | id\_sector                   | Main sectors                                                 |
| **ss**    | id\_subsector                | Main sectors & subsectors                                    |
| **a**     | id\_action\_type             | Improvement actions                                          |
| **m**     | id\_measure                  | ID attributed to a front\-end row \(representing a measure\) |
| **e**     | id\_final\_energy\_carrier   | Final energy carriers                                        |
| **pe**    | id\_primary\_energy\_carrier | Primary energy carriers                                      |
| **i**     | id\_indicator                | Indicators                                                   |
| **p**     | id\_parameter                | Parameters                                                   |


id_region
-
  
The MICATool is built to assess multiple impacts on three levels: EU, national, and local/regional level. 
For the EU and the national level, different ids are attributed, in order to make them distinguishable. 
However, given the mostly unavailable data on the local level, the latter is using scaled data from the 
national level. Thus, the national id is used for regions and urban areas in any given country. 

<details>
<summary>See the id_region table</summary>

| **Id** | **Label**      | **Description** |
|--------|----------------|-----------------|
| **0**  | European Union | EU27\_2020      |
| **1**  | Austria        | AT              |
| **2**  | Belgium        | BE              |
| **3**  | Cyprus         | CY              |
| **4**  | Czech Republic | CZ              |
| **5**  | Germany        | DE              |
| **6**  | Denmark        | DK              |
| **7**  | Estonia        | EE              |
| **8**  | Greece         | EL              |
| **9**  | Finland        | FI              |
| **10** | France         | FR              |
| **11** | Croatia        | HR              |
| **12** | Hungary        | HU              |
| **13** | Ireland        | IE              |
| **14** | Italy          | IT              |
| **15** | Latvia         | LV              |
| **16** | Lithuania      | LT              |
| **17** | Luxembourg     | LU              |
| **18** | Malta          | MT              |
| **19** | Netherlands    | NL              |
| **20** | Poland         | PL              |
| **21** | Portugal       | PT              |
| **22** | Slovakia       | SK              |
| **23** | Slovenia       | SI              |
| **24** | Spain          | ES              |
| **25** | Sweden         | SE              |
| **26** | Romania        | RO              |
| **27** | Bulgaria       | BG              |

*This table is from back_end/import/public/id_region.xlsx*

</details>

year
-

The tool calculates multiple impacts for certain years or projections of more 
than one timeslice. Thus, the majority of parameters and data are different
for different years. However, not all values are available for each year. 
Therefore, in order to avoid unfounded assumptions, missing values are inter- 
and extrapolated linearly. 

An issue is the inconsistency of the underlying baseline before and after 2020,
which stem from Eurostat and the EU Reference Scenario 2020, respectively. In 
order to avoid statistical artifacts at the crossover of both baselines, two
separated baselines have been defined. The ex-post baseline based on Eurostat 
allows assessments from 2000 to 2020, whereas the ex-ante baseline allows 
calculations from 2015 to 2050, using EU Reference Scenario 2020 data.

id_sector and id_subsector
-

The MICATool covers all end use sectors: agriculture, residential, tertiary, 
industry, and transport sector. These are listed in the id_sector-table. Given 
their significant variety, industry and transport have further been disaggregated 
into subsectors, in order to provide better default data and assumptions. 
As a result, an id_subsector-table containing the five main sectors as well as the 
subsectors for industry and transport has been created. In the case of the main 
sectors industry and transport, the average values for the whole sector are stored.
This is clarified by their name, with all main sectors' label starting with
"average", i.e. "average industry". Hence, despite the name, id_subsector also
includes main sectors.

<details>
<summary>See the id_sector table</summary>

| **Id** | **Label**   | **Description** |
|--------|-------------|-----------------|
| **1**  | Agriculture | Agriculture     |
| **2**  | Industry    | Industry        |
| **3**  | Tertiary    | Tertiary        |
| **4**  | Residential | Residential     |
| **5**  | Transport   | Transport       |

*This table is from back_end/import/public/id_sector.xlsx*

</details>

<details>
<summary>See the id_subsector table</summary>

| **Id** | **Label**                            | **Description**                      |
|--------|--------------------------------------|--------------------------------------|
| **1**  | Average Agriculture                  | Agriculture, Forestry & Fishing      |
| **2**  | Average Industry                     | Average Industry Sector              |
| **3**  | Iron & Steel                         | Iron & Steel                         |
| **4**  | Chemical & Petrochemical             | Chemical & Petrochemical             |
| **5**  | Non\-Ferrous Metals                  | Non\-Ferrous Metals                  |
| **6**  | Non\-Metallic Minerals               | Non\-Metallic Minerals               |
| **7**  | Transport Equipment                  | Transport Equipment                  |
| **8**  | Machinery                            | Machinery                            |
| **9**  | Mining & Quarrying                   | Mining & Quarrying                   |
| **10** | Food, Beverages & Tobacco            | Food, Beverages & Tobacco            |
| **11** | Paper, Pulp & Printing               | Paper, Pulp & Printing               |
| **12** | Wood & Wood Products                 | Wood & Wood Products                 |
| **13** | Construction                         | Construction                         |
| **14** | Textile & Leather                    | Textile & Leather                    |
| **15** | Not Elsewhere Specified In Industry  | Not Elsewhere Specified In Industry  |
| **16** | Average Tertiary                     | Tertiary Sector                      |
| **17** | Average Residential                  | Residential Sector                   |
| **18** | Average Transport                    | Average Transport Sector             |
| **19** | Rail                                 | Rail                                 |
| **20** | Road                                 | Road                                 |
| **21** | Aviation                             | Domestic Aviation                    |
| **22** | Navigation                           | Domestic Navigation                  |
| **23** | Pipeline                             | Pipeline Transport                   |
| **24** | Not Elsewhere Specified In Transport | Not Elsewhere Specified In Transport |


*This table is from back_end/import/public/id_subsector.xlsx*

*A mapping of subsectors to main sectors can be found in*
*back_end/import/public/mapping__subsector__sector.xlsx*

</details>

id_action_type
-

Since multiple impacts are linked to the implementation of measures,
the MICATool does not work with end uses, which are unspecific in
what exactly is implemented. Instead, improvement actions have been
defined, which group similar measures that create comparable multiple
impacts. The available improvement actions differ across sectors.

<details>
<summary>See the id_action_type table</summary>

| **id** | **label**                   | **description**                                                                                                        |
|--------|-----------------------------|------------------------------------------------------------------------------------------------------------------------|
| **1**  | Building envelope           | Building envelope insulation \(Windows, insulation, etc\)                                                              |
| **2**  | Heating fuel switch         | Heating fuel switch including to district heating                                                                      |
| **3**  | Energy\-efficient heating   | Energy efficiency improvements of heatings \(Boiler upgrade or replacement, pipe insulation, better heaters, etc\.\)   |
| **4**  | Electric appliances         | Electric appliances \(wet & cold appliances, lighting, consumer electronics, air conditioning, etc\.\)                 |
| **5**  | Cooking and water heating   | Cooking and water heating                                                                                              |
| **6**  | Behavioural changes         | Behavioural changes \(i\.e\. thermostat adjustments\)                                                                  |
| **7**  | Behavioural changes         | Organisational or behavioural changes \(i\.e\. thermostat adjustments or energy management systems such as ISO 50001\) |
| **8**  | Cross\-cutting technologies | Energy\-efficient electric cross\-cutting technologies                                                                 |
| **9**  | Process change              | Process change \(fundamental changes to processes\)                                                                    |
| **10** | Fuel switch                 | Fuel switch in existing processes                                                                                      |
| **11** | Process\-specific savings   | Process\-specific savings \(incl\. waste\-heat recovery\)                                                              |
| **12** | Space heating and cooling   | Building envelope as well as space heating and cooling measures                                                        |
| **13** | Consumption reduction       | Consumption reduction of vehicles \(low\-resistance tyres, side\-boards on trucks, fuel additives, etc\.\)             |
| **14** | Modal shift                 | Modal shift \(Freight/passenger\)                                                                                      |
| **15** | Behavioural changes         | Behavioural or driving changes \(either autonomous or through regulations such as speed limits\)                       |
| **16** | Emission thresholds         | Emission thresholds                                                                                                    |
| **17** | Fuel switch                 | Fuel switch in vehicles \(within the same mode of transport\)                                                          |

*This table is from back_end/import/public/id_action_type.xlsx*

*A mapping of improvement actions to subsectors can be found in*
*back_end/import/public/mapping__subsector__action_type.xlsx*

</details>

id_measure
-

This id describes a row in the front-end, so a combination of (sub-)sector, improvement action, values, and optionally parameters. The id is mainly used during coding to unambiguously identify a front end row
and thereby, precisely attribute results to a certain measure.

id_final_energy_carrier
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

*This table is from back_end/import/public/id_final_energy_carriers.xlsx*

*Details about the mapping of energy carriers to these groups can be found in*
*back_end/import/public/mapping__final_energy_carrier__primary_energy_carrier.xlsx*

id_primary_energy_carrier
-----

The primary energy carriers have been grouped into 6 overarching energy carrier types:

| **Id** | **Label**                   | **Description**                                       |
|--------|-----------------------------|-------------------------------------------------------|
| **1**  | Oil                         | Oil \(incl\. Biodiesel\)                              |
| **2**  | Coal                        | Coal                                                  |
| **3**  | Gas                         | Gas \(incl\. Biogas\)                                 |
| **4**  | Biomass And Renewable Waste | Biomass And Non\-Renewable Waste                      |
| **5**  | Renewables                  | PV, Wind, Geothermal, Tidal, etc.                     |
| **6**  | Other                       | Other \(incl\. Nuclear, Non\-Renewable Waste, etc\.\) |


*This table is from back_end/import/public/id_primary_energy_carriers.xlsx*

*Details about the mapping of energy carriers to these groups can be found in*
*back_end/import/public/mapping__final_energy_carrier__primary_energy_carrier.xlsx*

Given the fact that electricity, heat, and H2 and synthetic fuels need to be generated
from primary energy carriers (see Chapter below), they are not listed among 
primary energy carriers.

id_indicator
-

The indicators identified and developed within the MICAT project have been gathered in
the id_indicator table. However, the lists also includes obsolete or not yet developed 
indicators. Moreover, some indicators can merely be quantified, not monetised, mainly
about missing underlying data. The indicators are also categorised into social, economic,
and environmental (or ecologic) indicators, a categorisation which can also be seen in
the subdivision of graphs in the front end.

<details>
<summary>See the id_indicator table</summary>

| **Id** | **Label**   | **Description** |
|--------|-------------|-----------------|
| **1**  | Agriculture | Agriculture     |
| **2**  | Industry    | Industry        |
| **3**  | Tertiary    | Tertiary        |
| **4**  | Residential | Residential     |
| **5**  | Transport   | Transport       |

*This table is from back_end/import/public/id_indicator.xlsx*

*Details about the mapping of indicators to social, economic, and ecologic indicator*
*groups can be found in*
*back_end/import/public/mapping__final_energy_carrier__primary_energy_carrier.xlsx*

</details>

id_parameter
-

The MICATool uses a variety of different datasets to allow for the quantification and
monetisation of multiple impacts, with several more allowing for the
provision of default data, in case users do not have all optional data at hand.
In order to keep these large datasets sorted, every set of values merely 
differentiated by the indices above is assigned to a parameter in the id_parameter
table. As such, the id_parameter template is often altered in the process of improving
existing or adding new indicators.

*The id_parameter table can be found here: back_end/import/public/id_parameter.xlsx*

*Since it is a work-in-progress and changes are frequent, as well as its considerable*
*length, it has not been included here.*
