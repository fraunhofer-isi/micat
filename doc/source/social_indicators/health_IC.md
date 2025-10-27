---
# © 2025 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

title: Health effects linked to indoor climate
description: This page shows the equations necessary to calculate the health effects linked to improved indoor climate.
license: AGPL
---

<!--
© 2024, 2025 Fraunhofer-Gesellschaft e.V., München

SPDX-License-Identifier: AGPL-3.0-or-later
-->

Health effects due to indoor climate
=

Quantification
-

$`\Delta DALY_{{\rm Asthma}, m, y} = DPDB_c \cdot N_{m, y} \cdot MDRS_c \cdot DBTF_{c}`$

$`\Delta DALY_{{\rm Asthma}, m, y}`$ = reduction in disability-adjusted life years due to improved air quality

$`DPDB_{c}`$ = DALY per damp and mouldy building ratio (source: Wuppertal, /public/Wuppertal/health.xlsx)

$`N_{m, y}`$ = number of affected buildings, calculated in the [related module](../modules/N_affected_dwellings.md)

$`MDRS_c`$ = share of measures constituting medium and deep renovations  (source: Wuppertal, /public/Wuppertal/health.xlsx)

$`DBTF_c`$ = damp and mouldy buildings targetedness factor (share of deep renovations implemented in buildings plagued with dampness and mould) (source: Wuppertal, /public/Wuppertal/health.xlsx)


Monetisation
-

$`HC_{{\rm AST}, c, ss, a, y} = \Delta DALY_{{\rm Asthma}, m, y} \cdot VOLY_{c, y}`$

$`HC_{{\rm AST}, c, ss, a, y}`$ = monetary benefits linked to a reduction of dampness and mould-related asthma cases 

$`\Delta DALY_{{\rm Asthma}, m, y}`$ = reduction in disability-adjusted life years due to improved air quality (from #28)

$`VOLY_{c, y}`$ = value of life year (id_parameter = 56). Sheet VOLY in public/WHO 