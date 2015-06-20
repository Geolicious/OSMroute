# -*- coding: utf-8 -*-
"""
/***************************************************************************
 OSMroute
                                 A QGIS plugin
 OpenRouteService routing
                              -------------------
        begin                : 2015-06-17
        git sha              : $Format:%H$
        copyright            : (C) 2015 by Riccardo Klinger / Geolicious
        email                : riccardo.klinger@geolicious.de
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
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon
# Initialize Qt resources from file resources.py

# Import the code for the dialog
from OSMroute_dialog import OSMrouteDialog
from qgis.core import * #to get access to qgis
#we will need these for getting the ors response and to parse it:

from xml.etree import ElementTree
import urllib2, os, requests, qgis.utils, os.path, resources_rc
#we need qvariant to build the shapefile
from PyQt4.QtCore import QVariant

class OSMroute:
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
            'OSMroute_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = OSMrouteDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&OSM route')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'OSMroute')
        self.toolbar.setObjectName(u'OSMroute')

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
        return QCoreApplication.translate('OSMroute', message)


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

        icon_path = ':/plugins/OSMroute/logo.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Create Route with OpenRouteService'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginWebMenu(
                self.tr(u'&OSM route'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar


    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()
        print "let's start"
        canvas = qgis.utils.iface.mapCanvas()
        allLayers = canvas.layers()
        #clear layer list prior calling the dialog
        self.dlg.start.clear()
        self.dlg.stop.clear()
        self.dlg.via.clear()
        self.dlg.mode.clear()
        #adding current layers to the dlg
        # index = 1  
        self.dlg.mode.addItem('Fastest')
        self.dlg.mode.addItem('Shortest')

        # self.dlg.layer_extent.setItemData(0,'None_id')
        # self.dlg.layer_extent.setItemText(0,'None - use keywords!')
        # for i in allLayers:
        #     if i.type() == 0 or i.type() == 1:
        #         self.dlg.layer_extent.addItem(i.name())     
        #         self.dlg.layer_extent.setItemData(index,i.id())
        #         self.dlg.layer_extent.setItemText(index,i.name())
        #         index = index +1
        # self.dlg.precision.clear()
        # self.dlg.precision.addItem('use user location (slow, accurate)')
        # self.dlg.precision.addItem('use place location (fast, inaccurate)')
       
        # self.dlg.output_file.addItem('no file of tweets needed')
        # self.dlg.output_file.addItem('file of raw tweets needed')
        # # Run the dialog event loop
        result = self.dlg.exec_()

        # See if OK was pressed
        if result:

            start_address = self.dlg.start.text().encode('utf-8')
            stop_address = self.dlg.stop.text().encode('utf-8')
            mode = self.dlg.mode.currentText()
            #here comes the geocoding:
            url = "http://openls.geog.uni-heidelberg.de/testing2015/geocoding"
            text='<?xml version="1.0" encoding="UTF-8"?><xls:XLS xmlns:xls="http://www.opengis.net/xls" xmlns:sch="http://www.ascc.net/xml/schematron" xmlns:gml="http://www.opengis.net/gml" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.opengis.net/xls http://schemas.opengis.net/ols/1.1.0/LocationUtilityService.xsd" version="1.1"><xls:RequestHeader/><xls:Request methodName="GeocodeRequest" requestID="123456789" version="1.1"><xls:GeocodeRequest><xls:Address countryCode="DE"><xls:freeFormAddress>' + start_address + '</xls:freeFormAddress></xls:Address></xls:GeocodeRequest></xls:Request></xls:XLS>'
            req = urllib2.Request(url=url,
                data=text,
                headers={'Content-Type': 'application/xml'})
            response_start=urllib2.urlopen(req).read()
            #tidy up response
            newstr = response_start.replace("\n", "")
            response_start = newstr.replace("  ", "")
            xml = ElementTree.fromstring(response_start)
            for child in xml[1][0]:
                numberOfHits = child.attrib["numberOfGeocodedAddresses"]
                print numberOfHits
            if numberOfHits != "0":
                start_point=xml[1][0][0][0][0][0].text
                print start_point
            #do the same for the destination
            url = "http://openls.geog.uni-heidelberg.de/testing2015/geocoding"
            text='<?xml version="1.0" encoding="UTF-8"?><xls:XLS xmlns:xls="http://www.opengis.net/xls" xmlns:sch="http://www.ascc.net/xml/schematron" xmlns:gml="http://www.opengis.net/gml" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.opengis.net/xls http://schemas.opengis.net/ols/1.1.0/LocationUtilityService.xsd" version="1.1"><xls:RequestHeader/><xls:Request methodName="GeocodeRequest" requestID="123456789" version="1.1"><xls:GeocodeRequest><xls:Address countryCode="DE"><xls:freeFormAddress>' + stop_address + '</xls:freeFormAddress></xls:Address></xls:GeocodeRequest></xls:Request></xls:XLS>'
            req = urllib2.Request(url=url,
                data=text,
                headers={'Content-Type': 'application/xml'})
            #tidy up response
            response_stop=urllib2.urlopen(req).read()
            newstr = response_stop.replace("\n", "")
            response_stop = newstr.replace("  ", "")
            xml = ElementTree.fromstring(response_stop)
            for child in xml[1][0]:
                numberOfHits = child.attrib["numberOfGeocodedAddresses"]
                print numberOfHits
            if numberOfHits != "0":
                stop_point=xml[1][0][0][0][0][0].text
                print stop_point
            #create the route for start and destination
            if start_point !="" and stop_point !="":
                print mode
                text = '''<?xml version="1.0" encoding="UTF-8" ?>
<xls:XLS xmlns:xls="http://www.opengis.net/xls" xsi:schemaLocation="http://www.opengis.net/xls http://schemas.opengis.net/ols/1.1.0/RouteService.xsd" xmlns:sch="http://www.ascc.net/xml/schematron" xmlns:gml="http://www.opengis.net/gml" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1.1" xls:lang="it">
    <xls:RequestHeader>
    </xls:RequestHeader>
    <xls:Request methodName="RouteRequest" version="1.1" requestID="00" maximumResponses="15">
        <xls:DetermineRouteRequest>
            <xls:RoutePlan>
                <xls:RoutePreference>Car</xls:RoutePreference>
                <xls:ExtendedRoutePreference>
                    <xls:WeightingMethod>'''
                text+=mode
                text+='''</xls:WeightingMethod>
                </xls:ExtendedRoutePreference>
                <xls:WayPointList>
                    <xls:StartPoint>
                        <xls:Position>
                            <gml:Point xmlns:gml="http://www.opengis.net/gml">
                                <gml:pos srsName="EPSG:4326">'''
                text+=start_point
                text+='''</gml:pos>
                            </gml:Point>
                        </xls:Position>
                    </xls:StartPoint>
                    <xls:EndPoint>
                        <xls:Position>
                            <gml:Point xmlns:gml="http://www.opengis.net/gml">
                                <gml:pos srsName="EPSG:4326">'''
                text+=stop_point
                text+='''</gml:pos>
                            </gml:Point>
                        </xls:Position>
                    </xls:EndPoint>
                </xls:WayPointList>
                <xls:AvoidList />
            </xls:RoutePlan>
            <xls:RouteInstructionsRequest provideGeometry="true" />
            <xls:RouteGeometryRequest>
            </xls:RouteGeometryRequest>
        </xls:DetermineRouteRequest>
    </xls:Request>
</xls:XLS>
'''
                print text
                url="http://openls.geog.uni-heidelberg.de/testing2015/routing"
                print url
                req = urllib2.Request(url=url, data=text, headers={'Content-Type': 'application/xml'})
                response_route=urllib2.urlopen(req).read()
                newstr = response_route.replace("\n", "")
                response_route = newstr.replace("  ", "")
                              
                if response_route != "":
                    xml_route = ElementTree.fromstring(response_route)
                    layer = QgsVectorLayer('LineString', 'route_OSM', "memory")
                    pr = layer.dataProvider()
                    pr.addAttributes([QgsField("attribution", QVariant.String)])
                    layer.updateFields()
                    fet = QgsFeature()
                    seg=[]
                    for i in range(0,len(xml_route[1][0][1][0])):
                        seg.append(QgsPoint(float(str.split(xml_route[1][0][1][0][i].text)[0]),float(str.split(xml_route[1][0][1][0][i].text)[1])))
                    fet.setGeometry(QgsGeometry.fromPolyline(seg))
                    fet.setAttributes(["route provided by openrouteservice.org"])
                    pr.addFeatures([fet])
                    layer.updateExtents() #update it
                    QgsMapLayerRegistry.instance().addMapLayer(layer)

            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            print "routing finished between " + start_address + "(" + start_point + ") and " + stop_address + "(" + stop_point + ")"
            pass