import maya.cmds as mc
from maya import OpenMayaUI as omui

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2.QtUiTools import *
from shiboken2 import wrapInstance

import scale_frames
reload(scale_frames)

MAYA_WINDOW_POINTER = omui.MQtUtil.mainWindow()
MAYA_MAIN_WINDOW = wrapInstance(long(MAYA_WINDOW_POINTER), QWidget)

WIN_TITLE = "Keyframe Scaler"

class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow,self).__init__(MAYA_MAIN_WINDOW)
        self.setWindowFlags(Qt.Window)
        self.setWindowTitle(WIN_TITLE)

        self.is_selection = True
        self.is_first = True
        self.vertical = True

        grid = QGridLayout(self)
        grid.setAlignment(Qt.AlignTop)
        self.setLayout(grid)

        # Check box determines whether the scaling is happening for only selected keyframes or
        # all keyframes in the timeline
        check_box = QCheckBox("Scale selected only")
        check_box.setChecked(True)
        explanation_of_selection = QLabel("(If off will scale the while curve after or before"
                                          " the first or the last selected keyframe)")
        explanation_of_selection.setWordWrap(True)

        # Horizontal and Vertical buttons determine whether we scale time-wise or value-wise
        vertical_scale_button, horizontal_scale_button = self.add_toggle_buttons("V","H")

        # First and Last buttons determine the pivot from which the scaling is happening
        first_frame_button, last_frame_button = self.add_toggle_buttons("F","L")

        # Spin box determines how much are the keyframes getting scaled
        spin_box = QDoubleSpinBox()
        self.init_spin_box(spin_box)

        # This button will be responsible for the main functionality
        scale_button = QPushButton("Scale")

        first_frame_button.clicked.connect(lambda: self.toggle_button(first_frame_button,
                                                                      last_frame_button))
        last_frame_button.clicked.connect(lambda: self.toggle_button(last_frame_button,
                                                                     first_frame_button))

        vertical_scale_button.clicked.connect(lambda: self.toggle_button(vertical_scale_button,
                                                                         horizontal_scale_button))
        horizontal_scale_button.clicked.connect(lambda: self.toggle_button(horizontal_scale_button,
                                                                           vertical_scale_button))

        grid.addWidget(check_box, 0, 0, 1, 4)
        grid.addWidget(explanation_of_selection, 1, 0, 1, 4)
        grid.addWidget(vertical_scale_button, 2, 1, 1, 1)
        grid.addWidget(horizontal_scale_button, 2, 2, 1, 1)
        grid.addWidget(first_frame_button, 3, 0, 1, 1)
        grid.addWidget(spin_box, 3, 1, 1, 2)
        grid.addWidget(last_frame_button, 3, 3, 1, 1)
        grid.addWidget(scale_button, 4, 0, 1, 4)

        check_box.stateChanged.connect(lambda: self.set_selection(check_box.isChecked()))

        scale_button.clicked.connect(lambda: scale_frames.main(
            is_first=first_frame_button.isChecked(),
            are_selected_frames=self.is_selection,
            scale_amount=spin_box.value(),
            is_vertical=vertical_scale_button.isChecked()))

        self.show()

    def init_toggle_button(self, button):
        button.setCheckable(True)
        button.setDown(True)
        button.setChecked(True)

    def init_spin_box(self, spin_box):
        spin_box.setSingleStep(0.1)
        spin_box.setMinimum(float("-inf"))
        spin_box.setValue(0.5)

    def set_selection(self, is_selection):
        self.is_selection = is_selection

    def toggle_button(self, button, another_button):
        """
        Toggle for first and last buttons. Changes their down state depending on whether
        they are checked
        type: firstLast or horizontalVertical
        """
        if button.isChecked():
            button.setDown(True)
            if another_button.isChecked():
                another_button.setChecked(False)
                another_button.setDown(False)
        else:
            button.setDown(False)

    def add_toggle_buttons(self, selected_label, unselected_label):
        """
        Adds buttons that can be toggled of and on like first/last frames or vertical/horizontal
        """
        button01 = QPushButton(selected_label)
        button02 = QPushButton(unselected_label)
        self.init_toggle_button(button01)
        button02.setCheckable(True)
        return button01, button02


def main():
    MainWindow()


