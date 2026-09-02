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


Calculation of intermediate results
===================================

The calculation of annuity relies on new annual savings and total investments (see below). In addition, constant and indicators and one-time impacts need to be treated differently for the annuity calculation.


## Calculation of new energy savings

For a cost-benefit-analysis, the new energy savings are necessary, which can be calculated from the interpolated total annual energy savings:

$`N \Delta E_{m, y} = \Delta E_{m, y} - \sum_{i=1}^{LT_{m}} N \Delta E_{m, (y-i)}`$

$`N \Delta E_{m, y}`$ = new additional energy savings

$`\Delta E_{m, y}`$ = total annual energy savings (as coming from the user input) in a given year. This needs to be interpolated for every year after the first entered value. Before the first value, all values are equal to 0.

$`LT_{m}`$ = average lifetime of a measure, either coming from the user template or as default from the database 

## Calculation of new investments

The same needs to be done for investments, although a little simpler:

$`N \Delta inv_{m, y} = \Delta inv_{m, y} - \Delta inv_{m, (y-1)}`$

$`N \Delta inv_{m, y}`$ = new additional investments

$`\Delta inv_{m, y}`$ = total investments (as coming from the user input) in a given year. This needs to be interpolated for every year after the first entered value. Before the first value, all values are equal to 0.

Constant indicators
-------------------

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
----------------

In contrast, one-time impacts such as new annual investments (see above) or GDP need to be discounted, using the capital recovery factor $`CRF_m`$:

$`dI_{m,i} = I_m \cdot CRF_m = I_m \cdot \frac{DR (1 + DR)^{LT_m}}{(1 + DR)^{LT_m} - 1}`$

$`dI_{m,i}`$ = discounted annual new investments

$`I_{m,i}`$ = annual new investments, as calculated in #339

$`DR`$ = discount rate, as implemented in slider in CBA

$`LT`$ = measure lifetime, coming from id_parameter 36 or advanced parameters

Annuity calculation
===================

Annuity
-------

The annuity $`A_{m,i}`$ describes the revenue or cost of a measure in stated year $`i`$:

$`A_{m,i} = dI_{m,i} - dGDP_{m,i} - \Delta MI_{m,i}`$

$`dGDP_{m,i}`$ = discounted effect on GDP, calculation analogous to $`dI_m`$

$`MI_{m,i}`$ = monetised impacts of constant indicators

Weighted annuity
----------------

In order to combine the calculated annuity for every stated year, a weighting using the energy savings implemented since the last stated year is carried out, resulting in a weighted annuity $`A_m`$:

$`A_m = [\sum_i (A_{m,i} \cdot \sum_{y = y(i-1)+1}^{y(i)} N \Delta E_{m,y})] / \sum_y N \Delta E_{m,y}`$

$`\sum_{y = y(i-1)+1}^{y(i)} N \Delta E_{m,y}`$ = sum of all new annual savings implemented between one year after the last stated year $`y(i-1)+1`$ and this stated year $`y(i)`$

$`\sum_y N \Delta E_{m,y}`$ = total sum of all new annual savings of the measure

Other CBA metrics
=================

To increase the scope of the CBA, more CBA metrics are included

Net present value
-----------------

This indicator is similar to annuity, comparing the investments to discounted benefits accruing over the measure's lifetime. $`NPV_m`$ is calculated by dividing the negative annuity $`A_m`$ by the capital recovery factor $`CRF_m`$:

$`NPV_m = - A_m / CRF_m`$

Levelised costs of energy savings
---------------------------------

Levelised costs of a measure $`LCOE_m`$ describe the cost per energy unit, with calculations based on weighted annuity $`A_m`$ :

$`LCOE_m = - \frac{A_m \cdot N_{m,y}}{\sum_y N \Delta E_{m,y}}`$

$`N \Delta E_{m,y}`$ = new annual savings as calculated in #339

$`N_{m,y}`$ = number of years for which new annual savings have been calculated

Levelised costs of carbon dioxide
---------------------------------

This calculation is analogeous to the calculation for LCOE:

$`LCOCO2_m = - \frac{A_m \cdot N_{m,y}}{\sum_y N \Delta CO2_{m,y}}`$

$`N_{m,y}`$ = number of years for which new annual savings have been calculated

$`N \Delta CO2_{m,y}`$ = newly avoided annual emissions, with a calculation analoguous to energy savings in #339 (after interpolation):

$`N \Delta CO2_{m,y} = \Delta CO2_{m, y} - \sum_{i=1}^{LT_{m}} N \Delta CO2_{m, (y-i)}`$

$`\Delta CO2_{m, y}`$ = total annual avoided CO2 emissions, as output by the tool

Cost-benefit ratio
------------------

The $`CBR_m`$ describes the ratio of costs to benefits, with a value below 1 indicating an economically viable investments:

$`CBR_{m,i} = \frac{dI_{m,i} }{ dGDP_{m,i} + \sum_{k} MI_{m,i,k}}`$

$`CBR_m = [\sum_i (CBR_{m,i} \cdot \sum_{y = y(i-1)+1}^{y(i)} N \Delta E_{m,y})] / \sum_y N \Delta E_{m,y}`$

Benefit-cost ratio

The $`BCR_m`$ describes the ratio of costs to benefits, with a value above 1 indicating an economically viable investments. It is the inverse of the CBR:

$`BCR_m = 1 / CBR_m`$


Other CBA aspects
=================

The slider for discount rate adjusts the discount rate (relevant for the discounting of one-time impacts). The sliders for energy price and investment sensitivity are multipliers for energy costs and discounted investments, respectively.
