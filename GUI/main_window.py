from core import Local_Worker as Worker
from environnement import Environnement
from .overview_window import Overview_Window
from .model_window import Model_Window

import os

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

env = Environnement()

h = 950
w = 500

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
        self.error = False
        self.Wtrain = None
        self.Weval = None
        self.Build_Swindow()

    def Build_Swindow(self):
        self.StFrame = QFrame(self)

        gbox = QGroupBox("Settings")

        HBlayout = QHBoxLayout()
        VBlayout = QVBoxLayout()
        VBFrame = QFrame()

        self.VFLayout = QVBoxLayout()

        self.SFrame = QFrame()
        SVbox = QVBoxLayout()

        RBgbox = QGroupBox("Mode")
        HRBlayout = QHBoxLayout()

        self.rbtrain = QRadioButton("Train")
        self.rbeval = QRadioButton("Eval")

        self.rbtrain.toggled.connect(lambda: self.Show_f(self.rbtrain.text()))
        self.rbeval.toggled.connect(lambda: self.Show_f(self.rbeval.text()))

        HRBlayout.addWidget(self.rbtrain)
        HRBlayout.addWidget(self.rbeval)

        HRBlayout.setAlignment(Qt.AlignHCenter)
        HRBlayout.setSpacing(350)

        RBgbox.setLayout(HRBlayout)

        self.next = QPushButton('Next')
        self.leave = QPushButton('Exit')

        self.next.clicked.connect(self.check_error)
        self.leave.clicked.connect(quit)

        HBlayout.addWidget(self.leave)
        HBlayout.addWidget(self.next)

        VBFrame.setLayout(HBlayout)
        gbox.setLayout(self.VFLayout)
        SVbox.addWidget(gbox)
        self.SFrame.setLayout(SVbox)

        self.lerror = QLabel()

        self.SFrame.hide()

        VBlayout.addWidget(RBgbox)
        VBlayout.addWidget(self.lerror)
        VBlayout.addWidget(self.SFrame)
        VBlayout.addWidget(VBFrame)
        VBlayout.addStretch()

        self.lerror.setAlignment(Qt.AlignHCenter)

        self.StFrame.setLayout(VBlayout)

        self.StFrame.resize(h, w)
        self.root.resize(h, 150)

    def _Build(self, mode):
        Frame = QFrame()
        Frame.setObjectName("Frame"+mode)
        #Frame.hide()

        HLayout = QHBoxLayout()

        gbox_es = self._build_env_settings(mode)
        gbox_ws = self._build_wallet_settings(mode)
        gbox_ms = self._build_model_settings(mode)

        HLayout.addWidget(gbox_es)
        HLayout.addWidget(gbox_ws)
        HLayout.addWidget(gbox_ms)

        Frame.setLayout(HLayout)

        return Frame

    def clearLayout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget() is not None:
                child.widget().deleteLater()
            else:
                clearLayout(child.layout())

    def Show_f(self, frame):
        if frame == "Train":
            self.StFrame.resize(h, w)
            self.root.resize(h, w)
            self.clearLayout(self.VFLayout)
            self.Wtrain = self.BuildTrain()
            self.VFLayout.addWidget(self.Wtrain)
        elif frame == "Eval":
            self.StFrame.resize(h, 425)
            self.root.resize(h, 425)
            self.clearLayout(self.VFLayout)
            self.Weval = self.BuildEval()
            self.VFLayout.addWidget(self.Weval)
        self.SFrame.show()
        self.error = False
        self.color_error()
        self.lerror.setText('')
        self.lerror.setStyleSheet("QLabel {background-color : }")

    def BuildTrain(self):
        env.mode = "train"
        return self._Build(env.mode)

    def BuildEval(self):
        env.mode = "eval"
        return self._Build(env.mode)

    def check_error(self):
        if self.error is False:
            self.Build_Primary_Window()

    def color_error(self):
        if self.error is True:
            self.next.setStyleSheet("QPushButton {color: grey}")
        else:
            self.next.setStyleSheet("QPushButton {color: }")

    def check_changed_lr(self, value):
        try:
            ret = float(value)
            if ret >= 1 or ret == 0:
                if ret >= 1:
                    self.lerror.setText('Learning rate >= 1')
                elif ret == 0:
                    self.lerror.setText('Learning rate == 0')
                self.lelr.setStyleSheet("QLineEdit {border-color : red}")
                self.lerror.setStyleSheet("QLabel {background-color : red}")
                self.error = True
            else:
                self.lelr.setStyleSheet("QLineEdit {border-color : }")
                self.lerror.setStyleSheet("QLabel {background-color : }")
                self.lerror.setText('')
                self.error = False
            self.color_error()
        except:
            self.lelr.setStyleSheet("QLineEdit {border-color : red}")
            self.lerror.setStyleSheet("QLabel {background-color : red}")
            self.lerror.setText('Learning rate is not a float')
            self.error = True
            self.color_error()

    def check_changed_an(self, name):
        for agent in env.agents:
            if name == agent:
                self.lemn.setStyleSheet("QLineEdit {border-color : }")
                self.lerror.setStyleSheet("QLabel {background-color : }")
                self.lerror.setText('')
                self.error = False
                self.color_error()
                return
        self.lemn.setStyleSheet("QLineEdit {border-color : red}")
        self.lerror.setText('Can\'t find agent')
        self.lerror.setStyleSheet("QLabel {background-color : red}")
        self.error = True
        self.color_error()

    def check_changed_dataset(self, data):
        if os.path.exists("data/"+data+".csv") == False:
            self.lem.setStyleSheet("QLineEdit {border-color : red}")
            self.lerror.setText('Can\'t find dataset')
            self.lerror.setStyleSheet("QLabel {background-color : red}")
            self.error = True
        else:
            self.lem.setStyleSheet("QLineEdit {border-color : }")
            self.lerror.setText('')
            self.lerror.setStyleSheet("QLabel {background-color : }")
            self.error = False
        self.color_error()

    def check_changed_exposure(self):
        cap_exposure = self.sbc.value() - (self.sbc.value() * (1 - self.sbexposure.value() / 100))
        max_order_valid = cap_exposure // (self.sbcp.value() + (self.sbmpd.value() * self.sbpv.value()))
        if max_order_valid == 0:
            self.change_exposure_varcolor('red')
            self.lerror.setText('Can\'t take orders')
            self.lerror.setStyleSheet("QLabel {background-color : red}")
            self.error = True
        elif max_order_valid < self.sbmo.value() // 2:
            self.change_exposure_varcolor('red')
            self.lerror.setText('Can\'t take '+str(int(self.sbmo.value() // 2))+' orders')
            self.lerror.setStyleSheet("QLabel {background-color : red}")
            self.error = True
        else:
            self.change_exposure_varcolor('')
            self.lerror.setText('')
            self.lerror.setStyleSheet("QLabel {background-color : }")
            self.error = False
        self.color_error()

    def change_exposure_varcolor(self, color):
        self.sbc.setStyleSheet("QSpinBox {border-color : " +color+ "}")
        self.sbexposure.setStyleSheet("QDoubleSpinBox {border-color :" +color +"}")
        self.sbmpd.setStyleSheet("QSpinBox {border-color : " +color+ "}")
        self.sbmo.setStyleSheet("QSpinBox {border-color : "+color+"}")
        self.sbcp.setStyleSheet("QSpinBox {border-color : "+color+"}")
        self.sbpv.setStyleSheet("QSpinBox {border-color : "+color+"}")

    def _build_wallet_settings(self, mode):
        Glayout = QGridLayout()
        gbox = QGroupBox("Wallet and risk settings")

        lc = QLabel('Capital : ')
        self.sbc = QSpinBox()
        self.sbc.setMinimum(5000)
        self.sbc.setMaximum(10000000)
        self.sbc.setValue(env.capital)

        lexposure = QLabel('Exposure : ')
        self.sbexposure = QDoubleSpinBox()
        self.sbexposure.setMinimum(1)
        self.sbexposure.setMaximum(100)
        self.sbexposure.setSingleStep(0.1)
        self.sbexposure.setValue(env.exposure)

        lmpd = QLabel('Max pip loss : ')
        self.sbmpd = QSpinBox()
        self.sbmpd.setMinimum(5)
        self.sbmpd.setMaximum(400)
        self.sbmpd.setValue(env.max_pip_drawdown)

        lmo = QLabel('Max pos : ')
        self.sbmo = QSpinBox()
        self.sbmo.setMinimum(1)
        self.sbmo.setMaximum(1000)
        self.sbmo.setValue(env.max_pos)

        Glayout.addWidget(lc, 0, 0)
        Glayout.addWidget(self.sbc, 0, 1)
        Glayout.addWidget(lexposure, 1, 0)
        Glayout.addWidget(self.sbexposure, 1, 1)
        Glayout.addWidget(lmpd, 2, 0)
        Glayout.addWidget(self.sbmpd, 2, 1)
        Glayout.addWidget(lmo, 3, 0)
        Glayout.addWidget(self.sbmo, 3, 1)

        self.sbc.valueChanged.connect(self.check_changed_exposure)
        self.sbexposure.valueChanged.connect(self.check_changed_exposure)
        self.sbmpd.valueChanged.connect(self.check_changed_exposure)
        self.sbmo.valueChanged.connect(self.check_changed_exposure)

        gbox.setLayout(Glayout)

        return gbox

    def _build_model_settings(self, mode):
        Glayout = QGridLayout()
        gbox = QGroupBox("Model settings")

        lmn = QLabel('Agent : ')
        self.lemn = QLineEdit()
        self.lemn.setText(str(env.model_name))

        llr = QLabel('Learning rate : ')
        self.lelr = QLineEdit()
        self.lelr.setText(str(env.learning_rate))

        lg = QLabel('Gamma : ')
        self.leg = QDoubleSpinBox()
        self.leg.setMinimum(0.01)
        self.leg.setMaximum(1)
        self.leg.setSingleStep(0.01)
        self.leg.setValue(env.gamma)

        le = QLabel('Epsilon : ')
        self.lee = QDoubleSpinBox()
        self.lee.setMinimum(0.01)
        self.lee.setMaximum(1)
        self.lee.setSingleStep(0.01)
        self.lee.setValue(env.epsilon)

        Glayout.addWidget(lmn, 0, 0)
        Glayout.addWidget(self.lemn, 0, 1)
        if mode == "train":
            Glayout.addWidget(llr, 1, 0)
            Glayout.addWidget(self.lelr, 1, 1)
            Glayout.addWidget(lg, 2, 0)
            Glayout.addWidget(self.leg, 2, 1)
            Glayout.addWidget(le, 3, 0)
            Glayout.addWidget(self.lee, 3, 1)

        self.lelr.textChanged.connect(self.check_changed_lr)
        self.lemn.textChanged.connect(self.check_changed_an)

        gbox.setLayout(Glayout)

        return gbox

    def _build_env_settings(self, mode):
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
        self.sbs = QDoubleSpinBox()
        self.sbs.setMaximum(10)
        self.sbs.setMinimum(0.01)
        self.sbs.setSingleStep(0.01)
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
        if mode == "train":
            Glayout.addWidget(lec, 4, 0)
            Glayout.addWidget(self.sbec, 4, 1)
            Glayout.addWidget(lws, 5, 0)
            Glayout.addWidget(self.sbws, 5, 1)
            Glayout.addWidget(lbs, 6, 0)
            Glayout.addWidget(self.sbbs, 6, 1)

        self.lem.textChanged.connect(self.check_changed_dataset)
        self.sbcp.valueChanged.connect(self.check_changed_exposure)
        self.sbpv.valueChanged.connect(self.check_changed_exposure)

        gbox.setLayout(Glayout)

        return gbox

    def _resize(self):
        self.h = 1855
        self.w = 1050
        self.root.resize(self.h, self.w)
        self.resize(self.h, self.w)
        self.root.showMaximized()

    def Hide_Swindow(self):
        self.StFrame.hide()

    def Show_Swindow(self):
        self.StFrame.show()

    def _get_env_var(self):
        env.stock_name = self.lem.text()
        env.model_name = self.lemn.text()
        env.learning_rate = float(self.lelr.text())

        env.gamma = self.leg.value()
        env.epsilon = self.lee.value()
        env.episode_count = self.sbec.value()
        env.window_size = self.sbws.value()
        env.sbbs = self.sbbs.value()
        env.capital = self.sbc.value()
        env.exposure = self.sbexposure.value()
        env.max_pip_drawdown = self.sbmpd.value()
        env.max_pos = self.sbmo.value()
        env.pip_value = self.sbpv.value()
        env.spread = self.sbs.value()
        env.contract_price = self.sbcp.value()

    def Build_Primary_Window(self):
        self.Hide_Swindow()
        self._resize()

        if env.mode == "Eval":
            env.episode_count = 1

        self.worker = Worker(env)
        self.worker.sig_step.connect(self.update)
        self.worker.sig_batch.connect(self.batch_up)
        self.worker.sig_episode.connect(self.episode_up)

        # Getting env settings
        self._get_env_var()

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
