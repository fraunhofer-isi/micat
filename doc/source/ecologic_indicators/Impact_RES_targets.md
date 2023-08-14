---
title: Energy cost savings
description: This page shows the equations necessary to calculate the impact of energy efficiency on RES targets.
license: AGPL
---

<!--
© 2023 Fraunhofer-Gesellschaft e.V., München

SPDX-License-Identifier: AGPL-3.0-or-later
-->

Impact on RES targets
===

This indicator "Impact on RES targets" belongs to ecologic indicators and assesses how the overall reduction in primary 
energy consumption increases the share of renewables in energy generation. 

Quantification
-

The charts shows the indicator in %-points: $\Delta RES_{y} \cdot 100$.

$\Delta RES_{y} = \left[ {\sum_{pe=4}^5 GAE_{P, pe, y}} / ({\sum_{pe=1}^6 GAE_{P, pe, y}} - \sum_{pe=1}^6 \Delta E_{P, pe, y}) - {\sum_{pe=4}^5 GAE_{P, pe, y}} / {\sum_{pe=1}^6 GAE_{P, pe, y}} \right]$

$\Delta RES_{y} =$ Impact on RES targets (=change in RES share)

$\sum_{pe=1}^6 \Delta E_{P, pe, y} =$ saved primary energy due to energy efficiency from [here](./PEC_FEC_savings.md)

$\sum_{pe=1}^6 GAE_{P, pe, y} =$ total gross available energy (id_parameter = 2)

$\sum_{pe=4}^5 GAE_{P, pe, y} =$ gross available energy generated from renewables energy sources (Renewables and biomass + waste)

Monetisation
-

This ticket monetises the "Impact on RES targets" calculated in #44:

$\Delta CST_{{\rm RES}, y} = \Delta RES_{y} \cdot ({\sum_{pe=1}^6 GAE_{pe, y}} - \sum_{pe=1}^6 \Delta E_{pe, y}) \cdot f_{{\rm CST}}$

$\Delta CST_{{\rm RES}, y}$ = Monetisation of the impact on RES targets (RES) (=cost of statistical transfer of renewables)

$\Delta RES_{y}$ = Impact on RES targets from above

$\sum_{pe=1}^6 \Delta E_{pe, y}$ = total saved primary energy due to energy efficiency, unit: ktoe from [here](./PEC_FEC_savings.md)

$\Delta E_{pe, y}$ = saved primary energy due to energy efficiency

$\sum_{pe=1}^6 GAE_{pe, y}$ = total gross available energy, id_parameter = 2, unit: ktoe

$GAE_{pe, y}$ = gross available energy



$f_{{\rm CST}} = 163 693$ €/ktoe = unit cost of statistical transfers of renewables