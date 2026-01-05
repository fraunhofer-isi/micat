---
# © 2025, 2026 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

title: The front end vizard of the MICATool
description: How to use the front end of the MICATool, in simple steps
tooltip: True
license: AGPL
---

<!--
© 2024, 2025 Fraunhofer-Gesellschaft e.V., München

SPDX-License-Identifier: AGPL-3.0-or-later
-->

The front end vizard
===

This page offers a step-by-step guide through the front end of the MICATool. 

Selection of the geographic area
-

In the MICATool vizard, the first step is the selection of the geographic area. Users have the choice between
the whole European Union as of 2020, a Member State, or a municipality/region in a Member State. For the latter
option, the number of inhabitants of the assessed entity is required, in order to allow for the scaling of some
national values. [This page](./geography.md) contains more details about the selection of the geographic area.

Selection of (sub-)sector and improvement action
-

In order for the MICATool to properly work, measures, policies, and scenarios need to be decomposed into combinations 
of (sub-)sectors and improvement actions. This is due to the fact, that impact factors and default values may strongly
differ between different combinations. The selection of (sub-)sectors and improvement action and how to decompose a 
measure is described [on this page](./specifying_subsector_action.md).


Inputting energy savings
-

The energy savings of measures have to be inputted in total annual savings, [one of three ways to account energy savings](./energy_savings_input.md).
However, the unit of energy savings can be selected in the drop-down menu on the left above the table.
Furthermore, in order to adapt to users' needs and data, specific year columns can be added by clicking on the "+Year"
button in the upper right corner of the table. In the same sense, additional rows can be added with the button "+Row".

Measure-specific parameters
-

The measure-specific template allows to alter default values for a certain row in the front end vizard. Thus, the tool
overrides the default values, in case the users changes a value in the template and uploads it. By default, the template
is populated with the default values the tool would normally use in the entered case. 