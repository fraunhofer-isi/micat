---
title: Reduction in air pollutants
description: This page shows the equations necessary to calculate the reduction in air pollutants.
license: AGPL
---

<!--
© 2024 Fraunhofer-Gesellschaft e.V., München

SPDX-License-Identifier: AGPL-3.0-or-later
-->

Reduction in air pollutants
===

The "Reduction in air pollution" belongs to the ecologic indicators and is calculated as follows:

$\Delta \xi_{p, c, e, ss, y} = EF_{p, c, e, ss, y} \cdot \Delta E_{c, e, ss, y}$

$\Delta E_{c, e, ss, y} = \sum_u \Delta E_{c, e, ss, u, y}$

$\Delta \xi_{p, c, e, ss, y} = $ "Reduction in air pollution" (=change in pollutant's emissions) 

$EF_{p, c, e, ss, y} = $ emission factor for a given pollutant, region, final energy carrier, subsector, and year, from import\public\iiasa\air_pollutant.xlsx

$p = $ id_parameter for pollutant {4: CO2, 5: SO2, 6: NOX, 7: PM_2_5}

$\Delta E_{c, e, ss, y} = $ energy savings in a given region, final energy carrier, subsector, and year

The raw data for the emission factor values are in kt per PJ of energy.
