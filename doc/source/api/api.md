---
title: API
description: Documentation of the Appliation Programming Interface (API)
license: AGPL
---

<!--
© 2023 Fraunhofer-Gesellschaft e.V., München

SPDX-License-Identifier: AGPL-3.0-or-later
-->

# API

The [front end](https://app.micatool.eu) of MICAT communicates with a corresponding back end API to retrieve
information about indicators and perform calculations. The base URL of the API is:

[https://api.micatool.eu](https://api.micatool.eu)

Available API endpoints are documented below. Results are returned as JSON. 

Please note that

a) most of the endpoints can be used as URL in the address bar of a browser (**GET** request).

b) some of the endpoints require to pass additional information in terms of a payload / request body (**POST** request).

The recommenced way to retrieve and display information is to use our front end: [https::/app.micatool.eu](https://app.micatool.eu).
Alternative approaches would be to write custom JavaScript code or use some advanced REST client tool.   


## ID tables

Following API endpoints provide information about ID tables:

[https://api.micatool.eu/id_mode](https://api.micatool.eu/id_mode)

[https://api.micatool.eu/id_region](https://api.micatool.eu/id_region)

[https://api.micatool.eu/id_subsector](https://api.micatool.eu/id_subsector)

[https://api.micatool.eu/id_action_type](https://api.micatool.eu/id_action_type)

[https://api.micatool.eu/id_final_energy_carrier](https://api.micatool.eu/id_final_energy_carrier)

[https://api.micatool.eu/id_indicator](https://api.micatool.eu/id_indicator)

Also see related section [indices/indices_description].

The JSON result includes the properties **headers** and **rows**.
The individual **headers** of the ID tables are:

* **id**: Unique numeric ID, used to identify the "row/entity". Also used as parameter in some API requests. 
* **label**: A short text that serves as a name. Might be used as a display label in graphical user interfaces, e.g. for combo boxes. 
* **description**: Potentially longer text, including more details. Might be used as tooltip text in graphical user interfaces to provide additional context.

**Example** JSON result for the **id_final_energy_carrier** endpoint:

```
{
  "headers": ["id", "label", "description"], 
  "rows": [
    [1, "Electricity", "Electricity"], 
	[2, "Oil", "Oil"], 
	[3, "Coal", "Coal"], 
	[4, "Gas", "Gas"], 
	[5, "Biomass and Waste", "Biomass and Waste"], 
	[6, "Heat", "District heating and CHP"], 
	[7, "H2 and e-fuels", "H2 and synthetic fuels"]
  ]
}
```

## Mapping tables

Following API endpoints provide information about mapping tables, describing relations between ID tables:

[https://api.micatool.eu/mapping__subsector__action_type](https://api.micatool.eu/mapping__subsector__action_type)

The JSON result includes the properties **headers** and **rows**. In addition to the column "id", there is a 
source column (left) and a target column (right). 

In a mapping table, several source values might be mapped to several target values. Therefore, mapping tables allow 
to model multiple types of relation: many to many, many to one, one to many, one to one).
The values of the source column might not be unique. The values of the column 'id' are unique.

The mapping table **mapping__subsector__action_type** describes what id_action_type values exist for a distinct value of id_subsector.
For example, **id_subsector** 1 provides the **id_action_type** values 8, 10, 11, 12.  

 
## Indicator calculations

The API endpoint for indicator calculations is

https://api.micatool.eu/indicator_data  

Please note that indicator results cannot be requested individually. There is only this single end point and data for all calculated
indicators is returned as a JSON dictionary. 

This endpoint requires following input parameters:

* **id_mode**, as query parameter in the url, also see [https://api.micatool.eu/id_mode](https://api.micatool.eu/id_mode)
* **id_region**, as query parameter in the url, also see [https://api.micatool.eu/id_region](https://api.micatool.eu/id_region)
* information about **measures** and optional **parameters** as JSON payload

Full example URL for POST request:

https://api.micatool.eu/indicator_data?id_mode=1&id_region=1

For some example payload and JavaScript code see

https://app.micatool.eu/demo_index.html

Open the developer tools of your browser (for example F12) and have a look at the source code. 
It demonstrates an example JSON payload, including user input about energy efficiency measures.

The API does not convert **units**. Energy related values need to be specified in the unit **ktoe**. 
If your user input is specified in different units or you want to visualize results in different units,
you need to implement corresponding unit conversions. 

Fractions need to specified (and are returned) as decimal numbers, e.g. 0.1 instead of 10 %. 
Therefore, you might need a conversion factor of 100 in some use cases.
   


## Parameter default values

a) The API endpoint for generating global default parameter values is:

https://api.micatool.eu/json_parameters

This endpoint requires following input parameters:

* **id_mode**, as query parameter in the url, also see [https://api.micatool.eu/id_mode](https://api.micatool.eu/id_mode)
* **id_region**, as query parameter in the url, also see [https://api.micatool.eu/id_region](https://api.micatool.eu/id_region)


Full example url: 

https://api.micatool.eu/json_parameters?id_mode=1&id_region=0

b) The API endpoint for generating measure specific default parameter values is:

https://api.micatool.eu/json_measure 

This enpoint requires following input parameters:

* **id_mode**, as query parameter in the url, also see [https://api.micatool.eu/id_mode](https://api.micatool.eu/id_mode)
* **id_region**, as query parameter in the url, also see [https://api.micatool.eu/id_region](https://api.micatool.eu/id_region)
* information about a **measure** as JSON payload

Full example URL for POST request:

https://api.micatool.eu/json_measure?id_mode=1&id_region=0


Example payload for POST request:

```
{
    "2000": 0,
    "2010": 0,
    "2015": 0,
    "2020": 10,
    "2025": 20,
    "2030": 30,
    "id": 1,
    "row_number": 1,
    "active": true,
    "subsector": {
      "id": 1,
      "label": "Average agriculture",
      "_description": "Agriculture, forestry & fishing"
    },
    "action_type": {
     "id": 8,
     "label": "Cross-cutting technologies",
     "_description": "Energy-efficient electric cross-cutting technologies"
    },
    "details": {},
    "unit": {
      "name": "kilotonne of oil equivalent",
      "symbol": "ktoe",
      "factor": 1
    }
};
```

## Descriptions

The API endpoints **descriptions** and **single_description** provide descriptions, for example for charts.
A single description can be identified by a corresponding, unique key. 

[https://api.micatool.eu/descriptions](https://api.micatool.eu/descriptions)

[https://api.micatool.eu/single_description?key=foo](https://api.micatool.eu/single_description?key=foo)

