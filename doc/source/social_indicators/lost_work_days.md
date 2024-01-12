---
title: Avoided lost work days due to air pollution
description: This page shows the equations necessary to calculate the health effects linked to reduced air pollution in terms of lost work days.
license: AGPL
---

<!--
© 2024 Fraunhofer-Gesellschaft e.V., München

SPDX-License-Identifier: AGPL-3.0-or-later
-->

Avoided lost work days due to air pollution
=

Quantification
-

In order to calculate the avoided lost work days $LWD$ related to the emissions of pollutants, the core equation is the following:

$\Delta LWD_{c, e, u, ss, y} = CF_{{\rm LWD}, c, e, ss, y} \cdot \Delta E_{c, e, ss, y} = CF_{{\rm LWD}, c, e, ss, y} \cdot \sum_u \Delta E_{c, e, ss, u, y}$

$\Delta LWD_{c, e, ss, y} = $ change in pollutants-related lost work days

$CF_{{\rm LWD}, c, e, ss, y} = $ lost work days factor for a given country, energy carrier, subsector, and year

The factor values are in lost work days per PJ of energy

Monetisation
-

$`HC_{{\rm LWD}, c, ss, a, y} = \Delta LWD_{m, y} \cdot VSL_{c, y}`$

$`HC_{{\rm LWD}, c, ss, a, y}`$ = monetary benefits linked to reduced lost work days due to air pollution

$`\Delta LWD_{m, y}`$ = reduction in lost work days due to improved air quality

$`VSL_{c, y}`$ = value of statistical life (id_parameter = 37). Sheet VSL in public/WHO 

