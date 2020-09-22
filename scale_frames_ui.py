import maya.cmds as mc
from maya import OpenMayaUI as omui

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2.QtUiTools import *
from shiboken2 import wrapInstance

import scale_frames

# UI for keyframe scaling tool. In it we can specify whether we are scaling only selected frames, or
# all the frames that go either after the first or before the last; whether we scale vertically (by
# value) or horizontally (by time); and whether the pivot should be at the first or the last frame.
# The value is being changed in the input box - an instance of CustomSpinBox. The user can change
# that value either by inserting a new value or by middle mouse dragging. Qt's SpinBox doesn't have
# a dragging functionality, so a CustomSpinBox(QLineEdit) is created.
# The scale factor is being calculated on value change and is new inserted value devided by the
# previous one. That factor is then being passed to scale_frames.main() for further
# computation and changes to the keyframe values.


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
        self.is_vertical = True

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
        self.vertical_scale_button, self.horizontal_scale_button = self.add_toggle_buttons("V","H")

        # First and Last buttons determine the pivot from which the scaling is happening
        self.first_frame_button, self.last_frame_button = self.add_toggle_buttons("F","L")

        # Spin box determines how much are the keyframes getting scaled
        self.spine_box = CustomSpinBox(value=1.0, parent=None, on_value_change = scale_frames.main,
            is_first=self.first_frame_button.isChecked(),
            are_selected_frames=self.is_selection,
            is_vertical=self.is_vertical)
        self.init_spin_box(self.spine_box)

        self.first_frame_button.clicked.connect(lambda: self.on_press_first())
        self.last_frame_button.clicked.connect(lambda: self.on_press_last())

        self.vertical_scale_button.clicked.connect(lambda: self.on_press_vertical())
        self.horizontal_scale_button.clicked.connect(lambda: self.on_press_horizontal())

        grid.addWidget(check_box, 0, 0, 1, 4)
        grid.addWidget(explanation_of_selection, 1, 0, 1, 4)
        grid.addWidget(self.vertical_scale_button, 2, 1, 1, 1)
        grid.addWidget(self.horizontal_scale_button, 2, 2, 1, 1)
        grid.addWidget(self.first_frame_button, 3, 0, 1, 1)
        grid.addWidget(self.spine_box, 3, 1, 1, 2)
        grid.addWidget(self.last_frame_button, 3, 3, 1, 1)

        check_box.stateChanged.connect(lambda: self.set_selection(check_box.isChecked()))

        self.show()

    def init_toggle_button(self, button):
        button.setCheckable(True)
        button.setDown(True)
        button.setChecked(True)

    def init_spin_box(self, spine_box):
        spine_box.setSingleStep(0.1)
        spine_box.setMinimum(float("-inf"))

    def set_selection(self, is_selection):
        self.is_selection = is_selection
        self.spine_box.is_selection = is_selection

    def _toggle_button(self, pressed_button, unpressed_button):
        pressed_button.setDown(True)
        unpressed_button.setChecked(False)
        unpressed_button.setDown(False)

    def on_press_vertical(self):
        self._toggle_button(self.vertical_scale_button, self.horizontal_scale_button)
        self.spine_box.is_vertical = True

    def on_press_horizontal(self):
        self._toggle_button(self.horizontal_scale_button, self.vertical_scale_button)
        self.spine_box.is_vertical = False

    def on_press_first(self):
        self._toggle_button(self.first_frame_button, self.last_frame_button)
        self.spine_box.is_first = True

    def on_press_last(self):
        self._toggle_button(self.last_frame_button, self.first_frame_button)
        self.spine_box.is_first = False

    def add_toggle_buttons(self, selected_label, unselected_label):
        """
        Adds buttons that can be toggled of and on like first/last frames or vertical/horizontal
        """
        button01 = QPushButton(selected_label)
        button02 = QPushButton(unselected_label)
        self.init_toggle_button(button01)
        button02.setCheckable(True)
        return button01, button02

# This is taken from here, and modified:
# https://stackoverflow.com/questions/20922836/increases-decreases-qspinbox-value-when-click-drag-mouse-python-pyside
class CustomSpinBox(QLineEdit):
    """
    Tries to mimic behavior from Maya's internal slider that's found in the channel box.
    """

    IntSpinBox = 0
    DoubleSpinBox = 1

    def __init__(self, value=0, parent=None, on_value_change=None, **kwargs):
        super(CustomSpinBox, self).__init__(parent)

        self.setToolTip(
            "Hold and drag middle mouse button to adjust the value\n"
            "(Hold CTRL or SHIFT change rate)")

        self.setValidator(QDoubleValidator(parent=self))

        self.min = None
        self.max = None
        self.step = 0.1
        self.value_at_press = None
        self.pos_at_press = None
        self.on_value_change_function = on_value_change
        self.value_change_kwargs = kwargs
        self.anim_curve_info_dict = {}

        self.setValueText(value)
        self.value = value
        self.is_selection = self.value_change_kwargs["are_selected_frames"]
        self.is_vertical = self.value_change_kwargs["is_vertical"]
        self.is_first = self.value_change_kwargs["is_first"]

        self.textChanged.connect(self.onTextChanged)

    def onTextChanged(self, inserted_text):
        if inserted_text != "":
            new_value = float(inserted_text)
            old_value = float(self.value)
            if old_value!=0:
                self.scale_factor = new_value/old_value
            self.value = inserted_text

            if self.on_value_change_function:
                self.on_value_change_function(scale_factor=float(self.scale_factor),
                                              are_selected_frames=self.is_selection,
                                              is_vertical=self.is_vertical,
                                              is_first=self.is_first)

    def mousePressEvent(self, event):
        mc.undoInfo(openChunk=True)
        if event.buttons() == Qt.MiddleButton:
            self.value_at_press = self.getValue()
            self.pos_at_press = event.pos()
            self.setCursor(QCursor(Qt.SizeHorCursor))
        else:
            super(CustomSpinBox, self).mousePressEvent(event)
            self.selectAll()

    def mouseReleaseEvent(self, event):
        mc.undoInfo(closeChunk=True)
        if event.button() == Qt.MiddleButton:
            self.value_at_press = None
            self.pos_at_press = None
            self.setCursor(QCursor(Qt.IBeamCursor))
            return

        super(CustomSpinBox, self).mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):

        if event.buttons() != Qt.MiddleButton:
            return
        if self.pos_at_press is None:
            return

        steps_mult = self.getStepsMultiplier(event)

        delta = event.pos().x() - self.pos_at_press.x()
        delta /= 6  # Make movement less sensitive.
        delta *= self.step * steps_mult


        value = self.value_at_press + delta
        if value == 0:
            value += self.step * steps_mult
        self.setValueText(value)

        super(CustomSpinBox, self).mouseMoveEvent(event)

    def getStepsMultiplier(self, event):
        steps_mult = 1

        if event.modifiers() == Qt.CTRL:
            steps_mult = 10
        elif event.modifiers() == Qt.SHIFT:
            steps_mult = 0.1

        return steps_mult

    def setSingleStep(self, step):
        self.step = step

    def getValue(self):
        return float(self.text())

    def setMinimum(self, min):
        self.min = min

    def setMaximum(self, max):
        self.max = max

    def setValueText(self, value):
        if self.min is not None:
            value = max(value, self.min)

        if self.max is not None:
            value = min(value, self.max)

        self.setText(str(float(value)))


def main():
    MainWindow()