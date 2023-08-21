---
title: Ecologic indicators
description: This page describes the underlying assumptions and data sources for the ecological indicators.
license: AGPL
---

<!--
© 2023 Fraunhofer-Gesellschaft e.V., München

SPDX-License-Identifier: AGPL-3.0-or-later
-->

Ecologic indicators
===

The MICATool covers a range of ecologic (or environmental) indicators, for each a fact sheet has been
written. The fact sheets cover details about background of the indicator, quantification, methodological
challenges, monetisation, etc. This page explains the assumptions and data sources that have been used, while
also linking to the relevant equations.

Energy savings
-

The calculation of energy savings mainly relies on the [calculation of the energy mix](../energy_mix/lambda_chi.md) and
the [conversion from final to primary energy savings](../energy_mix/FEC_to_PEC.md). Relevant key assumptions are described 
on the related page on the constitution of the [energy mix in the MICATool](../energy_mix/energy_mix_description.md). 

Although the energy savings are shown in primary energy savings, the calculation of saved energy costs relies on final
energy savings. These are multiplied with sector-dependent energy prices issued from the Enerdata database (However,
not all subsectors-energy carrier-combinations are available, so some values have been used for other combinations, in 
line with expected prices). Since this database is neither public nor does it allow the publication of values, these 
values are kept in the confidential database.

Here are the equations for the [quantification](./PEC_FEC_savings.md) and the [monetisation](./energy_cost.md). 
The fact sheet is available as a [PDF](../fact_sheets/energy_cost_savings.pdf).




