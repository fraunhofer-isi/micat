---
title: Calculation of improvement action energy mix
description: This page describes the equations necessary to calculate the energy mix of an improvement action starting from the (sub-)sectoral energy mix and a coefficient vector.
thumbnail: {image} ../micat_logo.jpg
license: AGPL
---

<!--
© 2024 - 2025 Fraunhofer-Gesellschaft e.V., München

SPDX-License-Identifier: AGPL-3.0-or-later
-->

Calculation of improvement action energy mix
===

This module calculates the energy mix of each id_action_type based on the subsectoral energy mix. To do so, the following equation is necessary:

$\Delta E_{e, ss, a, y} = \lambda_{e, ss, a, y} \cdot \Delta E_{ss, a, y}$ 

$\lambda_{e, ss, a, y} = \frac{\chi_{e, ss, a} \cdot \lambda_{e, ss, y}}{\sum_e \chi_{e, ss, a} \cdot \lambda_{e, ss, y}} $

$\Delta E_{e, ss, a, y} =$ final energy savings of final energy carrier $e$ for id_action_type $a$ and subsector $ss$

$\lambda_{e, ss, a, y} =$ action type energy mix (as a share of a given final energy carrier from total final energy consumption within each action type (and subsector))

$\chi_{e, ss, a} =$ action type energy mix coefficient (calculated [here](./chi_calc.md))

$\lambda_{e, ss, y} =$ subsectoral energy mix (as a share of a given final energy carrier from total final energy consumption within each subsector)
