---
title: Investments
description: This page shows how to determine the investments flowing into the calculations.
license: AGPL
---

<!--
© 2024 Fraunhofer-Gesellschaft e.V., München

SPDX-License-Identifier: AGPL-3.0-or-later
-->

Investments
=

Generally, investments are input by the user in the measure-specific template. However, a default assumption needs to be calculated as default for the template and in case the user does not use the template:

A. If $`I_{{\rm user\_input}, c, ss, a, y} \neq NaN`$:
-

$`I_{c, ss, a, y} = I_{{\rm user\_input}, c, ss, a, y}`$

B. If $`I_{{\rm user\_input}, c, ss, a, y} = NaN`$:
-

$`I_{c, ss, a, y} = \Delta E_{c, ss, a, y} \cdot k_{{\rm I/ktoe}, a} `$

---

$`I_{c, ss, a, y}`$ = investments for a given row in the front end

$`I_{{\rm user\_input}, c, ss, a, y}`$ = user input of investment costs from measure-specific parameter template

$`\Delta E_{c, ss, a, y}`$ = user input of energy savings of the same row in the front end

$`k_{{\rm I/ktoe}, a, y} `$ = investments per saved ktoe (id_parameter=41, source e3m, /public/e3m/investments_per_ktoe.xlsx)