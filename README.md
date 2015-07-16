# OSMrouter
Find routes using OpenStreetMap data. 

**ATTENTION: The current API of OpenRouteService.org only supports Europe, Asia, Africa and Australia!**

## Synopsis

This plugin provides an easy way to get routes from Address A to B via C. Furthermore you can create polygons which represents isochrones. 

## Usage

For route creation type an address for start and destination. You can add a "via" address if you like. A temporary shapefile for the addresses will be created as well.
The routing algorithm can be controlled using type of travel ("car", "bicycle", "pedestrian") and can diferentiate between fastest and shortest ways. The API from Openrouteservice.org will allow 1000 calls per hour.
The route will be created as a temporary shapefile as well.

Isochrone mapping is possible for a maximum of 30min travel time.

All files need to be saved seperately when needed for further analysis.

## Installation

* Download the source and place it in the '/.qgis2/python/plugins/OSMroute' folder  
  (Windows: 'C:\Users\{username}\.qgis2\python\plugins\OSMroute')
* Import the plugin using the normal "add plugin" method described [here](http://docs.qgis.org/2.2/en/docs/user_manual/plugins/plugins.html#managing-plugins 'qgis plugins').

## Version_changes
* 2015/07/16 v.0.4.1 added API key as desired by openrouteservice.org
* 2015/07/14 v.0.4 correct area for accessibility analysis and correct time attribute to differentiate polygons
* 2015/07/05 v.0.3.2 set EPSG 4326 as default for new vector layers.
* 2015/06/23 v.0.3.1 respecting travel type bike and ped on access analysis and corrected labels in GUI
* 2015/06/21 v.0.3 added some attributes to routes and polygons
* 2015/06/21 v.0.2 creation of categorized polygons for isochrone mapping
* 2015/06/21 v.0.1.3 deleted unused import of modul
* 2015/06/21 v.0.1.2 fixed issues with polygons
* 2015/06/21 v.0.1.1 minor changes in description, added messagebox if geocoding fails
* 2015/06/21 v.0.1: initial beta

## Tests

It was tested on Linux Mint/Ubuntu and Windows 7 with QGIS 2.8.1 and Python 2.7.5+ 

## Contributors

We would like to thank the guys at OpenRouteService.org for this great ressource.

## License

```
/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
```

