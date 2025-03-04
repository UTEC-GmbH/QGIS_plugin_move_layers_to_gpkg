# -*- coding: utf-8 -*-
"""
/***************************************************************************
 MoveLayersToGPKG
                                 A QGIS plugin
 This plugin renames selected layers (if they are nested in groups) and moves them to a new GeoPackage
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2025-03-04
        copyright            : (C) 2025 by Florian Ludwig
        email                : lasinludwig@gmail.com
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
    """Load MoveLayersToGPKG class from file MoveLayersToGPKG.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .move_layers_to_gpkg import MoveLayersToGPKG
    return MoveLayersToGPKG(iface)
