---
# © 2025 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

title: Selection of the geographic area
description: How to use the geographic selection pane and how it works in the back end
tooltip: True
license: AGPL
---

<!--
© 2024, 2025 Fraunhofer-Gesellschaft e.V., München

SPDX-License-Identifier: AGPL-3.0-or-later
-->

Selection of the geographic area
===

The selection pane
-

In the MICATool vizard, the first step is the selection of the geographic area. Users have the choice between
the whole European Union as of 2020, a Member State, or a municipality/region in a Member State. For the latter
option, the number of inhabitants of the assessed entity is required, in order to allow for the scaling of some
national values (see below).


Background
----

Within the MICAT project, a key element is the possibility to assess energy efficiency measures, policies, and 
scenarios on three governance levels: European Union, national, and local/regional level.
This also means that the data that is used needs to account for these different levels, as well as showing 
differences between Member States when significant. This is done by providing default data for all relevant 
geographic areas.

*The IDs, inter alia id_region, are described in greater detail [here](../indices/indices_description.md).*

In order to distinguish geographic areas accordingly, IDs have been attributed to all Member States and the whole 
EU area (EU27 in 2020). However, the local level has not been attributed IDs. Instead, the ID of the country is
used, while the national data is scaled to the locality or region. 

*The equation behind the scaling of data can be found [here](../modules/local_scaling.md).*

The reason behind this approach is the objective within the MICATool to provide an equal coverage for all regions
across the European Union. Given the strongly varying availability of datasets across Member States, an equal
coverage would thus not have been possible. 

As an alternative, an approach scaling down national data has been used. Thereby, absolute values from the national
level are scaled down in proportion to the examined locality's or region's population. This concerns values such as
primary production, gross available energy, dwelling stock, gross domestic product. However, the majority of the
stored data is relative and not absolute, describing proportions of a total. For instance, the energy mix is not stated
as the consumption in energy units but rather as an energy carrier's proportion of total energy consumption.

In the future, weighting factors for scaling are being discussed to account for instance for the urbanity of an area,
as well as other influencing factors.