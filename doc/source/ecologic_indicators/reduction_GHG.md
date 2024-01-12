---
title: Reduction in air pollutants
description: This page shows the equations necessary to calculate the reduction in GHG emissions.
license: AGPL
---

<!--
© 2024 Fraunhofer-Gesellschaft e.V., München

SPDX-License-Identifier: AGPL-3.0-or-later
-->

GHG emission reduction calculation
=

Quantification
-

The "Reduction in GHG emissions" belongs to the ecologic indicators and is calculated as follows:

$\Delta \xi_{{\rm CO_2}, c, e, ss, y} = EF_{ {\rm CO_2}, c, e, ss, y} \cdot \Delta E_{c, e, ss, y}$

$\Delta E_{c, e, ss, y} = \sum_u \Delta E_{c, e, ss, u, y}$

$\Delta \xi_{ {\rm CO_2}, c, e, ss, y} = $ "Reduction in air pollution" (=change in pollutant's emissions) 

$EF_{ {\rm CO_2}, c, e, ss, y} = $ emission factor for a given pollutant, region, final energy carrier, subsector, and year, from import\public\iiasa\air_pollutant.xlsx

$\Delta E_{c, e, ss, y} = $ energy savings in a given region, final energy carrier, subsector, and year

The raw data for the emission factor values is in kt per PJ of energy.

Monetisation
-

To monetise greenhouse gas emission (GHG) savings ($`M\xi_{\rm CO_2}`$), multiply the reduced GHG emissions $`\Delta \xi_{{\rm CO_2}, c, e, ss, y}`$ with a time-dependent monetisation factor $`k_{\rm CO_2}`$:

$`M\xi_{{\rm CO_2}, c, ss, u, y} = \Delta {CO_2}_{c, ss, u, y} \cdot k_{{\rm CO_2}, y} `$

The monetisation factor is 199€$`/tCO_2`$ in 2020, 219€$`/tCO_2`$ in 2030 and 255€$`/tCO_2`$ in 2050. All monetary values are stated in €$`_{2021}`$ and are
issued by the [German Federal Environmental Agency](https://www.umweltbundesamt.de/daten/umwelt-wirtschaft/gesellschaftliche-kosten-von-umweltbelastungen)
and annually updated to adjust prices to the previous year.