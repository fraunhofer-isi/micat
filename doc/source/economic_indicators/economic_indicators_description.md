---
title: Economic indicators
description: This page describes the underlying assumptions and data sources for the economic indicators.
license: AGPL
---

<!--
© 2024 Fraunhofer-Gesellschaft e.V., München

SPDX-License-Identifier: AGPL-3.0-or-later
-->

Economic indicators
===

Impact on GDP
-

Compared to the vast majority of indicators, Impact on GDP requires investments as input. In case it isn't provided, a 
ballpark conversion from energy savings is carried out, although the accuracy severely suffers with this operation.
The coefficients have been provided by e3m and have been calculated from a scenario similar to the EU Reference Scenario
2020 (although not the original one, due to confidentiality issues).

The relevant equations are on [this page](./GDP.md), the fact sheet can be found as a PDF [here](https://micatool.eu/seed-micat-project-wAssets/docs/publications/factsheets/Economic-impact-Impact-on-GDP.pdf).

Employment effects
-

Similar to Impact on GDP, Employment effects scale with investments. Thus, similar caveats as described above apply. The
data source is also identical.

The relevant equations are on [this page](./employment_effects.md), the fact sheet can be found as a PDF [here](https://micatool.eu/seed-micat-project-wAssets/docs/publications/factsheets/Economic-impact-Employment-effects.pdf).

Impact on energy intensity
-

The impact on energy intensity indicator compares two cases, a baseline one without the entered savings and one with
these savings. The result from the indicator Impact on GDP is also taken into account in the case with savings.
For ex-ante assessment, the non-energy consumption is currently not subtracted (as shown in the [equations](./energy_intensity.md)), as the EU 
Reference Scenario data does not allow enough disaggregation of the value to use it properly. Since the non-energy 
consumption is orders of magnitude smaller than normal energy consumption and both values are affected similarly, 
the effect should be negligible. We're working on addressing this issue.

You can find the equations [here](./energy_intensity.md), the PDF of the fact sheet is downloadable from [here](https://micatool.eu/seed-micat-project-wAssets/docs/publications/factsheets/Economic-impact-Energy-Intensity.pdf).

Asset value of buildings
-

The indicator asset value of buildings calculates the increase in value for certain residential and tertiary measures
(listed on the equations page). The approach works with capitalisation rates. These stem from a study by real estate
giant CBRE. However, data was not provided for all countries, so an average of these values was used for the remaining
countries.

Which measures are included and the equations are shown on [this page](./asset_value.md). The fact sheet can be found [here](https://micatool.eu/seed-micat-project-wAssets/docs/publications/factsheets/Economic-impact-Impact-on-the-asset-value-of-commercial-buildings.pdf)

Turnover of energy efficiency goods
-

This indicator is another approach at estimating the value chain effects of energy efficiency (however, only direct 
effects). Compared to the indicator "Impact on GDP", this indicator scales with energy savings directly. The figures
are issued from two large-scale studies, with more details laid out in the fact sheet.

The fact sheet can be downloaded as [PDF](https://micatool.eu/seed-micat-project-wAssets/docs/publications/factsheets/Economic-impact-Turnover-of-energy-efficiency-goods.pdf), the relevant equations are shown 
[here](./turnover_of_EE_goods.md).

Import dependence
-

Import dependence is calculated for the three main fossil fuels: oil, coal, and gas. To do so, a case without savings is
compared with one where the specified savings occur and the difference between both is stated in percentage points. The 
data stems from Eurostat's complete energy balances (ex-post) and the EU Reference Scenario 2020.

More details can be found in the [related equations](./import_dependence.md) and the [fact sheet](https://micatool.eu/seed-micat-project-wAssets/docs/publications/factsheets/Economic-impact-Import-dependency.pdf).

Supplier diversity
-

This indicator relies on the [Herfindahl-Hirschman index](https://en.wikipedia.org/wiki/Herfindahl%E2%80%93Hirschman_index), 
a measure of market concentration. Since PRIMES does not provide any projections for the future supplier landscape of 
fossil fuels, current Eurostat values since the invasion of Ukraine are used for the calculation of ex-ante results, 
whereas past Eurostat figures are used for ex-post examination. Furthermore, the assumption is that energy savings
result in a lower import from the largest supplier.

More details on the methodology are shown on the related [equations page](./supplier_diversity.md) and the [fact sheet](https://micatool.eu/seed-micat-project-wAssets/docs/publications/factsheets/Economic-impacts-Aggregated-energy-security-supply-diversity.pdf).

```{note}
In reality, the assumption that reduced consumption results in an improved supplier diversity or a lower import 
dependence is not always accurate. Instead, the selection of suppliers is less of a political decision but rather a 
result of market decisions following the merit-order principle. The political influence merely lays in the 
facilitation of import by provision of necessary facilities and infrastructure. In the end, other aspects might 
politically still be prioritised, such as lower energy prices or stronger domestic production, with the former often 
contradicting the improvement of supplier diversity (the main reason for one supplier's large share of supply is often
a favourable price). This caveat applies to the two indicators "Import dependence" and "Supplier diversity", both 
indicators' results should thus rather be considered as the potential to reach these targets through energy efficiency, 
not a self-evident consequence.
```

Avoided investments in additional capacity
-

This indicator assesses the effects of energy efficiency on necessary electricity generation capacity. The underlying
assumption is that energy efficiency reduces the need to invest in new renewables capacities, since RES make up for the
largest share of new capacities (and should do in order to reach climate neutrality). The calculation assumes new RES
installations would follow the RES technology mix (solar, onshore wind, and offshore wind) of the past with constant 
shares among these technologies. 

More details about the general methodology and cost assumptions can be found on the related [equations page](./avoided_additional_capacity.md)
and in the [fact sheet](https://micatool.eu/seed-micat-project-wAssets/docs/publications/factsheets/Economic-impact-Avoided-additional-energy-generation-capacity.pdf).