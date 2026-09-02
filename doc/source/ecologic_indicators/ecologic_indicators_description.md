---
# © 2025, 2026 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

title: Ecologic indicators
description: This page describes the underlying assumptions and data sources for the ecologic indicators.
license: AGPL
---

<!--
© 2024, 2025 Fraunhofer-Gesellschaft e.V., München

SPDX-License-Identifier: AGPL-3.0-or-later
-->

Ecologic indicators
===

The MICATool covers a range of ecologic (or environmental) indicators, for each a fact sheet has been
written. The fact sheets cover details about background of the indicator, quantification, methodological
challenges, monetisation, etc. This page explains the assumptions and data sources that have been used, while
also linking to the relevant equations.

Energy savings
-

The calculation of energy savings mainly relies on the [calculation of the energy mix](../energy_mix/lambda_chi.md) and
the [conversion from final to primary energy savings](../energy_mix/FEC_to_PEC.md). Relevant key assumptions are described 
on the related page on the constitution of the [energy mix in the MICATool](../energy_mix/energy_mix_description.md). 

Although the energy savings are shown in primary energy savings, the calculation of saved energy costs relies on final
energy savings. These are multiplied with sector-dependent energy prices issued from the Enerdata database (However,
not all subsectors-energy carrier-combinations are available, so some values have been used for other combinations, in 
line with expected prices). Since this database is neither public nor does it allow the publication of values, these 
values are kept in the confidential database.

Here are the equations for the [quantification](./PEC_FEC_savings.md) and the [monetisation](./energy_cost.md). 
The fact sheet is available as a [PDF](https://micatool.eu/seed-micat-project-wAssets/docs/publications/factsheets/Environmental-impact-Energy-cost-savings.pdf).

Impact on RES targets
-

Energy savings have an impact on Renewables Energy Source (RES) targets, which are defined in the Renewable Energy Directive (RED), by reducing the total consumption. These RES targets are specified as share of total national consumption.

The main assumption for this indicator is that energy savings merely displace fossil fuels in the energy generation. 
Assuming that savings occur proportionally to energy carriers' prevalence in the energy mix would have resulted in them not contributing at all to RES targets.
The reality effectively lies between those two approaches, with savings predominantly but not exclusively replacing fossil fuels. Thus, this indicator can be read as the potential to better reach RES targets utilising energy efficiency.

The equations can be found [here](./impact_res_targets), whereas the fact sheet can be downloaded as a [PDF](https://micatool.eu/seed-micat-project-wAssets/docs/publications/factsheets/Environmental-impact-impacts-on-RES-targets.pdf).

Greenhouse gas savings
-

Greenhouse gas emission (GHG) calculations rely on data from IIASA, modelled on the basis of the EU Reference 
Scenario 2020. However,these factors are constant and merely calculated for the seven final energy carriers. 
This entails that a future scenario strongly diverging from the EU Reference Scenario 2020 still uses the same 
marginal GHG emission factors. 

Furthermore, given the fact that one coefficient for electricity is calculated for every five years step based on 
the Reference Scenario's assumed energy mix, changes in energy mix stated within the tool are currently not accounted
for in GHG calculations.

The monetisation uses the societal costs of carbon, taking costs for the environment and citizens (for instance in 
terms of health) into account. These are provided by the German Federal Environmental Agency.

The equations can be found [here](./reduction_GHG.md), whereas the fact sheet can be downloaded as a [PDF](https://micatool.eu/seed-micat-project-wAssets/docs/publications/factsheets/Environmental-impact-GHG-savings-savings-of-direct-carbon-emissions.pdf).

Reduction in air pollutants
-

The calculation of air pollutants is identical to GHG savings. Thus, the same caveats apply as well. However, the
monetisation of air pollutants takes place within the indicator "Health effects due to air pollution".

The equations can be found [here](./reduction_AP.md), whereas the fact sheet can be downloaded as a [PDF](https://micatool.eu/seed-micat-project-wAssets/docs/publications/factsheets/Social-impact-Human-health-due-to-reduced-air-pollution.pdf).

## Net land use change

The land use indicator assesses the net land use effect of expanding renewable energy generation.
It captures both the additional land required for new RE installations (direct land use, such as turbine
foundations or PV arrays, and indirect land use, such as raw material extraction or component
manufacturing) and the land use avoided through the displacement of conventional fossil and nuclear
generation.

Land use intensities, expressed in m² per MWh, are derived from the scientific literature and multiplied
by the annual RE generation resulting from the user's capacity, country, and commissioning date
inputs, informed by a capacity factor based on PRIMES data. The avoided land use from displaced
primary fuels is calculated analogously, using land use intensities for conventional power plants. The
net land use change is the difference between the two.

The indicator is quantified for photovoltaics (rooftop and utility-scale), wind (onshore and offshore),
hydropower (reservoir and run-of-river), geothermal, biomass and waste, solar thermal, heat pumps,
and hydrogen power plants. It is expressed solely in physical terms (m²), as land procurement costs
are already included in investment costs and fuel prices, and monetisation would therefore constitute
double counting.

The equations used to quantify the net land use change are shown [here](./land_use.md). The fact sheet can be
downloaded as [PDF](https://micatool.eu/seed-micat-project-wAssets/docs/publications/factsheets/seed-micat-factsheets-finalised/SEED-MICAT-Environmental-impacts-Impact-on-land-use-1.pdf).

## Material demand

Building on a review of the scientific literature on critical raw materials (CRM) used in renewable
energy (RE) technologies, the MICATool estimates the quantity of raw materials required for a given
expansion of RE capacity. Material intensity values, expressed in kg per MW of installed capacity, are
derived for each RE technology and multiplied by the user-defined capacity to determine the total
material demand in tonnes.

The selection of materials follows the EU's Critical Raw Materials list (European Commission, 2023).
Not all listed materials are included, either because they are not used in the RE technologies covered
by SEED MICAT, or because no reliable material intensity data could be identified in the literature.
Structural materials such as steel or concrete are excluded, as the focus lies on materials whose
supply may constrain RE deployment.

The indicator is quantified for photovoltaics (rooftop and utility-scale), wind (onshore and offshore),
hydro, geothermal, biomass and waste, heat pumps, and hydrogen power plants. There is no
monetisation approach for material demand, as this would lead to double counting with the investment
costs of RE technologies, which already reflect material expenses.

The equations used to quantify material demand are shown [here](../economic_indicators/Material_demand_and_supply_risk.md). The fact sheet can be downloaded
as [PDF](https://micatool.eu/seed-micat-project-wAssets/docs/publications/factsheets/seed-micat-factsheets-finalised/SEED-MICAT-Environmental-impacts-critical-raw-materials-1.pdf).



