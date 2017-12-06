from core.environnement import *
from GUI.overview_window import *

from PyQt5.QtWidgets import (QMainWindow, QWidget, QPushButton, QLineEdit, 
    QLabel, QFrame, QSpinBox, QGridLayout, QGroupBox, QHBoxLayout, 
    QVBoxLayout, QTabWidget, QAction)

env = environnement()

h = 400
w = 200

class MainWindow(QWidget):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.Set_UI()


    def Set_UI(self):
        self.resize(h, w)
        self.setWindowTitle(env.name)
        self.move(0, 0)
        new = Start_Window(self)


class Start_Window(QWidget):

    def __init__(self, root):
        super(QWidget, self).__init__(root)
        self.root = root
        self.Build_Swindow()

    def Build_Swindow(self):
        self.SFrame = QFrame(self)
        self.SFrame.resize(h, w)

        Glayout = QGridLayout()
        HBlayout = QHBoxLayout()
        VBlayout = QVBoxLayout()
        VBFrame = QFrame()

        gbox = QGroupBox("Environnement settings")

        self.train = QPushButton('Train')
        self.eval = QPushButton('Eval')
        self.leave = QPushButton('Exit')

        self.train.clicked.connect(self.Build_Train)
        self.eval.clicked.connect(self.Build_Eval)
        self.leave.clicked.connect(quit)

        lm = QLabel('Model : ')
        self.lem = QLineEdit()
        self.lem.setText(str(env.stock_name))

        lmo = QLabel('Max order : ')
        self.sbmo = QSpinBox()
        self.sbmo.setMaximum(1000)
        self.sbmo.setMinimum(1)
        self.sbmo.setValue(env.max_order)

        lcp = QLabel('Contract price : ')
        self.sbcp = QSpinBox()
        self.sbcp.setMaximum(1000)
        self.sbcp.setValue(env.contract_price)

        lpv = QLabel('Pip value : ')
        self.sbpv = QSpinBox()
        self.sbpv.setMaximum(1000)
        self.sbpv.setMinimum(1)
        self.sbpv.setValue(env.pip_value)

        ls = QLabel('Spread : ')
        self.sbs = QSpinBox()
        self.sbs.setMaximum(10)
        self.sbs.setMinimum(1)
        self.sbs.setValue(env.spread)

        Glayout.addWidget(lm, 0, 0)
        Glayout.addWidget(self.lem, 0, 1)

        Glayout.addWidget(lmo, 1, 0)
        Glayout.addWidget(self.sbmo, 1, 1)

        Glayout.addWidget(lcp, 2, 0)
        Glayout.addWidget(self.sbcp, 2, 1)

        Glayout.addWidget(lpv, 3, 0)
        Glayout.addWidget(self.sbpv, 3, 1)

        Glayout.addWidget(ls, 4, 0)
        Glayout.addWidget(self.sbs, 4, 1)

        gbox.setLayout(Glayout)

        VBlayout.addWidget(self.train)
        VBlayout.addWidget(self.eval)
        VBlayout.addWidget(self.leave)

        VBFrame.setLayout(VBlayout)

        HBlayout.addWidget(gbox)
        HBlayout.addWidget(VBFrame)

        self.SFrame.setLayout(HBlayout)

        #self.hide()

    def _resize(self):
        self.h = 1024
        self.w = 720
        self.root.resize(self.h, self.w)
        self.resize(self.h, self.w)

    def Hide_Swindow(self):
        self.SFrame.hide()


    def Show_Swindow(self):
        self.SFrame.show()

    def Build_Eval(self):
        env.mode = "eval"
        self.Build_Primary_Window()

    def Build_Train(self):
        env.mode = "train"
        self.Build_Primary_Window()

    def Build_Primary_Window(self):
        # Getting env settings

        self._resize()

        env.contract_price = self.sbcp.value()
        env.stock_name = self.lem.text()
        env.spread = self.sbs.value()
        env.max_order = self.sbmo.value()
        env.pip_value = self.sbpv.value()

        VLayout = QVBoxLayout(self)

        HLayout = QHBoxLayout()
        BF = QFrame()

        b_run = QPushButton('Run')
        b_pause = QPushButton('Pause')
        b_resume = QPushButton('Resume')

        HLayout.addWidget(b_run)
        HLayout.addWidget(b_pause)
        HLayout.addWidget(b_resume)
        HLayout.addWidget(self.leave)


        self.Hide_Swindow()

        self.primary_frame = QFrame(self)

        self.main_tab = QTabWidget()

        self.overview_tab = Overview_Window(self.main_tab, env)
        self.model_tab = QWidget()
        self.historic_tab = QWidget()

        self.main_tab.addTab(self.overview_tab, 'OverView')
        self.main_tab.addTab(self.model_tab, 'Model')
        self.main_tab.addTab(self.historic_tab, 'Historic')
        
        HLayout.setSpacing(20)

        BF.setLayout(HLayout)
        VLayout.addWidget(self.main_tab)
        VLayout.addWidget(BF)

        self.setLayout(VLayout)
