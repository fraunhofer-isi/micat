---
title: Ecologic indicators
description: This page describes the underlying assumptions and data sources for the ecological indicators.
license: AGPL
---

<!--
© 2023 Fraunhofer-Gesellschaft e.V., München

SPDX-License-Identifier: AGPL-3.0-or-later
-->

Social indicators
===

Reduction in energy poverty
-

Building on the [module to assume the number of affected buildings](../modules/N_affected_dwellings.md), the number
of people lifted out of energy poverty is calculated. To assume the share of measures addressing energy poor households,
the national share of energy poverty is used as a default, with the possibility to adjust it in the measure-specific
parameter template. 

The exact methodology and its background are described in length in the [fact sheet](../fact_sheets/energy_poverty.pdf).
The equations used to quantify the number of people lifted out of energy poverty are shown [here](./energy_poverty.md).

Health impacts due to improved indoor climate
-

For now, health impacts linked to improved indoor climate are assessed by looking at the reduction in asthma cases. 
To do so, assumptions regarding the share of renovations occurring in damp and mouldy buildings as well as the share
of renovations constituting medium and deep renovations. As defaults, the projected rates in PRIMES and the current
national prevalence of damp and mould buildings are being used. Finally, a national coefficient describing the number of 
disability-adjusted life years lost per damp or mould building has been calculated from past data as impact factor.

The equations can be found [here](./health_IC.md), the fact sheet can be downloaded as [PDF](../fact_sheets/asthma.pdf).

Mortality due to reduced air pollution
-

The data for the reduction in mortality due to air pollution stems from IIASA, modelled on the basis of the EU Reference 
Scenario 2020. However, these factors are constant (but calculated for each five-year-step) and merely calculated for 
the seven final energy carriers. This entails that a future scenario strongly diverging from the EU Reference Scenario 
2020 still uses the same marginal GHG emission factors. 

Furthermore, given the fact that one coefficient for electricity is calculated for every five years step based on 
the Reference Scenario's assumed energy mix, changes in energy mix stated within the tool are currently not accounted
for in mortality coefficients.

The monetisation is based on the value of statistical life (VSL), with values being published by the WHO. 

The equations can be found [here](./health_AP.md), the fact sheet can be downloaded as [PDF](../fact_sheets/human_health_AP.pdf).

Lost work days due to air pollution
-

Another approach to assess health impacts linked to air pollution is an assessment of avoided lost work days. The data
is also provided by IIASA, again based on the EU Reference Scenario 2020, including the caveats mentioned above.

The monetisation uses the value of a work day provided by the WHO.

The equations, quite similar to the above indicator, are shown on [this page](./lost_work_days.md). The fact sheet can
be downloaded as a PDF from [here](../fact_sheets/human_health_AP.pdf), it is the same one as for the indicator above.