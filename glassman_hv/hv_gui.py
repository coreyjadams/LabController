import sys

from PyQt5 import QtCore, QtGui

from PyQt5.QtWidgets import (
    QWidget, QFrame,
    QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QComboBox,
    QLineEdit, QRadioButton, QPushButton
    )


from . HVController import HvController

import pyqtgraph as pg
pg.setConfigOptions(antialias=True)

import numpy
max_dataframe_size = 10000

from serial.tools import list_ports

from datetime import datetime

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


        self.global_layout = QVBoxLayout()

        self.top_layout = QHBoxLayout()

        # Configure the readout box:

        hv_layout = QVBoxLayout()
        self.HV_READBACK_GUI = HVReadbackGui()
        self.HV_SET_GUI      = HVSetGUI()


        hv_layout.addWidget(self.HV_READBACK_GUI)
        hv_layout.addWidget(self.HV_SET_GUI)

        # We need a dropdown box for the port selection:
        ports = list_ports.comports()

        port_layout = QHBoxLayout()
        port_layout.addStretch()
        port_layout.addWidget(QLabel("HV Port"))
        self.port_list_widget = QComboBox()
        port_layout.addWidget(self.port_list_widget)

        self.hv_open = QPushButton("OPEN Port")
        self.hv_close = QPushButton("CLOSE Port")
        port_layout.addWidget(self.hv_open)
        port_layout.addWidget(self.hv_close)
        port_layout.addStretch()
        self.hv_open.clicked.connect(self.connect_hv)
        self.hv_close.clicked.connect(self.disconnect_hv)

        for p in ports:
            self.port_list_widget.addItem(p.name)

        hv_layout.addLayout(port_layout)
        hv_layout.addStretch()


        self.top_layout.addLayout(hv_layout)

        # This is the class that communicates with the physical hardware:
        self.hv_controller = HvController()


        # Storage locations for the data
        dtype = [
            ('time', "datetime64[us]"),
            ('voltage', 'float32'),
            ('current', 'float32'),
        ]
        self.hv_data = numpy.zeros(max_dataframe_size, dtype=dtype)
        self.active_index=0

        # Put the gui together:

        plot_layout = QVBoxLayout()
        # Add plots to display HV:

        date_axis = pg.graphicsItems.DateAxisItem.DateAxisItem(orientation = 'bottom')

        hv_win = pg.PlotWidget(show=True, title="Voltage")
        hv_win.setAxisItems(axisItems={'bottom' : date_axis})
        # hv_plot = hv_win.addPlot(title="High Voltage")
        self.hv_item = hv_win.getPlotItem()
        # hv_plot.addItem(self.hv_item)

        curr_win = pg.PlotWidget(show=True, title="Current")
        # curr_win.setAxisItems(axisItems={'bottom' : date_axis})

        # curr_plot = curr_win.addPlot(title="Current")
        self.curr_item = curr_win.getPlotItem()
        # curr_plot.addItem(self.curr_item)

        self.hv_item.setXLink(self.curr_item)

        plot_layout.addWidget(hv_win)
        plot_layout.addWidget(curr_win)

        self.top_layout.addLayout(plot_layout)
        self.global_layout.addLayout(self.top_layout)

        self.setLayout(self.global_layout)

        # self.start_hv_monitor()

    def connect_hv(self):
        '''
        open the port to the HV FT
        '''

        # Get the port selected in the GUI:
        port = self.port_list_widget.currentText()

        print("Current port: ", port)

        if self.hv_controller.device.is_open:
            print("WARNING: Port is already open.  Disconnect HV First!.")
            return

        self.hv_controller.openPortHV(port)

        # if the port opens successfully, start the HV monitoring:
        if self.hv_controller.device.is_open:
            self.start_hv_monitor()

    def disconnect_hv(self):
        '''
        Disconnect from the HV Supply
        '''
        if self.hv_controller.voltage != 0:
            qm  = QtGui.QMessageBox()
            ret = qm.Question("Warning!  Voltage is not 0, are you sure you want to disconnect?")

            if ret == qm.No: return

        if self.hv_controller.device.is_open:
            self.hv_controller.closePortHV()

    def start_hv_monitor(self):
        # Open the port for the HV:

        # Make connections to the supply.

        # A timer to query every 0.5 seconds the FT.
        self.hv_query_timer = QtCore.QTimer()
        self.hv_query_timer.setInterval(500) # time in ms
        self.hv_query_timer.timeout.connect(self.query_HV)
        self.hv_query_timer.start()


    def hv_fault(self):
        print("HV FAULT DETECTED, NO LOGIC IMPLEMENTED YET")

    def update_plots(self):

        # Set the data for the plot items.
        # Take the last 200 points, or as many points as we have,
        # whatever is less.

        max_points = 200
        n_points = numpy.min([self.active_index, max_points])

        # start poitn is either 0 or active_index - max_points,
        # whatever is less
        start_index = numpy.max([0, self.active_index - max_points])
        end_index = start_index + n_points

        print(start_index)
        print(end_index)

        print(self.hv_data.shape)

        times = self.hv_data[start_index:end_index]['time']
        v = self.hv_data[start_index:end_index]['voltage']
        i = self.hv_data[start_index:end_index]['current']

        self.hv_item.plot(times, v)
        self.curr_item.plot(times, i)


    def query_HV(self):
        '''
        Send a query command to the HV supply and readback the response.

        Additionally, ping the heartbeat and update the data points
        '''
        print("Query")
        self.hv_controller.queryHV()
        t = datetime.now()
        print(t)
        print(numpy.datetime64(t))
        if self.hv_controller.fault:
            self.hv_fault()



        # if hv on, blink the heartbeat:

        # Readback the values:
        self.hv_data[self.active_index]['time'] = numpy.datetime64(t)
        self.hv_data[self.active_index]['voltage'] = self.hv_controller.voltage
        self.hv_data[self.active_index]['current'] = self.hv_controller.current
        self.active_index += 1

        self.update_plots()

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
