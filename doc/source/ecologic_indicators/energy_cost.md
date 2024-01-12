---
title: Energy cost savings
description: This page shows the equations necessary to calculate reduced costs of energy thanks to final energy savings.
license: AGPL
---

<!--
© 2024 Fraunhofer-Gesellschaft e.V., München

SPDX-License-Identifier: AGPL-3.0-or-later
-->

Energy cost savings
===


$\Delta EC_{e, ss, u} = \Delta E_{e, ss, u} \cdot p_{e, s, y} \cdot v_{e, y}$

$\Delta EC_{e, ss, u}$ = reduction of energy costs

$\Delta E_{e, ss, u}$ = final energy savings coming from [here](./PEC_FEC_savings.md)

$p_{e, s, y}$ = energy prices (based on Enerdata Price Database, IEA Future of hydrogen, Heizpellets24), distinguished by country, energy carrier, sector, and year. These are CONFIDENTIAL.  (id_parameter = 13)

$v_{e, y}$ = evolution of energy prices (based on IEA World Energy Outlook). Equals the price of target year divided by the price for 2020.

Preprocessing of data
-

The file Enerdata_energy_prices.xlsx in /micat/import_confidential/enerdata contains the data for this indicator. The first sheet either specifies the price of the energy carrier-sector-combination or specifies the code for the relevant rows in the second sheet. Since the mapping relates to sectors rather than subsectors, mapping__sector__subsector.xlsx needs to be used accordingly.

Since there are several data gaps in the second sheet, a four-stepped process to address them is used:
- When merely some values are missing in between for a country and energy carrier in a time se-ries, the missing values are interpolated
- When a larger share of data of a time series is missing, the price trend across the years is as-sessed along the time series of countries with full data and then multiplied with the existing data to extrapolate missing values
- When the whole time series is missing for a country, the European average is used
- When the European average is missing, the non-weighted average of the time series without gaps is calculated and also used for countries with no data at all

Then, in order to reflect the development of energy prices, missing values for the past and future need to be calculated. 

- for energy carriers originating from Enerdata (1,2,3,4,6), the trajectory for the future can be in-terpolated with $v_{e, y}$.
- for the other energy carriers, a constant value is assumed, in the future as well as in the past.