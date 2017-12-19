from core import Worker
from environnement import Environnement
from .overview_window import Overview_Window

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

env = Environnement()

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
        Start_Window(self)


class Start_Window(QWidget):

    def __init__(self, root):
        super(QWidget, self).__init__(root)
        #env.ui = self
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

        lmo = QLabel('Max pos : ')
        self.sbmo = QSpinBox()
        self.sbmo.setMaximum(1000)
        self.sbmo.setMinimum(1)
        self.sbmo.setValue(env.max_pos)

        lcp = QLabel('Contract price : ')
        self.sbcp = QSpinBox()
        self.sbcp.setMaximum(1000)
        self.sbcp.setMinimum(1)
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
        self.h = 1855
        self.w = 1050
        self.root.resize(self.h, self.w)
        self.resize(self.h, self.w)
        self.root.showMaximized()

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
        self._resize()
        
        self.worker = Worker(env)
        self.worker.sig_step.connect(self.update)

        # Getting env settings
        env.contract_price = self.sbcp.value()
        env.stock_name = self.lem.text()
        env.spread = self.sbs.value()
        env.max_pos = self.sbmo.value()
        env.pip_value = self.sbpv.value()

        VLayout = QVBoxLayout(self)
        HLayout = QHBoxLayout()
        BF = QFrame()

        b_run = QPushButton('Run')
        b_pause = QPushButton('Pause')
        b_resume = QPushButton('Resume')

        b_run.clicked.connect(self.worker.start)
        b_pause.clicked.connect(env._pause)
        b_resume.clicked.connect(env._resume)

        HLayout.addWidget(b_run)
        HLayout.addWidget(b_pause)
        HLayout.addWidget(b_resume)
        HLayout.addWidget(self.leave)

        self.Hide_Swindow()

        self.main_tab = QTabWidget()

        self.overview = Overview_Window(self.main_tab, env)
        self.model = QWidget()
        self.historic = QWidget()

        self.main_tab.addTab(self.overview, 'OverView')
        self.main_tab.addTab(self.model, 'Model')
        self.main_tab.addTab(self.historic, 'Historic')

        HLayout.setSpacing(20)

        BF.setLayout(HLayout)
        VLayout.addWidget(self.main_tab)
        VLayout.addWidget(BF)

        self.setLayout(VLayout)

    def update(self):
        self.overview.ordr = env.manage_orders(self.overview.ordr)
        self.overview.Update_Overview(env)
