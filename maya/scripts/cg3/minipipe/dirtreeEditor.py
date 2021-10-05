import os
from pathlib import Path
import tempfile
import shutil
import pprint

from maya.app.general.mayaMixin import MayaQWidgetDockableMixin

from PySide2.QtCore import Qt
#from PySide2.QtGui import 
from PySide2.QtWidgets import (
    QPushButton, QWidget, QVBoxLayout, QFileSystemModel, QLineEdit,
    QMainWindow, QTreeView, QMenu, QFileDialog, QInputDialog
)

from cg3.ui.windows import maya_main_window
from cg3.util.names import legalize_text
from cg3.file.dirtree import Dir


class DirtreeEditor(MayaQWidgetDockableMixin, QMainWindow):
    def __init__(self):
        super().__init__(maya_main_window())
        path = tempfile.mkdtemp()

        self.root_path = path

        show_info_btn = QPushButton("Show Info")
        show_info_btn.clicked.connect(self.show_info)

        toolbar = self.addToolBar("Tools")
        action = toolbar.addAction("Print Dirtree")
        action.triggered.connect(self.print_dirtree)
        action.setToolTip("Print the current Tree as Dictionary.")
        action = toolbar.addAction("Expand All")
        action.triggered.connect(self.expand_all)

        widget = QWidget()
        self.setCentralWidget(widget)
        self.main_vbox = QVBoxLayout(widget)

        self.model = QFileSystemModel()
        self.model.setRootPath("")

        self.tree_view = QTreeView()
        self.tree_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_view.customContextMenuRequested.connect(self.open_menu)
        self.tree_view.setModel(self.model)
        self.tree_view.setRootIndex(self.model.index(self.root_path))
        self.tree_view.hideColumn(1)  # size column
        self.tree_view.hideColumn(3)  # date modified column

        self.main_vbox.addWidget(self.tree_view)

        self.setLayout(self.main_vbox)

        self.setGeometry(300, 300, 350, 300)
        self.setWindowTitle('Dirtree Helper')
        self.show(dockable=True)

    def expand_all(self):
        self.tree_view.expandAll()

    def show_info(self):
        #print(self.tree_view.selectedIndexes())
        selected = self.tree_view.selectedIndexes()[0]
        #print(dir(selected))
        print(selected.data())
        file_path = self.model.filePath(selected)
        print(file_path[len(self.root_path):])

    def print_dirtree(self):
        filePath = Path(self.model.filePath(self.tree_view.rootIndex()))
        pprint.pprint(Dir().read_from_path(filePath))

    def get_index(self):
        indexes = self.tree_view.selectedIndexes()
        # if indexes is not empty: something is selected, else use root
        return self.tree_view.rootIndex() if not indexes else indexes[0]

    def open_menu(self, position):
        index = self.get_index()
        menu = QMenu()
        if self.model.isDir(index):
            menu.addAction("Add Folder(s)", self.add_multiple_folders)
            menu.addAction("Add File...", self.add_file)
        if index != self.tree_view.rootIndex():
            menu.addAction("Rename", self.rename)
            menu.addAction("Delete", self.delete)
        menu.exec_(self.tree_view.viewport().mapToGlobal(position))

    def add_file(self):
        index = self.get_index()
        file_path = self.model.filePath(index)

        fname = QFileDialog.getOpenFileName(self, 'Add File')
        if fname[0]:
            filename = os.path.basename(fname[0])
            shutil.copyfile(fname[0], os.path.join(file_path, filename))

    def add_multiple_folders(self):
        text, ok = QInputDialog.getText(
            self, 'Enter Foldernames', 'Commaseperated:')
        if ok:
            folders = [legalize_text(f.strip()) for f in text.split(",")]
            for folder in folders:
                self.add_folder(folder)

    def add_folder(self, foldername):
        index = self.get_index()

        self.model.layoutAboutToBeChanged.emit()
        self.model.mkdir(index, foldername)
        self.model.layoutChanged.emit()

        self.tree_view.expand(index)

    def delete(self):
        index = self.get_index()
    
        self.model.layoutAboutToBeChanged.emit()
        if self.model.isDir(index):
            #self.model.rmdir(index)
            file_path = self.model.filePath(index)
            shutil.rmtree(file_path)
        else:
            self.model.remove(index)
        self.model.layoutChanged.emit()

    def rename(self):
        index = self.get_index()
        file_path = self.model.filePath(index)
        dirname = os.path.dirname(file_path)
        filename = os.path.basename(file_path)

        text, ok = QInputDialog.getText(
            self, 'Rename', 'New Name:', QLineEdit.Normal, filename)
        if ok:
            os.rename(file_path, os.path.join(dirname, legalize_text(text,allow=".")))


#DirtreeEditor()

