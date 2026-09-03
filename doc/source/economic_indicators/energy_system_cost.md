
<!--
© 2024, 2025 Fraunhofer-Gesellschaft e.V., München

SPDX-License-Identifier: AGPL-3.0-or-later
-->

Total energy system costs of VRE
-

Total energy system costs of VRE per year $`TESC_{c,ss,a,y}`$ is calculated using the following equation (results in €):

$`TESC_{c,ss,a,y} = E(VRE)_{c,ss,a,y} \cdot esc(VRE)_{c,y}= (C_{c,ss,a,y} \cdot cf_{c,ss,a,y} \cdot (365\,d/yr \cdot 24\,h/d)\cdot esc(VRE)_{c,y})`$

$`esc(VRE)_{c,y}`$ = Energy system cost (VRE) per MWh produced electricity per VRE technology _ss_ with configuration _a_ (id_parameter = 76)

$`E(VRE)_{c,ss,a,y}`$ = Produced electricity of the installed VRE technology _ss_ with configuration _a_ in country _c_ and year _y_ (=0 if ID subsector =32, 33, 34, 35, 36, 37, 38)

$`C_{c,ss,a,y}`$ = Capacity of the installed RE technology _ss_ with configuration _a_ in country _c_ and year _y_ (main user input)

$`cf_{c,ss,a,y}`$ = Capacity factor of the installed RE technology _ss_ with configuration _a_ in country _c_ and year _y_ (id_parameter = 64)