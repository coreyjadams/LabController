import sys

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QApplication

class SupplyParameterDisplay(QWidget):



    def __init__(self,
        label : str = "test",
        unit :str = "",
        max_value : float = 1.):

        QWidget.__init__(self)

        self.label = label
        self.unit  = unit
        self.max_value = max_value

        layout = QVBoxLayout()

        sub_layout = QHBoxLayout()

        self.label_widget = QLabel(self.label)
        layout.addWidget(self.label_widget)
        self.readbackWidget = QLabel("" +self.unit)

        layout.addWidget(self.readbackWidget)

        self.setLayout(layout)




class HV_Gui(QWidget):

    def __init__(self):

        QWidget.__init__(self)


        layout = QVBoxLayout()

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

        layout.addWidget(self.current_display)
        layout.addWidget(self.voltage_display)

        self.setLayout(layout)
