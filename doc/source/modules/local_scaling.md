---
title: Scaling of data for the local level
description: This page shows the equation used to scale absolute database values for the local level.
license: AGPL
---

<!--
© 2024 Fraunhofer-Gesellschaft e.V., München

SPDX-License-Identifier: AGPL-3.0-or-later
-->

Scale database values for local level by population
===

When using the local level, absolute values $X_c$ are scaled with the value of the local 
population $pop_{\rm{local}}$:

$X_{\rm{local}} = X_c \cdot pop_{\rm{local}} / pop_c$

$X_{local}$ = scaled value for the municipality 

$pop_{\rm local}$ = local population value, specified for a municipality by user in front end

$pop_c$ = national population related to $X_c$ (id_parameter = 24, "10_24_GDP_population_primes")

*This is relevant for the following id_parameters:*

2: GAE

10: GDP

24: Population

32: Dwelling stock