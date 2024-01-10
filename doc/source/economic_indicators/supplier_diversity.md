---
title: Supplier diversity
description: This page shows the equations necessary to calculate the impact of energy efficiency on supplier diversity.
license: AGPL
---

<!--
© 2023 - 2024 Fraunhofer-Gesellschaft e.V., München

SPDX-License-Identifier: AGPL-3.0-or-later
-->

Supplier diversity
=

$ \Delta HHI_{c, e, y} = HHI_{c, e, y} - [LS_{c, e, y} + OS_{c, e, y}]$

$ \Delta HHI_{c, e, y}  = $ Change in supplier diversity by energy efficiency impact, unit: unitless

$ HHI_{c, e, y} = $ Supplier diversity, unit: unitless, must be **calculated in the back_end** ,  calculation: [see here](#supplier-diversity)

$LS_{c, e, y} = $ Impact of energy efficiency on largest supplier, unit: unitless **calculation  depends** on the user imput, calculation: [see here](#impact-of-energy-efficiency-on-largest-supplier)

$OS_{c, e, y} = $ Impact of energy efficiency on other suppliers, unit: unitless **calculation depends** on the user imput, calculation: [see here](#impact-of-energy-efficiency-on-other-suppliers)

**Note:** index _e_ is for id_final_energy_carrier and here only includes the values 2 (for oil), 3 (for coal), and 4 (for gas). For other id_final_energy_carrier are not applicable and should not be shown the user.

<a name="Supplier diversity"></a>
Supplier diversity
-

$HHI_{c, e, y} = \Sigma_{pc=1}^{N_{pc}} (\frac{k_{pc} \cdot IE_{c, e, pc, y}}{IE_{c, e, y}})^2 $

$IE_{c, e, y} = \sum_{pc}{IE_{c, e, pc, y}} $

$HHI_{c, e, y} = $ supplier diversity for energy carrier (e) and the region (c) in each year (y), unit: unitless (factor)

$k_{pc} = $ risk coefficient of suppliers , unit: unitless, id_parameter = 52, <a name="source_k"></a>source: \micat\back_end\import_public\raw_data\eurostat\risk_coefficient_of_suppliers.xlsx

$IE_{c, e, pc, y} = $ average monthly imported energy (e) by region (c)  from partner region (pc), and in each year (y), unit: ktoe, id_parameter = 51, <a name="source_IE">source: \micat\back_end\import_public\raw_data\eurostat\average_monthly_imported_energy.xlsx

$IE_{c, e, y} = $ total amount of imported energy, unit: ktoe

<a name="Impact of energy efficiency on largest supplier"></a>
Impact of energy efficiency on largest supplier
-

$LS_{c, e, y} = (k_{1, c, y} \frac{IE_{c, e, y, 1} - \Delta E_{c, e, y}}{IE_{c, e, y} - \Delta E_{c, e, y}})^2$

$LS_{c, e, y}$ = Impact of energy efficiency on largest supplier, unit: unitless

$k_{1, c, e, y} = $ risk coefficient of the largest supplier for each region, unit: unitless, **calculation:** go to the [table](#source_IE) for $ IE_{c, e, pc, y}$, for each year, each id_region, and each id_final_energy_carrier, check which id_partner_region has the largest value. then go to the [table](#source_k) for $k_{pc}$ and take the value for the same id_partner_country that you just have found. This value is the $ k_{1, c, e, y}$

$IE_{c, e, y, 1} = $ amount of imported energy from the largest supplier by region (c), final energy carrier (e), and year (y); unit: ktoe, **calculation:** go to the [table](#source_IE) for $ IE_{c, e, pc, y}$, for each year, each id_region, and each id_final_energy_carrier, check which id_partner_region has the largest value, and take this value as IE_{c, e, y, 1}

$\Delta E_{c, e, y} = $ energy savings, unit: ktoe, input by user

<a name="Impact of energy efficiency on other suppliers"></a>
Impact of energy efficiency on other suppliers
-

$OS_{c, e, y} = \Sigma_{pc=2}^{N_{pc}} (\frac{k_{pc} \cdot IE_{c, e, pc, y}}{IE_{c, e, y} - \Delta E_{c, e, y}})^2$

Parameters are explained above.

**Note:**  In the $OS_{c, e, y}$ calculation, the Sigma starts from 2, which means you need to exclude the largest supplier values which you have found in the LS calculation [here](#impact-of-energy-efficiency-on-the-largest-supplier)