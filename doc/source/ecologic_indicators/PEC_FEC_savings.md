---
# © 2025 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

title: Primary and final energy savings
description: This page shows the equations necessary to calculate primary and final energy savings.
license: AGPL
---

<!--
© 2024, 2025 Fraunhofer-Gesellschaft e.V., München

SPDX-License-Identifier: AGPL-3.0-or-later
-->

Primary energy savings
===

The indicator "Primary savings by fuel" describes the savings accruing in terms of different energy carriers for primary energy consumption:

$\Delta E_{{\rm P}, pe, y} = \sum_u \sum_{ss} \Delta E_{{\rm P}, pe, ss, a, y}$ 

$\Delta E_{{\rm P}, pe, y} = $ Primary savings by fuel ( = total energy savings of an primary energy carrier in a given year)

$\Delta E_{{\rm P}, pe, ss, a, y} =$ total energy savings of primary energy carrier $pe$ for id_action_type $a$ and subsector $ss$ (from [here](../energy_mix/FEC_to_PEC.md))

Final energy savings
---

The "final energy savings" are currently not an indicator but are needed as interim result. The following calculation originally was part of the above.

$\Delta E_{e, y} = \sum_u \sum_{ss} \Delta E_{e, ss, a, y}$

$\Delta E_{e, y} = $ total energy savings for a final energy carrier in a given year

$\Delta E_{e, ss, a, y} =$ energy savings of final energy carrier $e$ for id_action_type $a$ and id_subsector $ss$ (from [here](../energy_mix/lambda_chi.md))

