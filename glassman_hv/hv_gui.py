import sys

from PyQt5 import QtCore, QtGui

from PyQt5.QtWidgets import (
    QWidget, QFrame,
    QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel,
    QLineEdit, QRadioButton, QPushButton
    )

from . HVController import HvController

class SupplyParameterDisplay(QFrame):



    def __init__(self,
        label : str = "test",
        unit :str = "",
        max_value : float = 1.):

        QFrame.__init__(self)
        # self.setFrameShape(QFrame.Box)
        self.label = label
        self.unit  = unit
        self.max_value = max_value

        layout = QHBoxLayout()

        self.label_widget = QLabel(self.label)
        layout.addWidget(self.label_widget)
        self.readbackWidget = QLabel("" +f"({self.unit})")
        self.readbackWidget.setStyleSheet("border: 1px solid black;")

        # help(self.readbackWidget)

        self.readbackWidget.setMinimumWidth(150)
        layout.addWidget(self.readbackWidget)

        self.setLayout(layout)


from enum import Enum
class Status(Enum):
    OFF     = 1
    ON      = 2
    FAULT   = 3
    UNKNOWN = 4

status_indicator_icons = {}
status_indicator_icons[Status.OFF]     = "glassman_hv/icons/gray-led-off.png"
status_indicator_icons[Status.ON]      = "glassman_hv/icons/green-led-on.png"
status_indicator_icons[Status.FAULT]   = "glassman_hv/icons/red-led-on.png"
status_indicator_icons[Status.UNKNOWN] = "glassman_hv/icons/blue-led-on.png"


class IndicatorAndLabel(QWidget):

    def __init__(self, label):
        QWidget.__init__(self)
        
        self.ICON = QLabel(self)
        self.ICON.setMaximumSize(QtCore.QSize(21,21))
        self.ICON.setText("")

        self.setStatus(Status.OFF)
      
        self.ICON.setScaledContents(True)
        self.ICON.setObjectName(label)
        self.ICON.show()

        self.LABEL = QLabel(label)

        # layout = QHBoxLayout()
        # layout.addWidget(self.ICON)
        # layout.addWidget(self.LABEL)
        # layout.addStretch()
        # self.setLayout(layout)

        # self.show()

    def setStatus(self, status : Status):
        print("status set to ", status)

        pixmap = QtGui.QPixmap(status_indicator_icons[status])

        self.ICON.setPixmap(pixmap)

        pass

class HVReadbackGui(QWidget):

    def __init__(self):

        QWidget.__init__(self)

        self.global_layout = QHBoxLayout()

        # Put indicators on the left, and readback values on the right

        self.indicators_top_layout = QVBoxLayout()

        self.indicators_layout = QFormLayout()

        # Indicators
        self.HV_ON_LED = IndicatorAndLabel("HV On")
        self.FAULT_LED = IndicatorAndLabel("Fault")
        self.HEARTBEAT_LED = IndicatorAndLabel("Heartbeat")
        self.indicators_layout.addRow(self.HV_ON_LED.ICON, self.HV_ON_LED.LABEL)
        self.indicators_layout.addRow(self.FAULT_LED.ICON, self.FAULT_LED.LABEL)
        self.indicators_layout.addRow(self.HEARTBEAT_LED.ICON, self.HEARTBEAT_LED.LABEL)

        self.indicators_top_layout.addStretch()
        self.indicators_top_layout.addLayout(self.indicators_layout)
        self.indicators_top_layout.addStretch()


        self.FAULT_LED.setStatus(Status.OFF)

        self.global_layout.addLayout(self.indicators_top_layout)

        # Read back values:

        self.readback_layout = QVBoxLayout()



        self.current_display = SupplyParameterDisplay(
            label = "Current",
            unit  = "mA",
            max_value = 5.
        )
        self.voltage_display = SupplyParameterDisplay(
            label = "Voltage",
            unit  = "kV",
            max_value = 125.
        )
        # self.readout_box = QHBoxLayout()
        self.readback_layout.addStretch()
        self.readback_layout.addWidget(self.current_display)
        self.readback_layout.addWidget(self.voltage_display)
        self.readback_layout.addStretch()

        self.global_layout.addLayout(self.readback_layout)

        self.setLayout(self.global_layout)

        self.show()

class SetParameterWithLabel(QWidget):

    def __init__(self, label : str, max_value : float, default : float):

        QWidget.__init__(self)

        layout = QHBoxLayout()

        layout.addStretch()

        self.label = label
        self.max   = max_value


        self.label_widget = QLabel(self.label)
        self.label_widget.setAlignment(QtCore.Qt.AlignRight)
        layout.addWidget(self.label_widget)

        self.entry_widget = QLineEdit()
        self.entry_widget.setText(str(default))

        layout.addWidget(self.entry_widget)

        self.setLayout(layout)

    def validate_input(self):
        pass

class HVSetGUI(QWidget):
    """
    This class describes a hv set gui.
    """

    def __init__(self):
        QWidget.__init__(self)

        # Control 3 parameters:
        #  - set voltage (max)
        #  - set current (max)
        #  - ramp rate in V / s
        #  
        #  Additionall, this gui sets the current/voltage limit.
        #  
        #  Finally, this GUI enables HV or not.

        self.global_layout = QHBoxLayout()


        self.parameter_set_layout = QVBoxLayout()

        self.voltage_setter = SetParameterWithLabel(
            label     = "Voltage (kV)", 
            max_value = 125.,
            default   = 0.)
        self.current_setter = SetParameterWithLabel(
            label     = "Current (mA)", 
            max_value = 5.,
            default   = 0.)
        self.ramp_setter    = SetParameterWithLabel(
            label     = "Ramp Rate (kV/s)",
            max_value = 0.1,
            default   = 0.01)

        self.parameter_set_layout.addWidget(self.voltage_setter)
        self.parameter_set_layout.addWidget(self.current_setter)
        self.parameter_set_layout.addWidget(self.ramp_setter)

        self.global_layout.addLayout(self.parameter_set_layout)


        self.enable_layout = QVBoxLayout()

        self.control_model_label = QLabel("Control Mode")
        self.control_mode_v = QRadioButton("Voltage")
        self.control_mode_c = QRadioButton("Current")

        self.set_values_button = QPushButton("Set Values")
        self.reset_button = QPushButton("Reset")

        self.enable_layout.addWidget(self.control_model_label)
        self.enable_layout.addWidget(self.control_mode_v)
        self.enable_layout.addWidget(self.control_mode_c)
        self.enable_layout.addWidget(self.set_values_button)
        self.enable_layout.addWidget(self.reset_button)

        self.global_layout.addLayout(self.enable_layout)

        self.setLayout(self.global_layout)

class HV_Gui(QWidget):
    """
    This class describes a hv graphical user interface.
    """

    def __init__(self):

        QWidget.__init__(self)

        self.layout = QVBoxLayout() 

        # Configure the readout box:

        self.HV_READBACK_GUI = HVReadbackGui()
        self.HV_SET_GUI      = HVSetGUI()


        self.layout.addWidget(self.HV_READBACK_GUI)
        self.layout.addWidget(self.HV_SET_GUI)


        self.setLayout(self.layout)

        # This is the class that communicates with the physical hardware:
        self.hv_controller = HvController()



# # -*- coding: utf-8 -*-
# """
# This example demonstrates the ability to link the axes of views together
# Views can be linked manually using the context menu, but only if they are given 
# names.
# """

# import initExample ## Add path to library (just for examples; you do not need this)


# from pyqtgraph.Qt import QtGui, QtCore
# import numpy as np
# import pyqtgraph as pg

# app = pg.mkQApp("Linked Views Example")
# #mw = QtGui.QMainWindow()
# #mw.resize(800,800)

# x = np.linspace(-50, 50, 1000)
# y = np.sin(x) / x

# win = pg.GraphicsLayoutWidget(show=True, title="pyqtgraph example: Linked Views")
# win.resize(800,600)

# win.addLabel("Linked Views", colspan=2)
# win.nextRow()

# p1 = win.addPlot(x=x, y=y, name="Plot1", title="Plot1")
# p2 = win.addPlot(x=x, y=y, name="Plot2", title="Plot2: Y linked with Plot1")
# p2.setLabel('bottom', "Label to test offset")
# p2.setYLink('Plot1')  ## test linking by name


# ## create plots 3 and 4 out of order
# p4 = win.addPlot(x=x, y=y, name="Plot4", title="Plot4: X -> Plot3 (deferred), Y -> Plot1", row=2, col=1)
# p4.setXLink('Plot3')  ## Plot3 has not been created yet, but this should still work anyway.
# p4.setYLink(p1)
# p3 = win.addPlot(x=x, y=y, name="Plot3", title="Plot3: X linked with Plot1", row=2, col=0)
# p3.setXLink(p1)
# p3.setLabel('left', "Label to test offset")
# #QtGui.QApplication.processEvents()

# if __name__ == '__main__':
#     pg.exec()
