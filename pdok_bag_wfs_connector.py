# -*- coding: utf-8 -*-
"""
/***************************************************************************
 PdokBagWfsConnector
                                 A QGIS plugin
 Connects to the BAG WFS
                              -------------------
        begin                : 2017-06-25
        git sha              : $Format:%H$
        copyright            : (C) 2017 by Marco Duiker - MD-kwadraat
        email                : md@md-kwadraat.nl
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os.path

from PyQt4.QtCore import *
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import *
from PyQt4.QtGui import QAction, QIcon

import qgis
import webbrowser
from qgis.core import *

from osgeo import ogr

# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from pdok_bag_wfs_connector_dialog import PdokBagWfsConnectorDialog


class PdokBagWfsConnector:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'PdokBagWfsConnector_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # initialize service url
        with open(os.path.join(self.plugin_dir,'url.txt'),'r') as f:
            url = f.read().strip()
        if url[-1] != '&' and url[-1] != '?':
            if '?' in url:
                url = url + '&'
            else:
                url = url + '?'
        self.service_url = url

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&PDOK BAG WFS Connector')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'PdokBagWfsConnector')
        self.toolbar.setObjectName(u'PdokBagWfsConnector')

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('PdokBagWfsConnector', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        # Create the dialog (after translation) and keep reference
        self.dlg = PdokBagWfsConnectorDialog()

        # add some slots for the signals
        self.dlg.button_box.button(QDialogButtonBox.Ok).setEnabled(False)
        QObject.connect(self.dlg.fileBrowseButton_2, SIGNAL("clicked()"), self.chooseFile)
        QObject.connect(self.dlg.fileNameBox, SIGNAL("textChanged(QString)"), self.fileNameBoxChanged)
        QObject.connect(self.dlg.helpButton, SIGNAL("clicked()"), self.showHelp)

        # populate the layer combo
        with open(os.path.join(self.plugin_dir,'layers.txt'),'r') as f:
            layers = [line.strip() for line in f]
        for layer in layers:
            self.dlg.layerCombo.addItem(layer)

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToWebMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/PdokBagWfsConnector/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Connect to PDOK BAG WFS '),
            callback=self.run,
            parent=self.iface.mainWindow())

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginWebMenu(
                self.tr(u'&PDOK BAG WFS Connector'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    def chooseFile(self):
        """Reacts on browse button and opens the right file selector dialog"""

        fileName = QFileDialog.getSaveFileName(caption = self.tr(u"Save .xml and .vrt link files"), directory = '', filter = '*.vrt')
        self.dlg.fileNameBox.setText(fileName)
        
    def fileNameBoxChanged(self, fileName):
        """Reacts on a changed filename; enables the OK button if file name is ok"""

        if os.path.exists(os.path.dirname(fileName)):
            self.dlg.button_box.button(QDialogButtonBox.Ok).setEnabled(True)
            
    def showHelp(self):
        """Reacts on help button"""

        #qgis.utils.showPluginHelp(filename = 'help/index')
        webbrowser.open_new(os.path.join("file://",os.path.abspath(self.plugin_dir), 'help/build/html','index.html')) 
        

    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            canvas = self.iface.mapCanvas()
            url =  self.service_url
            file_name = os.path.abspath(self.dlg.fileNameBox.displayText())
            layer_name = self.dlg.layerCombo.currentText()
            extent = canvas.extent()
            srs = canvas.mapRenderer().destinationCrs().authid()
            
            link_url = url + u'service=wfs&amp;typeName=%s&amp;srsName=%s' % (layer_name,srs)
            xml = u"<OGRWFSDataSource><URL>%s</URL><PagingAllowed>ON</PagingAllowed></OGRWFSDataSource>" % link_url
            vrt = u'<OGRVRTDataSource><OGRVRTLayer name="%s"><SrcDataSource relativeToVRT="true">%s</SrcDataSource><SrcRegion clip="false">%s</SrcRegion></OGRVRTLayer></OGRVRTDataSource>' % (layer_name, os.path.basename(file_name) + '.xml',extent.asWktPolygon())
            try:
                with open(file_name + '.xml','w') as f:
                    f.write(xml)
                with open(file_name,'w') as f:
                    f.write(vrt)
                self.iface.addVectorLayer(file_name,layer_name,'ogr')
            except Exception as v:
                self.iface.messageBar().pushMessage('Error', self.tr(u"Could not write or load link file: ") + v)   
