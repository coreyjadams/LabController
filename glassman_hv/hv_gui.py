import sys
import time
from datetime import datetime, date
from teafiles import *

from PyQt5 import QtCore, QtGui
from PyQt5 import QtTest
from PyQt5.QtWidgets import (
    QWidget, QFrame, QCheckBox,
    QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QComboBox,
    QLineEdit, QRadioButton, QPushButton
    )



from . HVController import HvController

import pyqtgraph as pg
pg.setConfigOptions(antialias=True)

import numpy
max_dataframe_size = 100000 

from serial.tools import list_ports

from datetime import datetime, timedelta

class TimeAxisItem(pg.AxisItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def tickStrings(self, values, scale, spacing):
        return [ str(self.int2dt(value)) for value in values]
        # return [ str(self.int2dt(value)).strftime("%H:%M:%S") for value in values]

    def int2dt(self, ts, ts_mult=1e6):
        return (timedelta(seconds=float(ts)/ts_mult))

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

    def updateText(self, value):
        self.readbackWidget.setText(f"{value:.3f} ({self.unit})")


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

        pixmap = QtGui.QPixmap(status_indicator_icons[status])

        self.ICON.setPixmap(pixmap)
        self.STATUS = status
        pass

    def heartbeat(self, status : Status = Status.UNKNOWN):
        # return
        original_status = self.STATUS
        self.setStatus(status)
        self.ICON.repaint()
        # self.repaint()
        time.sleep(0.1)
        self.setStatus(original_status)


class HVReadbackGui(QWidget):

    stepping = QtCore.pyqtSignal(float)

    def __init__(self):

        QWidget.__init__(self)

        self.global_layout = QVBoxLayout()
        self.global_layout.addStretch()
        self.one_down_layout = QHBoxLayout()
        # Put indicators on the left, and readback values on the right

        #This one is the highest indicator layout on the left
        self.indicators_top_layout = QVBoxLayout()

        self.indicators_layout = QFormLayout()

        # Indicators
        self.HV_ON_LED = IndicatorAndLabel("HV On")
        self.FAULT_LED = IndicatorAndLabel("Fault")
        self.HEARTBEAT_LED = IndicatorAndLabel("Heartbeat")
        self.indicators_layout.addRow(self.HV_ON_LED.ICON, self.HV_ON_LED.LABEL)
        self.indicators_layout.addRow(self.FAULT_LED.ICON, self.FAULT_LED.LABEL)
        self.indicators_layout.addRow(self.HEARTBEAT_LED.ICON, self.HEARTBEAT_LED.LABEL)

        # self.indicators_top_layout.addStretch()
        self.indicators_top_layout.addLayout(self.indicators_layout)
        # self.indicators_top_layout.addStretch()


        self.FAULT_LED.setStatus(Status.OFF)

        self.one_down_layout.addLayout(self.indicators_top_layout)

        # Read back values:




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
        self.readback_layout = QVBoxLayout()

        self.readback_layout.addStretch()
        self.readback_layout.addWidget(self.current_display)
        self.readback_layout.addWidget(self.voltage_display)

        self.top_control_mode_space = QHBoxLayout()
        self.top_control_mode_space.addStretch()
        self.control_mode_label = QLabel("Control Mode")
        self.top_control_mode_space.addWidget(self.control_mode_label)
        self.top_control_mode_space.addStretch()


        self.bottom_control_mode_space = QHBoxLayout()
        self.control_mode_v = IndicatorAndLabel("Voltage")
        self.control_mode_c = IndicatorAndLabel("Current")
        self.bottom_control_mode_space.addStretch()
        self.bottom_control_mode_space.addWidget(self.control_mode_v.ICON)
        self.bottom_control_mode_space.addWidget(self.control_mode_v.LABEL)
        self.bottom_control_mode_space.addStretch()
        self.bottom_control_mode_space.addWidget(self.control_mode_c.ICON)
        self.bottom_control_mode_space.addWidget(self.control_mode_c.LABEL)
        self.bottom_control_mode_space.addStretch()

        self.control_mode_holder = QVBoxLayout()

        self.control_mode_holder.addLayout(self.top_control_mode_space)
        self.control_mode_holder.addLayout(self.bottom_control_mode_space)

        self.readback_layout.addLayout(self.control_mode_holder)
        self.readback_layout.addStretch()
        self.readback_layout.addStretch()



        self.one_down_layout.addLayout(self.readback_layout)
        self.global_layout.addLayout(self.one_down_layout)

        self.setLayout(self.global_layout)

        self.show()

    def setControlMode(self, mode):

        if mode not in ["current", "voltage"]:
            print(f"ERROR: unknown control mode {mode}")

        if mode == "voltage":
            self.control_mode_v.setStatus(Status.ON)
            self.control_mode_c.setStatus(Status.OFF)
            return

        elif mode == "current":
            self.control_mode_v.setStatus(Status.OFF)
            self.control_mode_c.setStatus(Status.ON)


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

        self.set_values_button = QPushButton("Set Values")        
        self.reset_button = QPushButton("Reset")


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


        # This is the class that communicates with the physical hardware:
        self.hv_controller = HvController()

        self.global_layout = QVBoxLayout()

        self.top_layout = QHBoxLayout()

        # Configure the readout box:

        hv_layout = QVBoxLayout()
        self.HV_READBACK_GUI = HVReadbackGui()
        self.HV_SET_GUI      = HVSetGUI()

        self.HV_SET_GUI.reset_button.clicked.connect(
            self.hv_controller.resetHV
        )

        self.HV_SET_GUI.set_values_button.clicked.connect(
            self.set_hv
        )



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


        # Storage locations for the data
        dtype = [
            ('elapsed_time',    'float32'),
            ('voltage', 'float32'),
            ('current', 'float32'),
        ]
        self.hv_data = numpy.zeros(max_dataframe_size, dtype=dtype)
        self.active_index=0

        # Put the gui together:

        plot_layout = QVBoxLayout()
        # Add plots to display HV:

        # date_axis = pg.graphicsItems.DateAxisItem.DateAxisItem(orientation = 'bottom')

        hv_win = pg.PlotWidget(show=True, title="Voltage")
        hv_win.enableAutoRange("y",False)
        hv_win.setAspectLocked(lock=False)
        hv_win.setAutoVisible(y=1.0)
        hv_win.setAxisItems(axisItems={'bottom' : pg.DateAxisItem(orientation='bottom')})

        # hv_plot = hv_win.addPlot(title="High Voltage")
        self.hv_item = hv_win.getPlotItem()
        self.hv_plot = self.hv_item.plot(pen='y')
        self.hv_item.showGrid(x=True, y=True)
        # hv_plot.addItem(self.hv_item)

        curr_win = pg.PlotWidget(show=True, title="Current")
        curr_win.enableAutoRange(False)
        curr_win.setAxisItems(axisItems={'bottom' : pg.DateAxisItem(orientation='bottom')})
        # curr_win.setAxisItems(axisItems={'bottom' : date_axis})

        new_var = 'nmew'

        # curr_plot = curr_win.addPlot(title="Current")
        self.curr_item = curr_win.getPlotItem()
        self.curr_plot = self.curr_item.plot(pen='y')
        self.curr_item.showGrid(x=True, y=True)

        self.hv_item.setXLink(self.curr_item)

        self.auto_range = QCheckBox("AutoRange")
        self.auto_range.setChecked(True)

        self.plot_control = QHBoxLayout()
        self.plot_control.addWidget(self.auto_range)

        plot_layout.addWidget(hv_win)
        plot_layout.addWidget(curr_win)
        plot_layout.addLayout(self.plot_control)

        self.top_layout.addLayout(plot_layout)
        self.global_layout.addLayout(self.top_layout)

        self.setLayout(self.global_layout)

    def set_hv(self):
        '''
        Update the HV.
        '''
        #self.starting_time = time.time()
        # Block signals to the set button until completion:
        self.HV_SET_GUI.blockSignals(True)

        # First, capture the target values
        global target_hv
        target_hv   = float(self.HV_SET_GUI.voltage_setter.entry_widget.displayText())
        global target_curr        
        target_curr = float(self.HV_SET_GUI.current_setter.entry_widget.displayText())
        
        target_ramp = float(self.HV_SET_GUI.ramp_setter.entry_widget.displayText())


        print(target_hv)
        print(target_curr)
        print(target_ramp)

        self.ramp_rate = target_ramp


        
        #################################
        # THIS IF ELSE IS ABOUT THE RAMP RATE
        ################################# 

        # What is the set mode?

        if target_ramp == 0.0 or 0:
            # directly set the voltage:
            self.hv_controller.setHV(target_hv, target_curr)

        else:
            self.update_voltage()
                     
            
            
        self.HV_SET_GUI.set_values_button.blockSignals(False)



    def update_voltage(self):
        current_voltage = self.hv_controller.voltage
        target_voltage = target_hv
        diff = numpy.abs(target_voltage - current_voltage)
        ramp_rate = self.ramp_rate
        nsteps = int(numpy.abs(diff / ramp_rate))
        step_size = diff*self.ramp_rate
        duration = diff/ramp_rate
        pause = float(duration/nsteps)
        self.counter = 0

        if target_voltage > current_voltage:
            self.voltage1 = numpy.linspace(current_voltage,target_hv,nsteps-1)            
        
            for voltages in self.voltage1:
                    self.hv_controller.setHV(voltages,target_curr)
                    
                    QtTest.QTest.qWait(int(float('{0:1.0f}'.format(pause*1000))))
        else:
            self.voltage2 = numpy.linspace(current_voltage,target_hv,nsteps+1)
            
            for voltages in self.voltage2:
                    self.hv_controller.setHV(voltages,target_curr)
                    
                    QtTest.QTest.qWait(int(float('{0:1.0f}'.format(pause*1000))))



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
            self.hv_query_timer.stop()

    def start_hv_monitor(self):
        # Open the port for the HV:

        # Make connections to the supply.

        # A timer to query every 0.5 seconds the FT.
        self.hv_query_timer = QtCore.QTimer()
        self.hv_query_timer.setInterval(500) # time in ms
        self.hv_query_timer.timeout.connect(self.query_HV)
        self.hv_query_timer.start()

        self.start_time = time.time()
        
        self.curr_date = datetime.now()
        self.str_date = 'hvps_' + datetime.now().isoformat("_")+'.tea'
        self.str_name = self.str_date[:24].replace(':', ".") + '.tea'
        #self.str_date = 'hvps3_31_mar_2023.tea'
        self.open_t_file()
    
    def hv_fault(self):
        print("HV FAULT DETECTED, NO LOGIC IMPLEMENTED YET")

    def auto_range_plots(self):
        self.auto_range = True

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


        times =  self.hv_data[start_index:end_index]['elapsed_time']
        # times =  [timedelta(t) / 1e6 for t in times]
        # times = numpy.arange(start_index, end_index)
        v = self.hv_data[start_index:end_index]['voltage']
        i = self.hv_data[start_index:end_index]['current']


        self.hv_plot.setData(times, v)
        self.curr_plot.setData(times, i)
        if self.auto_range.checkState():
            self.hv_item.setXRange(times[0], times[-1], padding=0)
        # self.curr_item.plot(times, i)


    def query_HV(self):
        '''
        Send a query command to the HV supply and readback the response.

        Additionally, ping the heartbeat and update the data points
        '''
        self.hv_controller.queryHV()
        t = time.time()


        if self.hv_controller.fault:
            self.hv_fault()

        self.HV_READBACK_GUI.HEARTBEAT_LED.heartbeat()

        # if hv on, blink the heartbeat:

        # Readback the values:
        self.hv_data[self.active_index]['elapsed_time'] = t - self.start_time
        self.hv_data[self.active_index]['voltage'] = self.hv_controller.voltage
        self.hv_data[self.active_index]['current'] = self.hv_controller.current
        self.active_index += 1

        self.HV_READBACK_GUI.setControlMode(self.hv_controller.ctrlMode)

        self.HV_READBACK_GUI.voltage_display.updateText(self.hv_controller.voltage)
        self.HV_READBACK_GUI.current_display.updateText(self.hv_controller.current)
        # voltage_display


        self.update_plots()

        self.write_t_file()
        
        
        


    def open_t_file(self):
        self.filename = self.str_name
        self.tf = TeaFile.create(self.filename, "Time Voltage Current", "qdd","hvps measurements")  # change date format !!!!
        print(self.filename)
    
    def write_t_file(self):
        hoje = datetime.today().isoformat()
        hj_iso = datetime.fromisoformat(str(hoje))
        t = (time.time() - self.start_time)*1000
        TeaFile.openread(self.filename)
        self.tf.write(DateTime.parse(f'{str(hj_iso.year)}-{str(hj_iso.month)}-{str(hj_iso.day)}','%Y-%m-%d') + Duration(ticks = t)
        ,  self.hv_controller.voltage
        ,  self.hv_controller.current)
        




    
    
 
