from core import Local_Worker as Worker
from environnement import Environnement
from .overview_window import Overview_Window
from .model_window import Model_Window

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

env = Environnement()

h = 950
w = 400

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

        gbox = QGroupBox("Settings")

        HBlayout = QHBoxLayout()
        HLayout = QHBoxLayout()
        VBlayout = QVBoxLayout()
        VBFrame = QFrame()

        self.train = QPushButton('Train')
        self.eval = QPushButton('Eval')
        self.leave = QPushButton('Exit')

        self.train.clicked.connect(self.Build_Train)
        self.eval.clicked.connect(self.Build_Eval)
        self.leave.clicked.connect(quit)

        HBlayout.addWidget(self.train)
        HBlayout.addWidget(self.eval)
        HBlayout.addWidget(self.leave)

        VBFrame.setLayout(HBlayout)

        gbox_es = self._build_env_settings()
        gbox_ws = self._build_wallet_settings()
        gbox_ms = self._build_model_settings()

        HLayout.addWidget(gbox_es)
        HLayout.addWidget(gbox_ws)
        HLayout.addWidget(gbox_ms)

        gbox.setLayout(HLayout)

        VBlayout.addWidget(gbox)
        VBlayout.addWidget(VBFrame)

        self.SFrame.setLayout(VBlayout)

    def _build_wallet_settings(self):
        Glayout = QGridLayout()
        gbox = QGroupBox("Wallet and risk settings")

        lc = QLabel('Capital : ')
        self.lec = QLineEdit()
        self.lec.setText(str(env.capital))

        lexposure = QLabel('Exposure : ')
        self.sbexposure = QSpinBox()
        self.sbexposure.setMinimum(0)
        self.sbexposure.setMaximum(90)
        self.sbexposure.setValue(env.exposure)

        lmpd = QLabel('Max pip loss : ')
        self.lempd = QLineEdit()
        self.lempd.setText(str(env.max_pip_drawdown))

        lmo = QLabel('Max pos : ')
        self.sbmo = QSpinBox()
        self.sbmo.setMinimum(1)
        self.sbmo.setValue(env.max_pos)

        Glayout.addWidget(lc, 0, 0)
        Glayout.addWidget(self.lec, 0, 1)
        Glayout.addWidget(lexposure, 1, 0)
        Glayout.addWidget(self.sbexposure, 1, 1)
        Glayout.addWidget(lmpd, 2, 0)
        Glayout.addWidget(self.lempd, 2, 1)
        Glayout.addWidget(lmo, 3, 0)
        Glayout.addWidget(self.sbmo, 3, 1)

        gbox.setLayout(Glayout)

        return gbox

    def _build_model_settings(self):
        Glayout = QGridLayout()
        gbox = QGroupBox("Model settings")

        lmn = QLabel('Name : ')
        self.lemn = QLineEdit()
        self.lemn.setText(str(env.model_name))

        llr = QLabel('Learning rate : ')
        self.lelr = QLineEdit()
        self.lelr.setText(str(env.learning_rate))

        lg = QLabel('Gamma : ')
        self.leg = QLineEdit()
        self.leg.setText(str(env.gamma))

        le = QLabel('Epsilon : ')
        self.lee = QLineEdit()
        self.lee.setText(str(env.epsilon))

        Glayout.addWidget(lmn, 0, 0)
        Glayout.addWidget(self.lemn, 0, 1)
        Glayout.addWidget(llr, 1, 0)
        Glayout.addWidget(self.lelr, 1, 1)
        Glayout.addWidget(lg, 2, 0)
        Glayout.addWidget(self.leg, 2, 1)
        Glayout.addWidget(le, 3, 0)
        Glayout.addWidget(self.lee, 3, 1)

        gbox.setLayout(Glayout)

        return gbox

    def _build_env_settings(self):
        Glayout = QGridLayout()
        gbox = QGroupBox("Environnement settings")

        lm = QLabel('Data : ')
        self.lem = QLineEdit()
        self.lem.setText(str(env.stock_name))

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

        lec = QLabel('Episodes : ')
        self.sbec = QSpinBox()
        self.sbec.setMinimum(1)
        self.sbec.setMaximum(10000)
        self.sbec.setValue(env.episode_count)

        lws = QLabel('Window size : ')
        self.sbws = QSpinBox()
        self.sbws.setMinimum(1)
        self.sbws.setMaximum(1000)
        self.sbws.setValue(env.window_size)

        lbs = QLabel('Batch size : ')
        self.sbbs = QSpinBox()
        self.sbbs.setMinimum(1)
        self.sbbs.setMaximum(1024)
        self.sbbs.setValue(env.batch_size)

        Glayout.addWidget(lm, 0, 0)
        Glayout.addWidget(self.lem, 0, 1)
        Glayout.addWidget(lcp, 1, 0)
        Glayout.addWidget(self.sbcp, 1, 1)
        Glayout.addWidget(lpv, 2, 0)
        Glayout.addWidget(self.sbpv, 2, 1)
        Glayout.addWidget(ls, 3, 0)
        Glayout.addWidget(self.sbs, 3, 1)
        Glayout.addWidget(lec, 4, 0)
        Glayout.addWidget(self.sbec, 4, 1)
        Glayout.addWidget(lws, 5, 0)
        Glayout.addWidget(self.sbws, 5, 1)
        Glayout.addWidget(lbs, 6, 0)
        Glayout.addWidget(self.sbbs, 6, 1)

        gbox.setLayout(Glayout)

        return gbox

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
        self.worker.sig_batch.connect(self.batch_up)
        self.worker.sig_episode.connect(self.episode_up)

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
        self.model = Model_Window(self.main_tab, env)
        self.settings = QWidget()
        self.wallet = QWidget()
        self.logs = QWidget()

        self.main_tab.addTab(self.overview, 'OverView')
        self.main_tab.addTab(self.model, 'Model')
        self.main_tab.addTab(self.wallet, 'Wallet')
        self.main_tab.addTab(self.logs, 'Logs')
        self.main_tab.addTab(self.settings, 'Settings')

        HLayout.setSpacing(20)

        BF.setLayout(HLayout)
        VLayout.addWidget(self.main_tab)
        VLayout.addWidget(BF)

        self.setLayout(VLayout)

    def update(self):
        self.overview.ordr = env.manage_orders(self.overview.ordr)
        self.overview.Update_Overview(env)
        self.model.update_step(env)

    def batch_up(self):
        self.model.update_batch(env)

    def episode_up(self):
        self.model.update_episode(env)
