---
title: Impact on integration of renewables
description: This page shows the equations necessary to calculate the impact of energy efficiency on the integration of renewables.
license: AGPL
---

<!--
© 2024 Fraunhofer-Gesellschaft e.V., München

SPDX-License-Identifier: AGPL-3.0-or-later
-->

Impact on integration of renewables
=

This indicator is quantified by assessing the change in demand-response potentials due to improved energy efficiency.

```{warning}
This indicator currently shows unexpected behaviour. Until this is fixed, please restrain from using its results!
```

Quantification
-

In order to assess the changes in demand-response potentials $`\Delta P_{DR, c, ss, a, t, y}`$ additional as well as lost potentials are allocated to improvement actions across the different sectors. This is done by  attributing every combination of (sub-)sector and improvement action a coefficient $`𝑘_{DR, ss, u}`$:

$`\Delta P_{DR, c, ss, a, t, y} = r_{DR, ss, a, flex, t} \cdot \Delta E_{c, ss, a, y}`$ 

$`\Delta P_{DR, c, ss, a, t, y} = `$ The change in demand-response potential in energy [MWh] by country, energy efficiency action, and technology.

$`r_{DR, ss, a, flex, t} = `$ flexibilisable capacity share (share of installed capacity that can be flexibilised). 
id_parameter = (do be set), source: \micat\back_end\import_public\raw_data\irena\flexibilizable_capacity_share.xlsx)

$`\Delta E_{c, ss, a, y} = `$ energy savings from a certain improvement action which is an input from MICAT and defined by the user of the tool.

$DR$ = Demand-Response.

$c$ = Country (region) in the european union from table id_region.

$ss$ = Sub-sectors

$u$ = Energy efficiency action

$t$ = Energy-consuming technology type.

Monetisation
-

In order to monetize the demand-response potentials, the price of alternatives providing the same demand-response 
service with a similar potential is used. This is done for increases and decreases in demand-response potentials:

$`M_{DR, c, ss, a, y} = \alpha_{DR, c, y} \cdot \Delta P_{DR, c, ss, a, t, y}`$

$`\Delta P_{DR, c, ss, a, t, y} = `$ The change in demand-response potential in energy [MWh] by country, energy 
efficiency action, and technology (see above)

$`\alpha_{DR, c, y} = `$ The cost per demand-response potential unit of an alternative service in [€/MWh]. The battery 
storage system is chosen as an alternative service for demand-response potential in monetisation. This variable depends 
on the source of energy (id_technology), region (id_region), and the cost components for the DR potentials based on 
their sectors.