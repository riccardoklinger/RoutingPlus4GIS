"""
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

#from QGIS.routingplus4gis.support import getUUID

import requests
import configparser
import os
from qgis.PyQt.QtCore import QCoreApplication, QVariant
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsFeature,
                       QgsGeometry,
                       QgsField,
                       QgsFields,
                       QgsPoint,
                       QgsPointXY,
                       QgsWkbTypes,
                       QgsProcessingException,
                       QgsCoordinateReferenceSystem,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterString,
                       QgsProcessingParameterNumber)
from qgis import processing


class RoutingPlus4GISRouting(QgsProcessingAlgorithm):
    """
    This is an example algorithm that takes a vector layer and
    creates a new identical one.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the QgsProcessingAlgorithm
    class.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    INPUT_X = 'INPUT_COORDINATE_X'
    INPUT_Y = "INPUT_COORDINATE_Y"
    INPUT_X2 = "INPUT_COORDINATE_X2"
    INPUT_Y2 = "INPUT_COORDINATE_Y2"
    OUTPUT = 'OUTPUT'

    def getUUID(self):
        uuid = os.environ.get('UUID')
        if not uuid:
            config = configparser.RawConfigParser()
            config.read('CONFIG.cfg')
            uuid = config.get('Authorization', 'UUID')
        return uuid

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return RoutingPlus4GISRouting()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'routing'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('BKG Routing')

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr('Algorithms for RoutingPlus')

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'RoutingPlus4GIS'

    def shortHelpString(self):
        """
        Returns a localised short helper string for the algorithm. This string
        should provide a basic description about what the algorithm does and the
        parameters and outputs associated with it..
        """
        return self.tr("Algorithms for RoutingPlus routing")

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # We add the input vector features source. It can have any kind of
        # geometry.
        self.addParameter(
            QgsProcessingParameterNumber(
                name = self.INPUT_X,
                description = self.tr('Input Längengrad VON'),
                type=QgsProcessingParameterNumber.Double,
                defaultValue = 8.5,
                optional = True
            )
        )
        

        # We add a feature sink in which to store our processed features (this
        # usually takes the form of a newly created vector layer when the
        # algorithm is run in QGIS).
        self.addParameter(
            QgsProcessingParameterNumber(
                self.INPUT_Y,
                self.tr('Input Breitengrad VON'),
                type=QgsProcessingParameterNumber.Double,
                defaultValue = 50.1,
                optional = True            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                self.INPUT_X2,   
                self.tr('Input Längengrad NACH'),
                type=QgsProcessingParameterNumber.Double,
                defaultValue = 9.1,
                optional = True
            )
        )

        # We add a feature sink in which to store our processed features (this
        # usually takes the form of a newly created vector layer when the
        # algorithm is run in QGIS).
        self.addParameter(
            QgsProcessingParameterNumber(
                self.INPUT_Y2,
                self.tr('Input Breitengrad NACH'),
                type=QgsProcessingParameterNumber.Double,
                defaultValue = 48.5,
                optional = True
            )
        )
    

        # We add a feature sink in which to store our processed features (this
        # usually takes the form of a newly created vector layer when the
        # algorithm is run in QGIS).
        #self.addParameter(
        #    QgsProcessingParameterFeatureSink(
        #        self.OUTPUT,
        #        self.tr('Output Route layer')
        #    )
        #)
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Route layer')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        coord_x = self.parameterAsDouble(
            parameters,
            self.INPUT_X,
            context
        )
        coord_y = self.parameterAsDouble(
            parameters,
            self.INPUT_Y,
            context
        )
        coord_x2 = self.parameterAsDouble(
            parameters,
            self.INPUT_X2,
            context
        )
        coord_y2 = self.parameterAsDouble(
            parameters,
            self.INPUT_Y2,
            context
        )
        feedback.pushInfo(str(coord_x))
        uuid = self.getUUID()
        url = 'https://sg.geodatenzentrum.de/web_ors__' + uuid + '/v2/directions/driving-car/geojson' 
        h = {'Content-Type': 'application/json; charset=utf-8',
             'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8' }
        
        d = '{"coordinates":[['+str(coord_x)+ ','+str(coord_y) + '],[' +str(coord_x2)+','+ str(coord_y2)+']]}'
        response = requests.post(url, data=d, headers=h) 
        feedback.pushInfo(str(response.json()["features"][0]))
        fields = QgsFields()
        fields.append(QgsField("distance", QVariant.Double))
        fields.append(QgsField("dtration", QVariant.Double))
        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            fields,
            QgsWkbTypes.LineString,
            QgsCoordinateReferenceSystem(4326)
        )
        fet = QgsFeature()
        point_list = [QgsPoint(pt[0],pt[1])  for pt in response.json()["features"][0]["geometry"]['coordinates']]        
        geom = QgsGeometry.fromPolyline(point_list)
        fet.setGeometry(geom)
        fet.setAttributes([
            response.json()["features"][0]["properties"]["summary"]["distance"],
            response.json()["features"][0]["properties"]["summary"]["duration"],
        ])
        sink.addFeature(fet, QgsFeatureSink.FastInsert)
        return {self.OUTPUT: dest_id}
