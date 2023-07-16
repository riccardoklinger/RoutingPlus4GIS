# -*- coding: utf-8 -*-

"""
/***************************************************************************
 RoutingPlus4GIS
                                 A QGIS plugin
 RoutingPlus implememtation for QGIS and ArcGIS
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
"""
import configparser
import os

def getUUID():
    uuid = os.environ.get('UUID')
    if not uuid:
        config = configparser.RawConfigParser()
        config.read('CONFIG.cfg')
        uuid = config.get('Authorization', 'UUID')
    print(uuid)
    return uuid