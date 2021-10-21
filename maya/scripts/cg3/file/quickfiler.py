from pathlib import Path
import shutil
from typing import List
from functools import partial
from string import ascii_letters
import PySide2.QtCore as qc
import PySide2.QtWidgets as qw
import PySide2.QtGui as qg

from maya.app.general.mayaMixin import MayaQWidgetDockableMixin

from cg3.ui.windows import maya_main_window
from cg3.ui.widgets import QHLine
from cg3.env.settings import get_project_settings, get_user_settings
from cg3.file.models import Asset

from cg3.event import cg3event


class AssetCompleter(qw.QCompleter):
    def __init__(self):
        super().__init__()
        self.model = qg.QStandardItemModel()
        self.model.setColumnCount(3)
        self.model.setHorizontalHeaderLabels(['Thumb', 'Name', 'Departments'])

        self.setModel(self.model)
        self.setFilterMode(qc.Qt.MatchFlag.MatchContains)

        table = qw.QTableView()
        table.setFixedWidth(300)

        self.setPopup(table)

        self.popup().setMinimumWidth(300)
        self.popup().setFixedHeight(500)

        self.setCompletionColumn(1)
        self.setMaxVisibleItems(200)
        self.setModelSorting(qw.QCompleter.CaseInsensitivelySortedModel)

        h_header = table.horizontalHeader()
        h_header.setSectionResizeMode(0, qw.QHeaderView.ResizeToContents)
        h_header.setSectionResizeMode(1, qw.QHeaderView.ResizeToContents)
        h_header.setStretchLastSection(True)
        #h_header.setStyleSheet("QHeaderView::section:horizontal {padding: 0 10 0 10;};")

        v_header = table.verticalHeader()
        v_header.setSectionResizeMode(qw.QHeaderView.Fixed)
        v_header.setDefaultSectionSize(45)

    def clear_rows(self):
        self.model.removeRows(
            0, self.model.rowCount())

    def add_row(self, asset):
        name = qg.QStandardItem(asset.name)
        icon = qg.QStandardItem()
        icon.setData(qg.QPixmap.fromImage("C:/Users/jobo/Pictures/suzuki_swift.jpg").scaled(
            80, 80, qc.Qt.KeepAspectRatio
        ), qc.Qt.DecorationRole
        )
        deps = qg.QStandardItem(f"{' | '.join(asset.get_deps())}")

        self.model.appendRow([icon, name, deps])

    def add_rows(self, assets):
        for asset in assets:
            self.add_row(asset)


class SearchLineEdit(qw.QLineEdit):
    """LineEdit with special signals needed for autocompletion in QuickFile"""
    mouse_pressed = qc.Signal()
    focus_in = qc.Signal()
    tab_pressed = qc.Signal()

    def __init__(self, height, css):
        self.lost_focus = False
        super().__init__()
        self.setFixedHeight(height)
        self.setStyleSheet(f"border: none; {css}")
        self.setPlaceholderText("Search by Name")

    def mousePressEvent(self, event):  # pylint: disable=invalid-name
        """When left MB pressed, selects all and fires event focus_in."""
        if event.button() == qc.Qt.LeftButton:
            self.selectAll()
            self.mouse_pressed.emit()
        else:
            super().mousePressEvent(event)

    def focusInEvent(self, _):  # pylint: disable=invalid-name
        """When widget reveives focus, selects all and fires event focus_in."""
        if self.lost_focus:
            self.selectAll()
        self.lost_focus = False
        self.focus_in.emit()

    def focusOutEvent(self, event):  # pylint: disable=invalid-name
        """On focus out set instance variable."""
        self.lost_focus = True
        super().focusOutEvent(event)

    def focusNextPrevChild(self, _):  # pylint: disable=invalid-name
        """Fires tab_pressed event."""
        self.tab_pressed.emit()
        return True


class SearchLineCombo(qw.QComboBox):
    return_pressed = qc.Signal()

    def __init__(self, height, css, min_width):
        super().__init__()
        self.setMinimumWidth(min_width)
        self.setFixedHeight(height)
        self.setStyleSheet(css)
        self.css = css

    def focusInEvent(self, event):  # pylint: disable=invalid-name
        super().focusInEvent(event)
        self.setStyleSheet(f"background-color: #ff0000; {self.css}")

    def focusOutEvent(self, event):  # pylint: disable=invalid-name
        super().focusOutEvent(event)
        self.setStyleSheet(f"background-color: none; {self.css}")

    def keyPressEvent(self, event):  # pylint: disable=invalid-name
        super().keyPressEvent(event)
        if event.key() == qc.Qt.Key_Return:
            self.return_pressed.emit()


class QuickFileOpen(qw.QVBoxLayout):
    def __init__(self, asset_provider):
        super().__init__()
        self.inputs_height = 25
        self.inputs_css = "font-size: 14px; font-weight: bold;"

        self.asset_provider = asset_provider

        self.setAlignment(qc.Qt.AlignTop)
        #self.setSpacing(2)

        header_label = qw.QLabel("Quick File Open")
        header_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        header_label.setAlignment(qc.Qt.AlignCenter)
        self.addWidget(header_label)

        self.create_search_row()

        self.completer = None
        self.update_completer()
        cg3event.subscribe("asset_created", self.on_asset_created)

        self.open_button = qw.QPushButton("Nothing selected")
        self.open_button.setDisabled(True)
        self.open_button.clicked.connect(self.open_button_clicked)
        self.addWidget(self.open_button)

        self.search_lineedit.setFocus()

    def on_asset_created(self, asset):
        self.completer.popup().hide()
        self.asset_provider.assets[asset.name] = asset
        self.update_completer()

    def update_completer(self):
        self.completer = AssetCompleter()
        self.completer.add_rows(self.asset_provider.list_assets())
        self.completer.highlighted.connect(self.completer_highlighted)
        self.completer.activated.connect(self.set_asset)
        self.search_lineedit.setCompleter(self.completer)

    def create_search_row(self):
        min_width = 50

        search_component_hbox = qw.QHBoxLayout()
        search_component_hbox.setSpacing(2)

        self.search_lineedit = SearchLineEdit(
            self.inputs_height, self.inputs_css
        )
        self.search_lineedit.focus_in.connect(self.list_all)
        self.search_lineedit.mouse_pressed.connect(self.list_all)
        self.search_lineedit.tab_pressed.connect(self.set_asset)
        self.search_lineedit.returnPressed.connect(self.set_asset)
        search_component_hbox.addWidget(self.search_lineedit, stretch=2)

        self.dep_combo = SearchLineCombo(
            self.inputs_height, self.inputs_css, min_width)
        self.dep_combo.currentIndexChanged.connect(self.dept_changed)
        self.dep_combo.return_pressed.connect(self.open_button_clicked)
        search_component_hbox.addWidget(self.dep_combo, stretch=1)

        self.version_combo = SearchLineCombo(
            self.inputs_height, self.inputs_css, min_width)
        self.version_combo.currentIndexChanged.connect(self.version_changed)
        self.version_combo.return_pressed.connect(self.open_button_clicked)
        search_component_hbox.addWidget(self.version_combo, stretch=1)

        self.addLayout(search_component_hbox)

    def completer_highlighted(self, key):
        self.search_lineedit.setText(key)

    def set_asset(self):
        key = self.search_lineedit.text()

        self.asset = self.asset_provider.get(key)

        self.dep_combo.clear()
        self.version_combo.clear()
        self.dep_combo.addItems(self.asset.get_deps())
        self.dep_combo.setFocus()
        self.completer.popup().hide()

    def list_all(self):
        self.completer.setCompletionPrefix("")
        self.completer.complete()

    def dept_changed(self, _):
        dept = self.dep_combo.currentText()
        versions = self.asset.list_versions(dept)
        if not versions:
            return
        version_scenes = reversed(versions)
        self.version_combo.clear()
        self.version_combo.addItems([v.version for v in version_scenes])

    def version_changed(self, _):
        dep = self.dep_combo.currentText()
        v = self.version_combo.currentText()
        if not v:
            return
        v_scene = self.asset.get_version(dep, v)
        self.open_button.setText(
            f"Open {v_scene.name}"
        )
        self.open_button.setEnabled(True)

    def open_button_clicked(self):
        dep = self.dep_combo.currentText()
        v = self.version_combo.currentText()
        v_scene = self.asset.get_version(dep, v)
        print(f"Open {v_scene}")
        cg3event.post("asset_open_clicked", str(v_scene), self.asset)
        # reset all widgets
        self.search_lineedit.setText("")
        self.dep_combo.clear()
        self.dep_combo.clearFocus()
        self.version_combo.clear()
        self.version_combo.clearFocus()
        self.open_button.setText("Nothing selected")
        self.open_button.setEnabled(False)


class QuickAssetCreator(qw.QVBoxLayout):
    def __init__(self, dialog_parent, asset_provider, extension):
        super().__init__()
        
        self.dialog_parent = dialog_parent
        self.asset_provider = asset_provider
        self.extension = extension

        self.legal_chars = f"{ascii_letters}-,1234567890"
        self.save_char_map = {
            'ä': 'ae', 'ö': 'oe', 'ü': 'ue', 'ß': 'ss',
            'Ä': 'AE', 'Ö': 'OE', 'Ü': 'UE', 
            ' ': '-', '.': '-', ':': '-'
        }

        kind_hbox = qw.QHBoxLayout()

        for kind in self.asset_provider.settings.kinds:
            btn = qw.QPushButton(kind)
            btn.clicked.connect(partial(self.show_dialog, kind))
            kind_hbox.addWidget(btn)

        header_label = qw.QLabel("Quick New Asset")
        header_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        header_label.setAlignment(qc.Qt.AlignCenter)
        self.addWidget(header_label)
        self.addLayout(kind_hbox)

    def show_dialog(self, kind):
        self.dialog = qw.QInputDialog(self.dialog_parent)
        self.dialog.setInputMode(qw.QInputDialog.InputMode.TextInput)
        self.dialog.setWindowTitle(f"Create new {kind}s")
        self.dialog.setLabelText(
            f'To create multiple {kind}s separate them by Comma:'
        )
        self.dialog.textValueChanged.connect(self.check_character)

        ok = self.dialog.exec_()
        names = self.dialog.textValue()
        if ok:
            names = names.split(",")
            for name in names:
                self.create_asset(kind, name, self.extension)
        
    def check_character(self, arg):
        if not arg:
            return
        last_char = arg[-1]
        if last_char in self.legal_chars:
            return
        last_char = self.save_char_map.get(last_char, "-")
        self.dialog.setTextValue(f"{arg[:-1]}{last_char}")

    def create_asset(self, kind, name, extension):
        if name not in [a.name for a in self.asset_provider.list_assets()]:
            asset = Asset(kind, name, extension)
            dep = asset.get_deps()[0]
            asset.new_version(dep, self.asset_provider.user_settings.username)
            asset.create_folders()
            proj_loc = Path(self.asset_provider.user_settings.local_project_location)
            mother_scene = self.asset_provider.settings.mother_scenes.get(
                dep, self.asset_provider.settings.mother_scenes["default"]
            )
            shutil.copy(proj_loc / mother_scene, asset.get_version(dep))
            cg3event.post("asset_created", asset)
        else:
            print(f"Asset {name} already exists. Ignored.")


class QuickFiler(MayaQWidgetDockableMixin, qw.QDialog):
    """Collection window for file related actions."""

    def __init__(self, asset_provider):
        super().__init__(maya_main_window())
        project_settings = get_project_settings()

        self.setGeometry(0, 0, 300, 500)
        cg3event.subscribe("asset_created", asset_provider.on_asset_created)

        self.main_layout = qw.QVBoxLayout(self)
        self.main_layout.setAlignment(qc.Qt.AlignTop)
        
        qfc = QuickAssetCreator(self, asset_provider, "ma")
        self.main_layout.addLayout(qfc)

        self.main_layout.addWidget(QHLine())

        qfo = QuickFileOpen(asset_provider)
        self.main_layout.addLayout(qfo)

        self.setWindowTitle("Quick Filer")
        self.show(dockable=True)
