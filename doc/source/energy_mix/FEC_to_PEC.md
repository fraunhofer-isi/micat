---
title: FEC-to-PEC conversion
description: This page contains the equations to convert final energy (FEC) to primary energy consumption (PEC).
license: AGPL
---

FEC to PEC conversion
===

**A.** **Total primary energy saving** for several years for each primary energy carrier:

$\Delta E_{{\rm P}, pe, ss, a, y} = \Delta E_{{\rm P_{con}}, pe, ss, a, y} + \Delta E_{{\rm P_{map}}pe, ss, a, y}$

$\Delta E_{{\rm P}, pe, ss, a, y} =$ Total primary energy savings 

$\Delta E_{{\rm P_{con}}, pe, ss, a, y} =$ Converted primary energy saving from electricity and heat generation

$\Delta E_{{\rm P_{map}}pe, ss, a, y} =$ mapping of $\Delta E_{e, ss, a, y}$ to primary energy carriers



**B.** **Primary energy saving** for a given id_primary_energy_carrier, id_action_type and year:

$\Delta E_{{\rm P_{con}}, pe, ss, a, y} =k_{{\rm heat}, pe, y} \cdot \Delta E_{{\rm heat}, ss, a, y} + k_{{\rm elec}, pe, y} \cdot (\Delta E_{{\rm elec}, ss, a, y} + k_{{\rm h2}, y} \cdot \Delta E_{{\rm H2}, ss, a, y})$

$\Delta E_{{\rm P_{con}}, pe, ss, a, y}$: Conventional primary energy saving for primary energy carrier $pe$ and year $y$ for heat and electricity

$k_{{\rm heat}, pe, y}$: Coefficient for heat (id_parameter = 20)

$k_{{\rm elec}, pe, y}$: Coefficient for electricity (id_parameter = 21)

$k_{{\rm H2}, pe, y}$: Coefficient for H2 and synthetic fuels (id_parameter = 22)

$\Delta E_{{\rm elec}, ss, a, y} =$ Final energy saving for electricity (= $\Delta E_{e, ss, a, y}$ for e=1), follows from #24

$\Delta E_{{\rm heat}, ss, a, y} =$ Final energy saving for heat (= $\Delta E_{e, ss, u, y}$ for e=7), follows from #24

$\Delta E_{{\rm H2}, ss, a, y} =$ Final energy saving for hydrogen and synthetic carburants (= $\Delta E_{e, ss, a, y}$ for e=8), follows from #24

**C.** **Import script for coefficients**

$k_{{\rm heat}, pe, y} =
\begin{cases}
      \frac{E_{{\rm in, heat}, pe, y} + \tau_{{\rm CHP, heat}, y} \cdot E_{{\rm in, CHP}, pe, y}}{E_{{\rm out, heat}, y} + E_{{\rm out, CHP}, heat, y}} \quad{\rm for} \quad E_{{\rm out, CHP, heat}, y} \neq 0\\ 
      \frac{ E_{{\rm in, heat}, pe, y} }{ E_{{\rm out, heat}, y} } \quad{\rm for} \quad E_{{\rm out, CHP, heat}, y} = 0 \quad{\rm and} \quad E_{{\rm out, heat}, y} \neq 0\\ 
0 \quad{\rm for} \quad E_{{\rm out, CHP, heat}, y} = 0 \quad{\rm and} \quad E_{{\rm out, heat}, y} = 0\\       
\end{cases}$

$k_{{\rm elec}, pe, y} =
\begin{cases}
      \frac{E_{{\rm in, elec}, pe, y} + \tau_{{\rm CHP, elec}, y} \cdot E_{{\rm in, CHP}, pe, y}}{E_{{\rm out, elec}, y} + E_{{\rm out, CHP}, elec, y}} \quad{\rm for} \quad E_{{\rm out, CHP, elec}, y} \neq 0\\ 
      \frac{ E_{{\rm in, elec}, pe, y} }{ E_{{\rm out, elec}, y} } \quad{\rm for} \quad E_{{\rm out, CHP, elec}, y} = 0 \quad{\rm and} \quad E_{{\rm out, elec}, y} \neq 0\\ 
0 \quad{\rm for} \quad E_{{\rm out, CHP, elec}, y} = 0 \quad{\rm and} \quad E_{{\rm out, elec}, y} = 0\\       
\end{cases}$

The figures from Eurostat's NRG balances for main activity producer (MAP) and autoproducer (AP) need to be merged:

$E_{{\rm in, heat}, pe, y} = TI\_EHG\_MAPH\_E_{pe, y} + TI\_EHG\_APH\_E_{pe, y}$

$E_{{\rm out, heat}, y} = TO\_EHG\_MAPH_{{\rm heat}, y} + TO\_EHG\_APH_{{\rm heat}, y}$

$E_{{\rm in, elec}, pe, y} = TI\_EHG\_MAPE\_E_{pe, y} + TI\_EHG\_APE\_E_{pe, y}$

$E_{{\rm out, elec}, y} = TO\_EHG\_MAPE_{{\rm elec}, y} + TO\_EHG\_APE_{{\rm elec}, y}$

$E_{{\rm in, CHP}, pe, y} = TI\_EHG\_MAPCHP\_E_{pe, y} + TI\_EHG\_APCHP\_E_{pe, y}$

$E_{{\rm out, CHP}, heat, y} = TO\_EHG\_MAPCHP_{heat, y} + TO\_EHG\_APCHP_{heat, y}$

$E_{{\rm out, CHP}, elec, y} = TO\_EHG\_MAPCHP_{elec, y} + TO\_EHG\_APCHP_{elec, y}$

Until now, the **nrg_bal** codes TI_EHG_MAPH_E, TI_EHG_MAPCHP, etc. are not mapped in our data import for id_parameter.

=> Since we do not need the energy data as parameters, but only the coefficients, we can hard code those relations in the import script for the coefficients.  

During the import, the **siec** codes for the energy carriers need to be mapped 
a) for the inputs: according to the already existing mapping mapping__siec__energy_carrier for id_primary_energy_carrier
b) for the outputs: according to the id_final_energy_carrier (or use the only existing entry)

The **energy usage share of CHP plants** for the generation of electricity and heat (source) follows from an equivalence number ($\tau$) method:

$\tau_{{\rm CHP, heat}, y} = \frac{\sigma_{{\rm I/O, heat}, y} \cdot E_{{\rm out, CHP, heat}, y}}{\sigma_{{\rm I/O, heat}, y} \cdot E_{{\rm out, CHP, heat}, y} + \sigma_{{\rm I/O, elec}, y} \cdot E_{{\rm out, CHP, elec}, y} }$

$\tau_{{\rm CHP, elec}, y} = \frac{\sigma_{{\rm I/O, elec}, y} \cdot E_{{\rm out, CHP, elec}, y}}{\sigma_{{\rm I/O, elec}, y} \cdot E_{{\rm out, CHP, elec}, y} + \sigma_{{\rm I/O, heat}, y} \cdot E_{{\rm out, CHP, heat}, y}}$

The result might be NaN for the case that both outputs are zero. However, that case is already handled in the equation for the coefficient. 


The **input/output-ratios** $\sigma$ follow from:

$\sigma_{{\rm I/O, elec}, y} = 
\begin{cases}
\frac{\sum_e E_{{\rm in, elec}, e, y}}{E_{{\rm out, elec}, y}} \quad{\rm for} \quad E_{{\rm out, elec}, y} \neq 0\\ 
\frac{\sum_c \sigma_{{\rm I/O, elec}, y, c}}{n_c} \quad{\rm for} \quad E_{{\rm out, elec}, y} = 0\\     
\end{cases}$

$\sigma_{{\rm I/O, heat}, y} = 
\begin{cases}
\frac{\sum_e E_{{\rm in, heat}, e, y}}{E_{{\rm out, heat}, y}} \quad{\rm for} \quad E_{{\rm out, heat}, y} \neq 0\\ 
\frac{\sum_c \sigma_{{\rm I/O, heat}, y, c}}{n_c} \quad{\rm for} \quad E_{{\rm out, heat}, y} = 0\\     
\end{cases}$

$c$ represents regions with $E_{out, ...} \neq \textrm{0}$ ($n_c$ being their number)
