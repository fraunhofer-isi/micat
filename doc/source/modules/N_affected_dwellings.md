---
# © 2025 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

title: Number of affected dwellings assumption
description: This page shows the equation used to assume the number of affected buildings for residential sector measures.
license: AGPL
---

<!--
© 2024, 2025 Fraunhofer-Gesellschaft e.V., München

SPDX-License-Identifier: AGPL-3.0-or-later
-->

Number of affected dwellings assumption
===

Since this figure is necessary for the calculation of energy poverty and indoor climate-related indicators, this
module assumes the number of affected dwellings for residential measures.

The easiest approach comes into play if users specify the figure in the measure-specific template, rendering the
equations to come superfluous. Alternatively, users can also specify a renovation rate in this template, which is
then multiplied with national dwelling stock data (on the local level, values are scaled using the [scaling module](./local_scaling.md)
but can be altered) to calculate the number of affected dwellings. 

In case neither of these values are stated, the number of affected dwellings is calculated from energy savings 
using a coefficient issued from modelling activities and provided by e3m (id_parameter=48).

Equations
-

### For id_action_type 1, 2, and 3
<a name = "Determination of N for id_action_type 1, 2, and 3"></a>

If $N_{{\rm user\_input}, y} \neq NaN => N_y = N_{{\rm user\_input}, y}$

If $N_{{\rm user\_input}, y} = NaN =>$ 

____ IF $ARR_{{\rm user\_input}, y} \neq NaN => N_y = ARR_{{\rm user\_input}, y} / 100 \cdot DS$

____ IF $ARR_{{\rm user\_input}, y} = NaN => N_y = \Delta E_{ss, a, y} \cdot k_{NIA/\Delta E, a}$

$N_{{\rm user\_input}, y}$ = user input "number of affected dwellings" on residential tab in measure specific parameters template (id_parameter = 45)

$ARR_{{\rm user\_input}, y}$ = "annual renovation rate" on residential tab in measure specific parameters template (id_parameter = 43)

$DS$ = national dwelling stock (id_parameter = 32, table wuppertal_parameters **and** measure specific template file, residential tab)

$k_{NIA/\Delta E, a}$ = number of affected dwellings per ktoe (coefficient describing the average number of improvement actions per energy unit) (id_parameter = 48, source e3m, public/e3m/NIA_per_ktoe.xlsx)

$\Delta E_{ss, a, y}$ = energy savings stemming from front end

### For id_action_type 4

If $N_{{\rm user\_input}, y} \neq NaN => N_y = N_{{\rm user\_input}, y}$

If $N_{{\rm user\_input}, y} = NaN =>$ 

_____ If $ARR_{{\rm user\_input}, y} \neq NaN => ARR_{{\rm user\_input}, y} / 100 \cdot DS$

_____ If $ARR_{{\rm user\_input}, y} = NaN => N_y = 0$

$N_{{\rm user\_input}, y}$ = number of affected dwellings (id_parameter = 45), specified as measure-specific parameter by a user

$ARR_{{\rm user\_input}, y}$ = "annual renovation rate" on residential tab in measure-specific parameters template (id_parameter = 43)

### For other values of id_action_type and other sub sectors

$N_y = 0$
