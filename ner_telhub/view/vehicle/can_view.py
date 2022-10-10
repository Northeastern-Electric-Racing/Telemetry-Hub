from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QLineEdit, 
    QHBoxLayout, QVBoxLayout, QWidget,
    QSlider, QMenu, QSpinBox, QListView, QGridLayout,
    QCheckBox
)
from PyQt6.QtGui import QAction, QPalette, QColor
from PyQt6.QtCore import QSize, Qt

from ner_telhub.widgets.menu_widgets import NERButton


class ReceiveFilters(QWidget):
    """
    Section to define inputs for adding receive filters.
    """
    
    def __init__(self, model):
        super(ReceiveFilters, self).__init__()

        # Define basic widgets
        self.header = QLabel("Receive Filters")
        self.id_entry = QLineEdit()
        self.interval_entry = QLineEdit()

        self.filter_view = QListView()
        self.model = model
        self.filter_view.setModel(self.model)

        self.add_button = NERButton("Add", "BLUE")
        self.del_button = NERButton("Delete", "RED")
        self.add_button.pressed.connect(self.add)
        self.del_button.pressed.connect(self.delete)

        # Style basic widgets
        self.header.setStyleSheet("font-size: 30px; font-weight: bold")
        self.header.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        
        inputs_layout = QGridLayout()
        inputs_layout.addWidget(QLabel("ID:"), 0, 0)
        inputs_layout.addWidget(self.id_entry, 0, 1)
        inputs_layout.addWidget(QLabel("Interval (ms):"), 0, 2)
        inputs_layout.addWidget(self.interval_entry, 0, 3)

        buttons_layout = QVBoxLayout()
        buttons_layout.addWidget(self.add_button)
        buttons_layout.addWidget(self.del_button)

        display_layout = QHBoxLayout()
        display_layout.addWidget(self.filter_view)
        display_layout.addLayout(buttons_layout)

        layout = QVBoxLayout()
        layout.addWidget(self.header)
        layout.addLayout(inputs_layout)
        layout.addLayout(display_layout)
        self.setLayout(layout)

    def add(self):
        try:
            id = int(self.id_entry.text())
            interval = int(self.interval_entry.text())

            print("Adding Filter:")
            print("  id - ", id)
            print("  interval - ", interval)

            self.model.addFilter(id, interval)

        except Exception as e:
            # TODO: Add popup window for error
            print("Error with the fields")

        self.id_entry.setText("")
        self.interval_entry.setText("")

    def delete(self):
        indexes = self.filter_view.selectedIndexes()
        if indexes:
            index = indexes[0]
            self.model.deleteFilter(index)
            self.filter_view.clearSelection()



class SendFilters(QWidget):
    """
    Section to define inputs for adding send filters.
    """

    def __init__(self, model):
        super(SendFilters, self).__init__()

        # Define basic widgets
        self.header = QLabel("Send Filters")
        self.id_entry = QLineEdit()
        self.interval_entry = QLineEdit()
        self.data_entry = QLineEdit()
        self.repeat_send_entry = QCheckBox()

        self.filter_view = QListView()
        self.model = model
        self.filter_view.setModel(self.model)

        self.add_button = NERButton("Add", "BLUE")
        self.del_button = NERButton("Delete", "RED")
        self.add_button.pressed.connect(self.add)
        self.del_button.pressed.connect(self.delete)

        # Style basic widgets
        self.header.setStyleSheet("font-size: 30px; font-weight: bold")
        self.header.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        
        inputs_layout = QGridLayout()
        inputs_layout.addWidget(QLabel("ID:"), 0, 0)
        inputs_layout.addWidget(self.id_entry, 0, 1)
        inputs_layout.addWidget(QLabel("Interval (ms):"), 0, 2)
        inputs_layout.addWidget(self.interval_entry, 0, 3)
        inputs_layout.addWidget(QLabel("Data:"), 1, 0)
        inputs_layout.addWidget(self.data_entry, 1, 1)
        inputs_layout.addWidget(QLabel("Send Once:"), 1, 2)
        inputs_layout.addWidget(self.repeat_send_entry, 1, 3)

        buttons_layout = QVBoxLayout()
        buttons_layout.addWidget(self.add_button)
        buttons_layout.addWidget(self.del_button)

        display_layout = QHBoxLayout()
        display_layout.addWidget(self.filter_view)
        display_layout.addLayout(buttons_layout)

        layout = QVBoxLayout()
        layout.addWidget(self.header)
        layout.addLayout(inputs_layout)
        layout.addLayout(display_layout)
        self.setLayout(layout)

    def add(self):
        try:
            id = int(self.id_entry.text())
            interval = 0
            data = self.data_entry.text()
            data = [int(s) for s in data.split(" ")]

            if not self.repeat_send_entry.isChecked():  
                interval = int(self.interval_entry.text())

            print("Adding Filter:")
            print("  id - ", id)
            print("  interval - ", interval)
            print("  data - ", data)

            self.model.addFilter(id, interval, data)

        except Exception as e:
            # TODO: Add popup window for error
            print("Error with the fields")

        self.id_entry.setText("")
        self.interval_entry.setText("")
        self.data_entry.setText("")
        self.repeat_send_entry.setChecked(False)

    def delete(self):
        indexes = self.filter_view.selectedIndexes()
        if indexes:
            index = indexes[0]
            self.model.deleteFilter(index)
            self.filter_view.clearSelection()



class MessageFeed(QWidget):
    """
    Section showing the current message feed.
    """
    
    def __init__(self, model):
        super(MessageFeed, self).__init__()

        self.feed_started = False

        self.view = QListView()
        self.model = model
        self.view.setModel(self.model)

        self.play_button = NERButton("Start", "GREEN")
        self.play_button.pressed.connect(self.play)

        layout = QVBoxLayout()
        layout.addWidget(self.view)
        layout.addWidget(self.play_button)

        self.setLayout(layout)

    def play(self):
        self.feed_started = not self.feed_started

        if self.feed_started:
            self.play_button.setText("Stop")
            self.play_button.changeColor("RED")
            # TODO: Start printing messages
        else:
            self.play_button.setText("Start")
            self.play_button.changeColor("GREEN")
            # TODO: Stop printing Messages



class CanView(QWidget):
    """
    Main CAN view class.
    """
    
    def __init__(self, message_model, receive_filter_model, send_filter_model):
        super(CanView, self).__init__()

        filter_layout = QVBoxLayout()
        filter_layout.addWidget(ReceiveFilters(receive_filter_model))
        filter_layout.addWidget(SendFilters(send_filter_model))
        
        layout = QHBoxLayout()
        layout.addWidget(MessageFeed(message_model))
        layout.addLayout(filter_layout)

        self.setLayout(layout)