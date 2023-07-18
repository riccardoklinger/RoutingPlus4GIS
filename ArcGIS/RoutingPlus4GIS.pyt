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

import arcpy
import requests
import os
from support import getUUID

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "RoutingPlus4GIS"
        self.alias = "RoutingPlus4GIS"

        # List of tool classes associated with this toolbox
        self.tools = [Routing, Isochrones]


class Routing(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Routing"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(
            displayName='Wegpunkte der Route',
            name='waypoints',
            datatype='GPFeatureRecordSetLayer',
            parameterType='Required',
            direction='Input')
        param1 = arcpy.Parameter(
            displayName='Geschwindigkeitsprofile',
            name='profile',
            datatype='GPString',
            parameterType='Required',
            direction='Input')
        
        paramX =  arcpy.Parameter(
            displayName='der Routenlayer',
            name='route',
            datatype='DEFeatureClass',
            parameterType='Required',
            direction='Output')
        param0.value = os.path.join(os.path.dirname(__file__), 'layer',
                                'routing.lyrx')
        param0.filter.list = ["Point"]
        param1.filter.type="ValueList"
        param1.filter.list=["Auto", "Schwerlastverkehr", "Fahrrad","Fußgänger","Rollstuhl"]
        param1.value = "Auto"
        #param1.filter.list=["driving-car", "driving-hgv", "cycling-regular","foot-walking","wheelchair"]
        
        params = [param0,param1,paramX]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""

        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        #parameters[0].setErrorMessage(str(arcpy.GetCount_management(parameters[1].value)))
        
            #parameters[0].setErrorMessage(str(type(arcpy.GetCount_management(parameters[0].value))))
            #parameters[0].setErrorMessage("Bitte nur einen Startpunkt definieren!")
        if int(arcpy.GetCount_management(parameters[0].value)[0]) < 2:
            parameters[0].setErrorMessage("Bitte definieren Sie mindestens Start und Endpunkt der Route")
        else:
            parameters[0].clearMessage()
        return
    
    def constructFeatureClass(self, fc, jsonIN, profile,  dura, dist):
        point = arcpy.Point()
        array = arcpy.Array()
       # featureList = []
        #feat = cursor.newRow()
        
        for pt in jsonIN:
            point.X = pt[0]
            point.Y = pt[1]
            array.add(point)
        polyline = arcpy.Polyline(array)
        with arcpy.da.InsertCursor(fc, ["profile", "distance", "duration", "SHAPE@"]) as cursor:
            cursor.insertRow((profile, dist, dura, polyline))
        return fc
    

    def execute(self, parameters, messages):
        """The source code of the tool."""
        #print the uuid:
        uuid = getUUID()
        messages.addMessage("Zugriff mittels folgender UUID: " + uuid)
        messages.addMessage("Zugriff mittels folgender UUID: " + uuid)
        messages.addMessage(type(parameters[0].value))
        wayPointsIn = parameters[0].value
        if parameters[1].valueAsText == 'Auto':
            profile = "driving-car"
        if parameters[1].valueAsText == "Schwerlastverkehr":
            profile = "driving-hgv"
        if parameters[1].valueAsText == "Fahrrad":
            profile = 'cycling-regular'
        if parameters[1].valueAsText == "Fußgänger":
            profile = 'foot-walking'
        if parameters[1].valueAsText == 'Rollstuhl':
            profile = "wheelchair"
        url = 'https://sg.geodatenzentrum.de/web_ors__' + uuid + '/v2/directions/{}/geojson'.format(profile)
        d = '{"coordinates":['
        with arcpy.da.SearchCursor(wayPointsIn,'SHAPE@') as cursor:
            for row in cursor:
                row4326 = row[0].projectAs(arcpy.SpatialReference(4326))
                x = row4326.firstPoint.X
                y = row4326.firstPoint.Y
                d +='[{},{}],'.format(x,y)
        d = d[:-1]
        messages.addMessage(d)
        d += ']}'
        messages.addMessage(parameters[1].value)
        h = {'Content-Type': 'application/json; charset=utf-8',
             'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8' }
        response = requests.post(url, data=d, headers=h)
        ws, fc_name = os.path.split(parameters[2].valueAsText)
        fc = arcpy.management.CreateFeatureclass(out_path=ws, 
                                                 out_name=fc_name, 
                                                 geometry_type="Polyline", 
                                                 spatial_reference=arcpy.SpatialReference(4326))
        arcpy.AddField_management(fc, "profile", "TEXT", field_length = 50)
        arcpy.AddField_management(fc, "duration", "LONG")
        arcpy.AddField_management(fc, "distance", "LONG")
        parameters[2]=self.constructFeatureClass(fc,
                                                response.json()["features"][0]["geometry"]['coordinates'],
                                                parameters[1].valueAsText,
                                                response.json()["features"][0]["properties"]["summary"]["duration"],
                                                response.json()["features"][0]["properties"]["summary"]["distance"],
                                                )

        messages.addMessage(response.text)
        return



class Isochrones(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Isochrones"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        params = None
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        return