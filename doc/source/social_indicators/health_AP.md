---
# © 2025, 2026 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

title: Reduced mortality due to air pollution
description: This page shows the equations necessary to calculate the health effects linked to reduced air pollution mortality.
license: AGPL
---

<!--
© 2024, 2025 Fraunhofer-Gesellschaft e.V., München

SPDX-License-Identifier: AGPL-3.0-or-later
-->

Reduced mortality due to air pollution
=

Quantification
-

In order to calculate the reduced mortality $MAP$ related to the emissions of pollutants, the core equation is the following:

$\Delta MAP_{c, e, u, ss, y} = CF_{{\rm MAP}, c, e, ss, y} \cdot \Delta E_{c, e, ss, y} = CF_{{\rm MAP}, c, e, ss, y} \cdot \sum_u \Delta E_{c, e, ss, u, y}$

$\Delta MAP_{c, e, ss, y} = $ change in pollutants-related mortality casualties and lost working days

$CF_{{\rm MAP}, c, e, ss, y} = $ casualty factor for a given country, energy carrier, subsector, and year, either for lost working days or mortality

The casualty factor values are in casualties per PJ of energy

Monetisation
-

$HC_{{\rm MAP}, c, ss, a, y} = \Delta \phi_{c, e, ss, y} \cdot VSL_{c, y}$

$HC_{{\rm MAP}, c, ss, a, y}$ = monetary benefits linked to reduced mortality due to air pollution

$\Delta MAP_{c, e, ss, y} = $ = reduction in mortality due to improved air quality

$VSL_{c, y}$ = value of statistical life (id_parameter = 37). Sheet VSL in public/WHO 

