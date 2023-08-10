import sys
import matplotlib.pyplot as plt
from qasync import QEventLoop, asyncSlot
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QGraphicsScene
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QStringListModel, QModelIndex
import asyncio
from bleak import BleakScanner, BleakClient, BleakError

characteristic_uuid = "beb5483e-36e1-4688-b7f5-ea07361b26a8"

class Ui_MainWindow(object):
    def __init__(self):
        self.devices_data = {}

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.graphicsView = QtWidgets.QGraphicsView(self.centralwidget)
        self.graphicsView.setGeometry(QtCore.QRect(50, 80, 581, 391))
        self.graphicsView.setObjectName("graphicsView")

        self.listView = QtWidgets.QListView(self.centralwidget)
        self.listView.setGeometry(QtCore.QRect(650, 130, 120, 281))
        self.listView.setObjectName("listView")
        self.listView.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)

        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setGeometry(QtCore.QRect(650, 90, 120, 30))
        self.pushButton_2.setObjectName("pushButton_2")

        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(650, 420, 120, 30))
        self.pushButton.setObjectName("pushButton")

        MainWindow.setCentralWidget(self.centralwidget)

        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 17))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)

        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.pushButton_2.clicked.connect(lambda: asyncio.ensure_future(self.scan()))
        self.listView.clicked.connect(lambda index: asyncio.ensure_future(self.on_device_clicked(index)))
        self.pushButton.clicked.connect(lambda: self.save_graph())


    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.pushButton_2.setText(_translate("MainWindow", "scan"))
        self.pushButton.setText(_translate("MainWindow", "save"))

    async def scan(self):
        scanner = BleakScanner()
        self.devices = await scanner.discover()
        
        device_list = [device.name for device in self.devices]
        
        model = QStringListModel()
        model.setStringList(device_list)
        self.listView.setModel(model)

    async def on_device_clicked(self, index: QModelIndex):
        selected_indexes = self.listView.selectionModel().selectedIndexes()
        for index in selected_indexes:
            device = self.devices[index.row()]
            if device.name not in self.devices_data:
                self.devices_data[device.name] = []
                print(f"Attempting to connect to {device.name} at {device.address}")
                await self.connect_and_listen(device)

    async def connect_and_listen(self, device):
        client = BleakClient(device.address)
        try:
            await client.connect()
            if client.is_connected:
                print(f"Connected to {device.name}")
                await self.listen_to_data(client, device.name)
            else:
                print(f"Failed to connect to {device.name}")
        except BleakError as e:
            print(f"Error: {e}")
        finally:
            if client.is_connected:
                await client.disconnect()

    async def listen_to_data(self, client, device_name):
        while client.is_connected:
            value = await client.read_gatt_char(characteristic_uuid)
            self.devices_data[device_name].append(int.from_bytes(value, byteorder='little', signed=True))
            self.update_graph()

    def update_graph(self):
        plt.figure(figsize=(5.81, 3.91))
        for device_name, data in self.devices_data.items():
            plt.plot(data, label=device_name)
        plt.legend(loc='upper right')
        plt.savefig('temp_plot.png', dpi=100)

        pixmap = QPixmap('temp_plot.png')
        scene = QGraphicsScene()
        scene.addPixmap(pixmap)
        self.graphicsView.setScene(scene)

    def save_graph(self):
        plt.figure(figsize=(5.81, 3.91))
        for device_name, data in self.devices_data.items():
            plt.plot(data, label=device_name)
        plt.legend(loc='upper right')
        plt.savefig('graph.pdf')

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()

    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    with loop:
        loop.run_forever()
