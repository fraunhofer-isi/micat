<!--
© 2024-2026 Fraunhofer-Gesellschaft e.V., München

SPDX-License-Identifier: AGPL-3.0-or-later
-->

Material demand
-

Total material demand per year $`MD_{ss,a,y,}`$ is calculated using the following equation:

$`MD_{c,ss,a,y,crm} = C_{ss,a,y} \cdot mi_{ss,a,crm}`$

$`C_{c,ss,a,y}`$ = Capacity of the installed RE technology _ss_ with configuration _a_ in country _c_ and year _y_ (main user input)

$`mi_{ss,a,crm}`$ = Material intensity of the installed RE technology _ss_ with configuration _a_ in country _c_ per critical raw material _crm_

(id_parameter = 71) - a respective id_crm was added to the database (raw_data/id_crm.xlsx) 

The results should the sum of the material demands across all critical raw materials crm in kg

Supply risk factor
-

The Aggragated supply risk factor per year $`ASRF_{ss,a,y}`$ is calculated using the following equation:

$`ASRF_{ss,a,y} = C_{ss,a,y} \cdot srf_{ss,a}`$

$`srf_{ss,a}`$ = Supply risk factor of installed RE technology _ss_ with configuration _a_ 

(id_parameter = 72)

The results are unitless!