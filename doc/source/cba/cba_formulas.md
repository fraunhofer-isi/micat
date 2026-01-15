---
# © 2025, 2026 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

title: Energy mix and how it's calculated within the MICATool
license: AGPL
---

<!--
© 2024, 2025 Fraunhofer-Gesellschaft e.V., München

SPDX-License-Identifier: AGPL-3.0-or-later
-->

To resolve the issue with not all data across measures' lifetime being available, the tool's CBA facility should be based on weighted average annuities. This requires a number of changes, compared to the previous version of the CBA (#493).

Calculation of intermediate results
=

The calculation of annuity relies on new annual savings and total investments. The relevant calculcation for new annual savings is described in #339. 

Constant indicators
-

First of all, all constant indicators need to be scaled:

$\Delta MI_{m,i} = \sum_{k} MI_{m,i,k} / \Delta E_{m,i} \cdot N \Delta E_{m,i}$

$\Delta MI_{m,i}$ = scaled indicators for measure $`m`$ in stated year $`i`$

$`MI_{m,i,k}`$ = result of indicator $`k`$ for measure $`m`$ in stated year (Stützjahr) $`i`$

$`\Delta E_{m,i}`$ = total annual savings for measure $`m`$ in stated year (Stützjahr) $`i`$, as input in the front end

$`N \Delta E_{m,y}`$ = new annual savings for measure $`m`$ in year $`y`$ (after interpolation, #521), as input in the front end

Relevant constant indicators are the following ones:
* Energy cost savings
* Premature deaths due to air pollution
* Avoided lost working days
* Reduction of greenhouse gas emissions
* Impact on RES targets
* Avoided asthma cases
* Avoided cold winter mortality

One-time impacts
-

In contrast, one-time impacts such as new annual investments (as calculated in #339) or GDP need to be discounted, using the capital recovery factor $`CRF_m`$:

$`dI_{m,i} = I_m \cdot CRF_m = I_m \cdot \frac{DR (1 + DR)^{LT_m}}{(1 + DR)^{LT_m} - 1}`$

$`dI_{m,i}`$ = discounted annual new investments

$`I_{m,i}`$ = annual new investments, as calculated in #339

$`DR`$ = discount rate, as implemented in slider in CBA

$`LT`$ = measure lifetime, coming from id_parameter 36 or advanced parameters

Annuity calculation
=

Annuity 
-

The annuity $`A_{m,i}`$ describes the revenue or cost of a measure in stated year $`i`$:

$`A_{m,i} = dI_{m,i} - dGDP_{m,i} - \Delta MI_{m,i}`$

$`dGDP_{m,i}`$ = discounted effect on GDP, calculation analogous to $`dI_m`$

$`MI_{m,i}`$ = monetised impacts of constant indicators

Weighted annuity
-

In order to combine the calculated annuity for every stated year, a weighting using the energy savings implemented since the last stated year is carried out, resulting in a weighted annuity $`A_m`$:

$`A_m = [\sum_i (A_{m,i} \cdot \sum_{y = y(i-1)+1}^{y(i)} N \Delta E_{m,y})] / \sum_y N \Delta E_{m,y}`$

$`\sum_{y = y(i-1)+1}^{y(i)} N \Delta E_{m,y}`$ = sum of all new annual savings implemented between one year after the last stated year $`y(i-1)+1`$ and this stated year $`y(i)`$

$`\sum_y N \Delta E_{m,y}`$ = total sum of all new annual savings of the measure

Other CBA aspects
=

As was the case before, the slider for discount rate adjusts the discount rate (relevant for the discounting of one-time impacts). The sliders for energy price and investment sensitivity are multipliers for energy costs and discounted investments, respectively.