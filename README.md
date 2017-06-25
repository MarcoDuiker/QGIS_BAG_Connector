QGIS PDOK BAG Connector Plugin
==============================

This QGIS plugin provides a way to easily add PDOK BAG WFS data to your QGIS project neatly side stepping some problems with the QGIS WFS connector.

The plugin adds a vector layer to the map. For this it uses the extent of the map as a bounding box. The plugin uses response paging to get all features in the bounding box. 
Unlike the QGIS WFS connector the attribute table and 'Save as ...' dialog respect the bounding box and won't try to download all features in the services. 

Via the properties of the added layer additional filtering can be set on the layer. The filters will be forwarded to the service so only the resulting features are downloaded.

The plugin can be easily adapted to consume other services as well. 

Please refer to the [help](https://marcoduiker.github.io/QGIS_BAG_Connector/help/build/html/introduction.html) for more info.

This plugin is more a demonstrator than a fully finished product. Error checking, progress info, and respecting a network proxy are vital to add. Finding some way to cache would be the icing on the cake.

