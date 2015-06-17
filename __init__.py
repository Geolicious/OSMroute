# -*- coding: utf-8 -*-
"""
/***************************************************************************
 OSMroute
                                 A QGIS plugin
 OpenRouteService routing
                             -------------------
        begin                : 2015-06-17
        copyright            : (C) 2015 by Riccardo Klinger / Geolicious
        email                : riccardo.klinger@geolicious.de
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load OSMroute class from file OSMroute.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .OSMroute import OSMroute
    return OSMroute(iface)
