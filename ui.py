import sys
import os

import numpy as np
import math
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from PyQt5.QtWidgets import (
    QAction, QApplication, QWidget, QPushButton, QFileDialog, QMainWindow, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QGroupBox, QHBoxLayout, QTabWidget
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot

from xlsx_parser import ReadExcel
from model import DataModel
from prediction import predict_y

class SelectView(QWidget):
    def __init__(self):
        super().__init__()
        self.button_open_file = QPushButton('Open file', self)
        self.button_open_file.clicked.connect(self.open_file)
        self.button_select_x = QPushButton('Select explanatory variables')
        self.button_select_y = QPushButton('Select objective variables')
        self.button_update_selection = QPushButton('Update selection')
        self.table = QTableWidget()
        self.set_layout()

    def set_layout(self):
        self.layout = QVBoxLayout()
        self.layout_select = QHBoxLayout()

        self.layout_select.addWidget(self.button_select_x)
        self.layout_select.addWidget(self.button_select_y)
        self.layout_select.addWidget(self.button_update_selection)

        self.layout.addWidget(self.button_open_file)
        self.layout.addWidget(self.table)
        self.layout.addLayout(self.layout_select)
        self.setLayout(self.layout)

    def open_file(self):
        initial_path = os.getcwd()
        path = QFileDialog.getOpenFileName(self, 'Open file', initial_path)[0]
        re = ReadExcel(path)
        self.xy_df = re.read_excel()
        self.table_update(self.xy_df)

    def table_update(self, xy_df):
        self.cols = xy_df.columns.tolist()
        yshape, xshape = xy_df.shape
        self.table.setRowCount(yshape)
        self.table.setColumnCount(xshape)
        self.table.setHorizontalHeaderLabels(self.cols)

        for i, col in enumerate(self.cols):
            for j in range(yshape):
                val = xy_df.iloc[j, i]
                val = str(val)
                self.table.setItem(i, j, QTableWidgetItem(val))

    def selected_cols(self):
        selected_cols = []
        for item in self.table.selectedItems():
            selected_cols.append(item.column())

        selected_cols = np.array(selected_cols)
        selected_cols = np.unique(selected_cols)
        return selected_cols


class PredictionView(QWidget):
    def __init__(self):
        super().__init__()
        self.button_ridge = QPushButton('Ridge', self)
        self.button_lasso = QPushButton('Lasso', self)
        self.button_svr = QPushButton('SVR_test', self)

        self.create_scatter_plot()
        self.set_layout()

    def set_layout(self):
        self.layout_select_est = QVBoxLayout()
        self.layout_select_est.addWidget(self.button_ridge)
        self.layout_select_est.addWidget(self.button_lasso)
        self.layout_select_est.addWidget(self.button_svr)

        self.layout_right = QVBoxLayout()
        self.layout_right.addWidget(self.FigureScatterCanvas)

        self.layout = QHBoxLayout()
        self.layout.addLayout(self.layout_select_est)
        self.layout.addLayout(self.layout_right)

        self.setLayout(self.layout)

    def create_scatter_plot(self):
        self.FigureScatter = plt.figure()
        self.FigureScatterCanvas = FigureCanvas(self.FigureScatter)

    def update_scatter_plot(self, x_list, y_list):
        n = len(y_list)
        for i, (x, y) in enumerate(zip(x_list, y_list)):
            self.axis = self.FigureScatter.add_subplot(math.ceil(n/2),2,i+1, figsize=(5, 5))
            self.axis.scatter(x, y)
        self.FigureScatterCanvas.draw()

    def predict(self, x, y_list):
        print(self.sender())
        print(self.button_ridge)
        button = self.sender()
        if button is self.button_ridge:
            est = 'Ridge'
        elif button is self.button_lasso:
            est = 'Lasso'
        elif button is self.button_svr:
            est = 'SVR'
        y_test_list_list, y_test_predict_list_list = predict_y(est, x, y_list)

        return y_test_list_list, y_test_predict_list_list
# class OptimizationView(QWidet):


class GAView(QWidget):
    def __init__(self):
        super().__init__()
        self.tabs = QTabWidget()
        self.tab1 = SelectView()
        self.tab2 = PredictionView()
        self.tab3 = QWidget()
        self.datamodel = DataModel()
        self._data_exchange()
        self._init_ui()
    
    def _data_exchange(self):
        self.tab1.button_select_x.clicked.connect(self._select_x)
        self.tab1.button_select_y.clicked.connect(self._select_y)

        self.tab2.button_ridge.clicked.connect(self._predict_plot)
        self.tab2.button_lasso.clicked.connect(self._predict_plot)
        self.tab2.button_svr.clicked.connect(self._predict_plot)

    def _init_ui(self):
        self.setGeometry(10, 10, 640, 480)
        self.tabs.addTab(self.tab1, "Select")
        self.tabs.addTab(self.tab2, "Prediction")
        self.tabs.addTab(self.tab3, "Optimization")

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

        self.show()

    def _select_x(self):
        col = np.array(self.tab1.cols)[self.tab1.selected_cols()]
        self.datamodel.x_col = col
        self.datamodel.x = self.tab1.xy_df[col]

    def _select_y(self):
        col = np.array(self.tab1.cols)[self.tab1.selected_cols()]
        self.datamodel.y_col = col
        self.datamodel.y = self.tab1.xy_df[col]
        print(self.datamodel.y)

    def _predict_plot(self):
        x = self.datamodel.x.values
        y_list = self.datamodel.y.values
        y_test_list_list, y_test_predict_list_list = self.tab2.predict(x, y_list)
        self.tab2.update_scatter_plot(y_test_list_list, y_test_predict_list_list)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ga_view = GAView()
    sys.exit(app.exec_())