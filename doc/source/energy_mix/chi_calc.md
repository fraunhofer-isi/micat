---
title: Calculation of the improvement action energy mix coefficient
description: This page shows the equations necessary to calculate the coefficient to convert the (sub-)sectoral energy mix to improvement action energy mix.
license: AGPL
---

<!--
© 2024 Fraunhofer-Gesellschaft e.V., München

SPDX-License-Identifier: AGPL-3.0-or-later
-->

Calculation of $\chi$
===

$\chi$ can be calculated in three alternative ways from the final energy demand:

a)    $\chi_{e, ss, a} = \frac{1}{n_{\rm{y}}} \sum_y \frac{E_{e,ss,a,y} / \sum_e E_{e,ss,a,y}}{E_{e,ss,y} / \sum_e E_{e,ss,y}} $

b)    $\chi_{e, ss, a} = \frac{1}{n_{\rm{y}}} \sum_y \frac{E_{e,ss,a,y}}{E_{e,ss,y}} $

c)    $\chi_{e, ss, a, y} = \frac{E_{e,ss,a,y}}{E_{e,ss,y}} $


For the calculation of $\lambda_{e, ss, a, y} $ the difference between a) and b) is not important/canceled out. 

$E_{e,ss,a,y}$: Final energy demand for given energy carrier, sub sector, improvement action, and year

$n_{\rm{y}}$: Number of years

$E_{e,ss,y} =\sum_a E_{e,ss,a,y} $
