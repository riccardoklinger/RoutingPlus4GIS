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
                       QgsProcessingParameterPoint,
                       QgsPointXY,
                       QgsProject,
                       QgsWkbTypes,
                       QgsProcessingException,
                       QgsCoordinateReferenceSystem,
                       QgsCoordinateTransform,
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

    INPUT_POINT_A = 'StartPoint'
    INPUT_POINT_B = 'EndPoint'
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
            QgsProcessingParameterPoint(
                self.INPUT_POINT_A,
                self.tr('Input VON x,y'),
                optional = True
            )
        )
        self.addParameter(
            QgsProcessingParameterPoint(
                self.INPUT_POINT_B,
                self.tr('Input NACH x,y'),
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

        pointA = self.parameterAsPoint(
            parameters,
            self.INPUT_POINT_A,
            context
        )
        pointB = self.parameterAsPoint(
            parameters,
            self.INPUT_POINT_B,
            context
        )
        crs = self.parameterAsPointCrs(
            parameters,
            self.INPUT_POINT_A,
            context
        )
        #tranform coordinates just to be on the safe side for the API:
        transform = QgsCoordinateTransform(crs,
                                   QgsCoordinateReferenceSystem("EPSG:4326"), QgsProject.instance())
        pointA4326 = transform.transform(pointA)
        pointB4326 = transform.transform(pointB)
        feedback.pushInfo('Berechne Route von ' + str(pointA4326) + 'nach ' + str(pointB4326))
        uuid = self.getUUID()
        url = 'https://sg.geodatenzentrum.de/web_ors__' + uuid + '/v2/directions/driving-car/geojson' 
        h = {'Content-Type': 'application/json; charset=utf-8',
             'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8' }
        
        d = '{"coordinates":[['+str(pointA4326.x())+ ','+str(pointA4326.y()) + '],[' +str(pointB4326.x())+','+ str(pointB4326.y())+']]}'
        response = requests.post(url, data=d, headers=h) 
        feedback.pushInfo(response.text)
        fields = QgsFields()
        fields.append(QgsField("distance", QVariant.Double))
        fields.append(QgsField("duration", QVariant.Double))
        (sink, destId) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            fields,
            QgsWkbTypes.LineString,
            QgsCoordinateReferenceSystem(4326)
        )
        fet = QgsFeature()
        pointList = [QgsPoint(pt[0],pt[1])  for pt in response.json()["features"][0]["geometry"]['coordinates']]        
        geom = QgsGeometry.fromPolyline(pointList)
        fet.setGeometry(geom)
        fet.setAttributes([
            response.json()["features"][0]["properties"]["summary"]["distance"],
            response.json()["features"][0]["properties"]["summary"]["duration"],
        ])
        sink.addFeature(fet, QgsFeatureSink.FastInsert)
        return {self.OUTPUT: destId}
