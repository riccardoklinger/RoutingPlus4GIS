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
import configparser
import json
import os

import requests
from qgis.PyQt.QtCore import QCoreApplication, QVariant
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterString,
                       QgsCoordinateTransform,
                       QgsCoordinateReferenceSystem,
                       QgsProcessingException,
                       QgsProject,
                       QgsJsonUtils,
                       QgsWkbTypes,
                       QgsFeature,
                       QgsField,
                       QgsFields,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink)

from qgis import processing


class RoutingPlus4GISIsochrones(QgsProcessingAlgorithm):
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

    INPUT = 'INPUT'
    PROFILE = 'PROFIL'
    RANGE_TYPE = 'ERREICHBARKEITSTYP'
    OUTPUT = 'OUTPUT'
    DISTANCES = 'ENTFERNUNGEN'


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
        return RoutingPlus4GISIsochrones()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'isochrones'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('BKG Isochrones')

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
        return self.tr("Algorithms for RoutingPlus isochrones")

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # We add the input vector features source. It can have any kind of
        # geometry.
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                self.tr('Input layer'),
                [QgsProcessing.TypeVectorPoint],
                optional=False
            )
        )
        self.addParameter(
            QgsProcessingParameterEnum(
            self.PROFILE,
            self.tr('Geschwindigkeitsprofil'),
            options=["Auto", "Schwerlastverkehr", "Fahrrad","Fußgänger","Rollstuhl"],
            defaultValue=0,
            optional=False
            )
        )
        self.addParameter(
            QgsProcessingParameterEnum(
            self.RANGE_TYPE,
            self.tr('Erreichbarkeitstyp'),
            options=["Zeit", "Distanz"],
            defaultValue=0,
            optional=False
            )
        )
        self.addParameter(
            QgsProcessingParameterString(
                self.DISTANCES,
                self.tr("Distance(s) in m oder sekunden"),
                "300,600,900",
                optional=False,
            )
        )

        # We add a feature sink in which to store our processed features (this
        # usually takes the form of a newly created vector layer when the
        # algorithm is run in QGIS).
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Output layer')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        # Retrieve the feature source and sink. The 'dest_id' variable is used
        # to uniquely identify the feature sink, and must be included in the
        # dictionary returned by the processAlgorithm function.
        source = self.parameterAsSource(
            parameters,
            self.INPUT,
            context
        )
        profile = self.parameterAsEnum(parameters, self.PROFILE, context)
        if profile == 0:
            profil = "driving-car"
        if profile == 1:
            profil = "driving-hgv"
        if profile == 2:
            profil = 'cycling-regular'
        if profile == 3:
            profil = 'foot-walking'
        if profile == 4:
            profil = "wheelchair"
        type = self.parameterAsEnum(parameters, self.RANGE_TYPE, context)
        if type == 0:
            typ = "time"
        if profile == 1:
            typ = "distance"
        uuid = self.getUUID()
        crs = self.parameterAsCrs(
            parameters,
            self.INPUT,
            context
        )
        dists = self.parameterAsString(
            parameters,
            self.DISTANCES,
            context
        )
        #construct URL
        url = 'https://sg.geodatenzentrum.de/web_ors__' + uuid + '/v2/isochrones/{}/geojson'.format(profil)
        feedback.pushInfo(url)
        feedback.pushInfo(str(crs))
        h = {'Content-Type': 'application/json; charset=utf-8',
             'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8' }
        
        # If source was not found, throw an exception to indicate that the algorithm
        # encountered a fatal error. The exception text can be any string, but in this
        # case we use the pre-built invalidSourceError method to return a standard
        # helper text for when a source cannot be evaluated
        if source is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))
        fields = QgsFields()
        
        fields.append(QgsField("group_index", QVariant.Int))
        fields.append(QgsField("value", QVariant.Int))
        fields.append(QgsField("center", QVariant.String, len=255))
        fields.append(QgsField("original_id", QVariant.Int))
        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            fields,
            QgsWkbTypes.Polygon,
            QgsCoordinateReferenceSystem(4326)
        )

        # Send some information to the user
        feedback.pushInfo(f'CRS is {source.sourceCrs().authid()}')

        # If sink was not created, throw an exception to indicate that the algorithm
        # encountered a fatal error. The exception text can be any string, but in this
        # case we use the pre-built invalidSinkError method to return a standard
        # helper text for when a sink cannot be evaluated
        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT))

        # Compute the number of steps to display within the progress bar and
        # get features from source
        total = 100.0 / source.featureCount() if source.featureCount() else 0
        features = source.getFeatures()

        for current, feature in enumerate(features):
            # Stop the algorithm if cancel button has been clicked
            if feedback.isCanceled():
                break
            feedback.pushInfo(str(feature))
            point = feature.geometry().asPoint()
            transform = QgsCoordinateTransform(crs,
                                   QgsCoordinateReferenceSystem("EPSG:4326"), QgsProject.instance())
            point4326 = transform.transform(point)
            #pointB4326 = transform.transform(pointB)
            d = '{"locations":[['+str(point4326.x())+ ','+str(point4326.y()) + ']], "range":[' + dists + '],"range_type":"' + typ + '"}'
            feedback.pushInfo(d)   
            # Add a feature in the sink
            #sink.addFeature(feature, QgsFeatureSink.FastInsert)
            response = requests.post(url, data=d, headers=h)
            feedback.pushInfo(str(response.text)) 
            fieldsBKG = QgsJsonUtils.stringToFields(json.dumps(response.json()))
            featuresBKG = QgsJsonUtils.stringToFeatureList(json.dumps(response.json()), fieldsBKG)
            #feedback.pushInfo(str(featuresBKG)) 
            for fet in reversed(featuresBKG):
                newFet = QgsFeature()
                newFet.setGeometry(fet.geometry())
                attrs = fet.attributes()
                #feedback.pushInfo(str(attrs))
                newFet.setAttributes([
                    attrs[0],
                    attrs[1],
                    attrs[2],
                    feature.id()
                ])
                sink.addFeature(newFet, QgsFeatureSink.FastInsert)
            #feedback.pushInfo(str(type(featuresBKG)))
            # Update the progress bar
            feedback.setProgress(int(current * total))

        return {self.OUTPUT: dest_id}
