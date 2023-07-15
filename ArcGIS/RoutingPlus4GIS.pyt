# -*- coding: utf-8 -*-

import os
import arcpy
import requests
import configparser

def loadCOnfig():
    config = configparser.RawConfigParser()
    config.read(os.path.join(os.path.dirname(__file__), '../CONFIG.cfg'))
    uuid = config.get('Authorization', 'UUID')
    return uuid

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
        #print the uuid:
        uuid = loadCOnfig()
        messages.addMessage(uuid)
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