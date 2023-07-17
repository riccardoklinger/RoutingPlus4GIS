# RoutingPlus4GIS
Eine RoutingPlus-Schnittstelle für ArcGIS und QGIS. Mit dieser ist der [RoutingPlus](https://gdz.bkg.bund.de/index.php/default/routing-plus-dienst-web-ors-001.htmls) Service des BKGs in ArcGIS Pro und QGIS nutzbar. 
Die abgerufenen Daten unterliegen hierbei folgendem Quellenvermerk:
© Bundesamt für Kartographie und Geodäsie (Jahr),
https://sg.geodatenzentrum.de/web_public/Datenquellen_web_ors.pdf

# Voraussetzungen

# Installation

## QGIS

## ArcGIS Pro

## Authorisierung

Zur Benutzung des Plugins wird eine UUID des Bundesamtes für Kartographie und Geodäsie benötigt. Dieser kann über das [Dienstleistungszentrum](dlz@bkg.bund.de) erworben werden.
Die UUID kann über unterschiedliche Wege genutzt werden:
- Erstellung einer CONFIG.cfg Datei mit dem folgenden Inhalt im Installationsverzeichnis des Plugins
```
[Authorization]
UUID:IHRE-UUID-HIER
```
- Hinterlegung der UUID in den Umgebungsvariablen des Nutzers und/oder des Systems:
![Systemumgebungsvariablen in Windows mit gestezter UUID](https://imgur.com/9VSU2z7.png)





# Quellen