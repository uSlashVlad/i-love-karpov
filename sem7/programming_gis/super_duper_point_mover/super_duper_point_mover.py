# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SuperDuperPointMover
                                 A QGIS plugin
 rgrfghwergreh
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2023-09-27
        git sha              : $Format:%H$
        copyright            : (C) 2023 by u/vlad
        email                : u.slash.vlad@gmail.com
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

from qgis.core import QgsWkbTypes, QgsPointXY, QgsGeometry, QgsVectorLayer, QgsSingleSymbolRenderer, QgsMarkerSymbol, QgsLineSymbol, QgsFillSymbol
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon, QBrush, QColor
from qgis.PyQt.QtWidgets import QAction, QMessageBox, QTableWidgetItem, QPushButton

from .resources import *
from .super_duper_point_mover_dialog import SuperDuperPointMoverDialog
from .edit_point_dialog import EditPointDialog
from .edit_line_dialog import EditLineDialog
from .point_tool import PointTool
from .edit_style_dialog import EditStyleDialog
import os.path


class SuperDuperPointMover:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'SuperDuperPointMover_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Super Duper Point Mover')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('SuperDuperPointMover', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/super_duper_point_mover/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u''),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True


    def unload(self):
        self._end_point_picker()
        if hasattr(self, 'selectedLayer') and isinstance(self.selectedLayer, QgsVectorLayer):
            self.selectedLayer.selectionChanged.disconnect(self._feature_selection_changed)

        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Super Duper Point Mover'),
                action)
            self.iface.removeToolBarIcon(action)


    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = SuperDuperPointMoverDialog()

            project_layers = self.iface.mapCanvas().layers()
            self.dlg.layerComboBox.addItem('Выберите слой')
            for layer in project_layers:
                if isinstance(layer, QgsVectorLayer):
                    self.dlg.layerComboBox.addItem(layer.name())
            self.dlg.layerComboBox.currentIndexChanged.connect(self._select_layer)
            self.dlg.editStyleButton.clicked.connect(self._open_style_editor)

        # show the dialog
        self.dlg.show()


    def _select_layer(self, index: int):
        def resetWidgets():
            self.dlg.geometryLabel.setText('Неверный тип геометрии')
            self.dlg.tableWidget.setRowCount(0)
            if hasattr(self, 'selectedLayer') and isinstance(self.selectedLayer, QgsVectorLayer):
                self.selectedLayer.selectionChanged.disconnect(self._feature_selection_changed)
            self.dlg.editStyleButton.setEnabled(False)

        if (index == 0):
            resetWidgets()
            return
        index -= 1

        if hasattr(self, 'selectedLayer') and isinstance(self.selectedLayer, QgsVectorLayer):
            self.selectedLayer.selectionChanged.disconnect(self._feature_selection_changed)
        self.selectedLayer = self.iface.mapCanvas().layer(index)
        self.selectedLayer.selectionChanged.connect(self._feature_selection_changed)
        self.dlg.editStyleButton.setEnabled(True)

        try:
            geometryType = self.selectedLayer.geometryType()
            if (geometryType == QgsWkbTypes.PointGeometry):
                self.dlg.geometryLabel.setText('Тип геометрии: <b>Точки</b>')
            elif (geometryType == QgsWkbTypes.LineGeometry):
                self.dlg.geometryLabel.setText('Тип геометрии: <b>Линии</b>')
            elif (geometryType == QgsWkbTypes.PolygonGeometry):
                self.dlg.geometryLabel.setText('Тип геометрии: <b>Полигоны</b>')
            else:
                resetWidgets()
                return;
        except:
            resetWidgets()
            return;

        self.dlg.tableWidget.setRowCount(self.selectedLayer.featureCount())

        selectedFeatures = self.selectedLayer.selectedFeatureIds()
        row = 0
        for feature in self.selectedLayer.getFeatures():
            featureId = feature.id()
            editCallback = lambda _, layer=self.selectedLayer, featureId=featureId: self._edit_geometry(layer, featureId)

            idItem = QTableWidgetItem(str(featureId))
            idItem.setFlags(QtCore.Qt.ItemIsEnabled)
            if featureId in selectedFeatures:
                self._set_table_call_as_selected(idItem)
            self.dlg.tableWidget.setItem(row, 0, idItem)

            editGeometryButton = QPushButton('Редактировать')
            editGeometryButton.clicked.connect(editCallback)
            if not feature.hasGeometry():
                editGeometryButton.setEnabled(False)
            self.dlg.tableWidget.setCellWidget(row, 1, editGeometryButton)

            row += 1

    def _feature_selection_changed(self, selected: list, deselected: list, clearAndSelect: bool):
        if clearAndSelect:
            for i in range(self.dlg.tableWidget.rowCount()):
                text = self.dlg.tableWidget.item(i, 0).text()
                idItem = QTableWidgetItem(text)
                idItem.setFlags(QtCore.Qt.ItemIsEnabled)
                if i in selected:
                    self._set_table_call_as_selected(idItem)
                self.dlg.tableWidget.setItem(i, 0, idItem)
        else:
            for featureIndex in selected:
                idItem = self.dlg.tableWidget.item(featureIndex, 0)
                self._set_table_call_as_selected(idItem)
                self.dlg.tableWidget.setItem(featureIndex, 0, idItem)
            for featureIndex in deselected:
                text = self.dlg.tableWidget.item(featureIndex, 0).text()
                idItem = QTableWidgetItem(text)
                idItem.setFlags(QtCore.Qt.ItemIsEnabled)
                self.dlg.tableWidget.setItem(featureIndex, 0, idItem)


    def _edit_geometry(self, layer, featureId: int):
        geometryType = layer.geometryType()

        if geometryType == QgsWkbTypes.PointGeometry:
            self._edit_point(layer, featureId)
        elif geometryType == QgsWkbTypes.LineGeometry:
            self._edit_line(layer, featureId)
        elif geometryType == QgsWkbTypes.PolygonGeometry:
            self._edit_polygon(layer, featureId)
        else:
            self._show_warning('Ошибка', 'Неподдерживаемый тип геометрии')


    def _edit_point(self, layer, featureId: int):
        self._close_edit_dialog()

        layer.select(featureId)
        feature = layer.getFeature(featureId)
        featureGeometry = feature.geometry().asPoint()

        self.editPointsDlg = editDlg = EditPointDialog()
        editDlg.layerNameLabel.setText(f'"{layer.name()}" #{featureId} (Точка)')
        editDlg.xLineEdit.setText(str(featureGeometry.x()))
        editDlg.yLineEdit.setText(str(featureGeometry.y()))
        editDlg.pickButton.clicked.connect(self._toggle_edit_point_picker)
        editDlg.show()

        pointsResult = editDlg.exec_()
        layer.deselect(featureId)
        self._end_point_picker()
        if pointsResult:
            try:
                x = float(editDlg.xLineEdit.text())
                y = float(editDlg.yLineEdit.text())

                layer.startEditing()
                newGeometry = QgsGeometry.fromPointXY(QgsPointXY(x, y))
                layer.changeGeometry(featureId, newGeometry)
                layer.commitChanges()
            except Exception as error:
                print('Error on edit geometry', error)
                self._show_warning('Ошибка', 'Введены неверные координаты')


    def _edit_line(self, layer, featureId: int):
        self._close_edit_dialog()

        layer.select(featureId)
        feature = layer.getFeature(featureId)
        featureGeometry = feature.geometry().asMultiPolyline()[0]

        self.editLineDlg = editDlg = EditLineDialog()
        editDlg.layerNameLabel.setText(f'"{layer.name()}" #{featureId} (Линии)')

        editDlg.coordsTable.setRowCount(len(featureGeometry));
        i = 0
        for point in featureGeometry:
            xItem = QTableWidgetItem(str(point.x()))
            editDlg.coordsTable.setItem(i, 0, xItem)
            yItem = QTableWidgetItem(str(point.y()))
            editDlg.coordsTable.setItem(i, 1, yItem)
            i += 1

        editDlg.show()

        pointsResult = editDlg.exec_()
        layer.deselect(featureId)
        if pointsResult:
            try:
                for i in range(len(featureGeometry)):
                    x = float(editDlg.coordsTable.item(i, 0).text())
                    y = float(editDlg.coordsTable.item(i, 1).text())
                    featureGeometry[i] = QgsPointXY(x, y)
                layer.startEditing()
                newGeometry = QgsGeometry.fromMultiPolylineXY([featureGeometry])
                layer.changeGeometry(featureId, newGeometry)
                layer.commitChanges()
            except Exception as error:
                print('Error on edit geometry', error)
                self._show_warning('Ошибка', 'Введены неверные координаты')


    def _edit_polygon(self, layer, featureId: int):
        self._close_edit_dialog()

        layer.select(featureId)
        feature = layer.getFeature(featureId)
        featureGeometry = feature.geometry().asMultiPolygon()[0][0]

        self.editPolygonDlg = editDlg = EditLineDialog()
        editDlg.layerNameLabel.setText(f'"{layer.name()}" #{featureId} (Полигоны)')

        editDlg.coordsTable.setRowCount(len(featureGeometry));
        i = 0
        for point in featureGeometry:
            xItem = QTableWidgetItem(str(point.x()))
            editDlg.coordsTable.setItem(i, 0, xItem)
            yItem = QTableWidgetItem(str(point.y()))
            editDlg.coordsTable.setItem(i, 1, yItem)
            i += 1

        editDlg.show()

        pointsResult = editDlg.exec_()
        layer.deselect(featureId)
        if pointsResult:
            try:
                for i in range(len(featureGeometry)):
                    x = float(editDlg.coordsTable.item(i, 0).text())
                    y = float(editDlg.coordsTable.item(i, 1).text())
                    featureGeometry[i] = QgsPointXY(x, y)
                layer.startEditing()
                newGeometry = QgsGeometry.fromMultiPolygonXY([[featureGeometry]])
                layer.changeGeometry(featureId, newGeometry)
                layer.commitChanges()
            except Exception as error:
                print('Error on edit geometry', error)
                self._show_warning('Ошибка', 'Введены неверные координаты')


    def _toggle_edit_point_picker(self, toggled: bool):
        if toggled:
            def _move_callback(point: QgsPointXY):
                self.editPointsDlg.xLineEdit.setText(str(point.x()))
                self.editPointsDlg.yLineEdit.setText(str(point.y()))

            def _click_callback(point: QgsPointXY):
                _move_callback(point)
                self.editPointsDlg.pickButton.setChecked(False)
                self._end_point_picker()

            self._start_point_picker(
                    _move_callback,
                    _click_callback
                )
        else:
            self._end_point_picker()


    def _start_point_picker(self, move_callback, click_callback):
        self._end_point_picker()
        print('Started picking point')
        self.tool = PointTool(self.iface.mapCanvas())
        self.iface.mapCanvas().setMapTool(self.tool)
        self.tool.moved.connect(move_callback)
        self.tool.clicked.connect(click_callback)

    def _end_point_picker(self):
        if hasattr(self, 'tool'):
            print('Ending picking point')
            self.iface.mapCanvas().unsetMapTool(self.tool)
            del self.tool


    def _close_edit_dialog(self):
        if hasattr(self, 'editPointsDlg'):
            self.editPointsDlg.reject()
            del self.editPointsDlg
        if hasattr(self, 'editLineDlg'):
            self.editLineDlg.reject()
            del self.editLineDlg
        if hasattr(self, 'editPolygonDlg'):
            self.editPolygonDlg.reject()
            del self.editPolygonDlg

    def _open_style_editor(self):
        styleDlg = EditStyleDialog()
        styleDlg.show()
        styleDlg.get_style_data_from_layer(self.selectedLayer)
        if styleDlg.exec_():
            strokeColor = styleDlg.strokeColor
            fillColor = styleDlg.fillColor
            symbolSize = styleDlg.widthSpinBox.value()

            geometryType = self.selectedLayer.geometryType()
            if geometryType == QgsWkbTypes.PointGeometry:
                renderer = QgsSingleSymbolRenderer(QgsMarkerSymbol.createSimple({'name': 'square', 'color': strokeColor, 'size': symbolSize}))
            elif geometryType == QgsWkbTypes.LineGeometry:
                renderer = QgsSingleSymbolRenderer(QgsLineSymbol.createSimple({'color': strokeColor, 'width': symbolSize}))
            elif geometryType == QgsWkbTypes.PolygonGeometry:
                renderer = QgsSingleSymbolRenderer(QgsFillSymbol.createSimple({'outline_color': strokeColor, 'color': fillColor, 'stroke_width': symbolSize}))
            self.selectedLayer.setRenderer(renderer)
            self.selectedLayer.triggerRepaint()


    def _show_warning(self, title: str, content: str):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setText(content)
        msgBox.setWindowTitle(title)
        msgBox.exec()


    def _set_table_call_as_selected(self, item: QTableWidgetItem):
        item.setBackground(QBrush(QColor.fromRgb(255, 220, 51)))
        item.setForeground(QBrush(QColor.fromRgb(28, 28, 28)))
