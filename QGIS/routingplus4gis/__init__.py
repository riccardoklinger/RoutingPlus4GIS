# -*- coding: utf-8 -*-
"""
/***************************************************************************
 RoutingPlus4GIS
                                 A QGIS plugin
 RoutingPlus implememtation for QGIS and ArcGIS
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2023-07-15
        copyright            : (C) 2023 by Riccardo Klinger
        email                : riccardo.klinger@gmail.com
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

__author__ = 'Riccardo Klinger'
__date__ = '2023-07-15'
__copyright__ = '(C) 2023 by Riccardo Klinger'


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load RoutingPlus4GIS class from file RoutingPlus4GIS.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .RoutingPlus4GIS import RoutingPlus4GISPlugin
    return RoutingPlus4GISPlugin()
