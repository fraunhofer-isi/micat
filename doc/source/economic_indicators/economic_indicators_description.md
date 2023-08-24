---
title: Economic indicators
description: This page describes the underlying assumptions and data sources for the economic indicators.
license: AGPL
---

<!--
© 2023 Fraunhofer-Gesellschaft e.V., München

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

The relevant equations are on [this page](./GDP.md), the fact sheet can be found as a PDF [here](../fact_sheets/impact_on_GDP.pdf).

Employment effects
-

Similar to Impact on GDP, Employment effects scale with investments. Thus, similar caveats as described above apply. The
data source is also identical.

The relevant equations are on [this page](./employment_effects.md), the fact sheet can be found as a PDF [here](../fact_sheets/employment_effects.pdf).

Impact on energy intensity
-

The impact on energy intensity indicator compares two cases, a baseline one without the entered savings and one with
these savings. The result from the indicator Impact on GDP is also taken into account in the case with savings.
For ex-ante assessment, the non-energy consumption is currently not subtracted (as shown in the [equations](./energy_intensity.md)), as the EU 
Reference Scenario data does not allow enough disaggregation of the value to use it properly. Since the non-energy 
consumption is orders of magnitude smaller than normal energy consumption and both values are affected similarly, 
the effect should be negligible. We're working on addressing this issue.

You can find the equations [here](./energy_intensity.md), the PDF of the fact sheet is downloadable from [here](../fact_sheets/energy_intensity.pdf).

Asset value of buildings
-


