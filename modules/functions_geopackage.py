"""Module: functions_geopackage.py

This module contains the functions concerning GeoPackages.
"""

from pathlib import Path
from typing import TYPE_CHECKING

from osgeo import ogr
from qgis._core import QgsLayerTree
from qgis.core import (
    Qgis,
    QgsProject,
    QgsVectorFileWriter,
    QgsVectorLayer,
)
from qgis.gui import QgisInterface

from .functions_general import get_current_project, get_selected_layers

if TYPE_CHECKING:
    from qgis.core import QgsMapLayer


def project_gpkg(plugin: QgisInterface) -> Path:
    """Check if a GeoPackage with the same name as the project
    exists in the project folder and creates it if not.

    Example: for a project 'my_project.qgz',
    it looks for 'my_project.gpkg' in the same directory.

    :returns: The Path object to the GeoPackage.
    :raises RuntimeError: If the project is not saved.
    :raises IOError: If the GeoPackage file cannot be created.
    """
    project: QgsProject = get_current_project(plugin)
    project_path_str: str = project.fileName()
    if not project_path_str:
        error_msg: str = "Project is not saved. Please save the project first."
        plugin.iface.messageBar().pushMessage(
            "Error", error_msg, level=Qgis.Critical, duration=5
        )
        raise RuntimeError(error_msg)

    project_path: Path = Path(project_path_str)
    gpkg_path: Path = project_path.with_suffix(".gpkg")

    if not gpkg_path.exists():
        driver = ogr.GetDriverByName("GPKG")
        data_source = driver.CreateDataSource(str(gpkg_path))
        if data_source is None:
            error_msg = f"Failed to create GeoPackage at: {gpkg_path}"
            plugin.iface.messageBar().pushMessage(
                "Error", error_msg, level=Qgis.Critical
            )
            raise OSError(error_msg)

        # Dereference the data source to close the file and release the lock.
        data_source = None

    return gpkg_path


def add_layers_to_gpkg(plugin: QgisInterface) -> None:
    """Add the selected layers to the project's GeoPackage."""

    project: QgsProject = get_current_project(plugin)
    layers: list[QgsMapLayer] = get_selected_layers(plugin)
    gpkg_path: Path = project_gpkg(plugin)
    gpkg_path_str = str(gpkg_path)

    results: dict = {"successes": 0, "failures": []}

    for layer in layers:
        if isinstance(layer, QgsVectorLayer):
            options = QgsVectorFileWriter.SaveVectorOptions()
            options.driverName = "GPKG"
            options.layerName = layer.name()
            options.actionOnExistingFile = QgsVectorFileWriter.CreateOrOverwriteLayer

            error: tuple = QgsVectorFileWriter.writeAsVectorFormatV3(
                layer, gpkg_path_str, project.transformContext(), options
            )
            if error[0] == QgsVectorFileWriter.WriterError.NoError:
                results["successes"] += 1
            else:
                results["failures"].append((layer.name(), error[1]))

    if results["successes"] > 0:
        plugin.iface.messageBar().pushMessage(
            "Success",
            f"Copied {results['successes']} layers to GeoPackage.",
            level=Qgis.Success,
        )
    if results["failures"]:
        for layer_name, error_msg in results["failures"]:
            plugin.iface.messageBar().pushMessage(
                "Error",
                f"Failed to copy layer '{layer_name}': {error_msg}",
                level=Qgis.Critical,
            )


def add_layers_from_gpkg_to_project(plugin: QgisInterface) -> None:
    """Add the selected layers from the project's GeoPackage."""
    project: QgsProject = get_current_project(plugin)
    selected_layers: list[QgsMapLayer] = get_selected_layers(plugin)
    gpkg_path: Path = project_gpkg(plugin)
    gpkg_path_str = str(gpkg_path)

    root: QgsLayerTree | None = project.layerTreeRoot()
    if not root:
        plugin.iface.messageBar().pushMessage(
            "Error", "Could not get layer tree root.", level=Qgis.Critical
        )
        return

    added_layers: list[str] = []
    not_found_layers: list[str] = []

    for layer_to_find in selected_layers:
        layer_name: str = layer_to_find.name()

        # Construct the layer URI and create a QgsVectorLayer
        uri: str = f"{gpkg_path_str}|layername={layer_name}"
        gpkg_layer = QgsVectorLayer(uri, layer_name, "ogr")

        if not gpkg_layer.isValid():
            not_found_layers.append(layer_name)
            continue

        # Add the layer to the project registry first, but not the legend
        project.addMapLayer(gpkg_layer, False)
        # Then, insert it at the top of the layer tree
        root.insertLayer(0, gpkg_layer)
        added_layers.append(layer_name)

    if added_layers:
        plural_s: str = "s" if len(added_layers) > 1 else ""
        plugin.iface.messageBar().pushMessage(
            "Success",
            f"Added {len(added_layers)} layer{plural_s} from the GeoPackage.",
            level=Qgis.Success,
        )
    if not_found_layers:
        plural_s = "s" if len(not_found_layers) > 1 else ""
        layer_list: str = ", ".join(not_found_layers)
        plugin.iface.messageBar().pushMessage(
            "Warning",
            f"Could not find {len(not_found_layers)} layer{plural_s} in GeoPackage: {layer_list}",
            level=Qgis.Warning,
        )


def move_layers_to_gpkg(plugin: QgisInterface) -> None:
    """Move the selected layers to the project's GeoPackage."""

    add_layers_to_gpkg(plugin)
    add_layers_from_gpkg_to_project(plugin)
