Introduction
************

About
=====
This plug-in is developed by Marco Duiker from `MD-kwadraat <http://www.md-kwadraat.nl/>`_ .

Background
=========
The PDOK BAG WFS service has a limitation of 1000 features per request. QGIS can use WFS2 response paging to fill your map with features even if more than 1000 features are required to fill your map extent. But … as soon as you try to see the attribute table of the layer or if you try to save the layer as a vector file, QGIS tries to download the entire BAG.

This plugin works around this issue by using the excellent WFS support of OGR.

Basic usage
===========
Zoom the map to your area of interest.
 
Open the dialog via the menu (Web) or the BAG icon. Select a layer and save the connection in a convenient place.

A layer will be added to the map, and the download of the features will start. Beware that this can take a long time if you have selected a large area. As there is no progress info you'll just have to wait.

Adapting the plugin to other services
=====================================
In the plugin folder you'll find a url.txt containing the url of the service the plugin is connecting to. You can change this url to any url of a WFS service you like, as long as you adapt the layers.txt as well, so that it reflects the avaiable typename (layers) in the service.

Further development
===================
This plugin is more a demonstrator than a fully finished product. Error checking, progress info, and respecting a network proxy are vital to add. Finding some way to cache would be the icing on the cake.

Please feel free to fork on GitHub and add your improvements.


