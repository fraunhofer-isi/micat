<!--
© 2024-2026 Fraunhofer-Gesellschaft e.V., München

SPDX-License-Identifier: AGPL-3.0-or-later
-->
Net Land use change
-

Net land use change per year $`LU_{c,ss,a,y}`$ is calculated using the following equation:

$`LU_{c,ss,a,y} = LU(RES)_{c,ss,a,y} -LU(conventional)_{c,ss,a,y}= (C_{c,ss,a,y} \cdot cf_{c,ss,a,y} \cdot (365\,d/yr \cdot 24\,h/d)\cdot lui(RES)_{ss,a})-(C_{c,ss,a,y} \cdot cf_{c,ss,a,y} \cdot (365\,d/yr \cdot 24\,h/d)\cdot \lambda_{c,ss,a,pe,y} \cdot lui(conventional)_{pe})`$

$`lui(RES)_{ss,a}`$ = Land use intensity (RES) per MWh produced electricity per RES technology _ss_ with configuration _a_ (id_parameter = 74)

$`lui(conventional)_{pe}`$ = Land use intensity (conventional) per MWh produced electricity per primary energy carrier _pe_ ( id_parameter = 73)

$`\lambda_{c,ss,a,pe,y}`$ = Substitution factor for each primary energy carrier _pe_ in country _c_ per RES technology _ss_ with configuration _a_ in year _y_ (id_parameter=67)

$`C_{c,ss,a,y}`$ = Capacity of the installed RE technology _ss_ with configuration _a_ in country _c_ and year _y_ (main user input)

$`cf_{c,ss,a,y}`$ = Capacity factor of the installed RE technology _ss_ with configuration _a_ in country _c_ and year _y_ (id_parameter = 64)