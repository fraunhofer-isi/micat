---
# © 2025, 2026 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

title: Asset value of buildings
description: This page shows the equations necessary to calculate the impact of energy efficiency on asset values of residential and tertiary buildings.
license: AGPL
---

<!--
© 2024, 2025 Fraunhofer-Gesellschaft e.V., München

SPDX-License-Identifier: AGPL-3.0-or-later
-->

Asset value of residential and tertiary buildings
=

This indicator merely applies to the sectors:

- residential (id_sector=4) and
- tertiary (id_sector=3). 

Within these sectors, it only applies to the following end uses:

- building envelope (id_action_type = 1),
- heating fuel switch (id_action_type = 2),  
- improvement of heating (id_action_type = 3 ). 

The formula is the following:

$\Delta AV_{s, y} = \frac{\sum_{e} \sum_u EC_{e, ss, a, y}}{CR_c}$

$\Delta AV_{s, y}$ = added asset value of buildings in € (id_indicator_chart =7)

$EC_{e, ss, a, y}$ = energy cost coming from #34

$CR_c$ = country-dependent capitalisation rate, in public/CBRE, differentiated for residential and tertiary buildings

For indices see #325