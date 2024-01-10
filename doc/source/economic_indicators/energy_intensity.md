---
title: Impact on energy intensity
description: This page shows the equations necessary to calculate the impact of energy savings on energy intensity.
license: AGPL
---

<!--
© 2023 - 2024 Fraunhofer-Gesellschaft e.V., München

SPDX-License-Identifier: AGPL-3.0-or-later
-->

Impact on energy intensity
=

```{warning}
This indicator currently shows unexpected behaviour. Until this is fixed, please restrain from using its results!
```

The energy intensity is the quotient of primary energy consumption and GDP, thus describing the energy needed to generate a unit of GDP. The baseline (BL) without savings would look as follows:

$\psi_{{\rm BL}, y} = \frac{\sum_e ( GAE_{e, y} - PC_{{\rm NE}, e, y})}{GDP_{{\rm BL}, y}}$

Including savings ($\Delta E$), the equation would look this way:

$\psi_{{\rm \Delta E}, y} = \frac{\sum_e (GAE_{e, y} - PC_{{\rm NE}, e, y} - \Delta E_{{\rm P}, e, y})}{GDP_{{\rm BL}, y} + GDP_{{\rm \Delta E}, y}}$

$\psi_{{\rm BL}, y}$ = energy intensity baseline

$\psi_{{\rm \Delta E}, y}$ = energy intensity including savings

$\Delta E_{{\rm PEC}, e, y}$ = primary energy savings as calculated in the indicator [Energy savings](../ecologic_indicators/energy_cost.md) 
and the [FEC to PEC conversion module](../energy_mix/FEC_to_PEC.md).

$GDP_{{\rm BL}, y}$ = GDP coming from database (id_parameter = 10)

$GDP_{{\rm \Delta E}, y}$ = additional GDP through savings as calculated in [Impact on GDP](./GDP.md)

$GAE_{e, y}$ = gross available energy (id_parameter = 2)

$PC_{{\rm NE}, e, y}$ = primary non-energy consumption (id_parameter = 3)