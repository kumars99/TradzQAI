import pandas as pd

from tools.indicators.exponential_moving_average import exponential_moving_average as ema
from tools.indicators.volatility import volatility as vol
from tools.indicators.stochastic import percent_k as K
from tools.indicators.stochastic import percent_d as D
from tools.indicators.relative_strength_index import relative_strength_index as RSI
from tools.indicators.moving_average_convergence_divergence import moving_average_convergence_divergence as macd
from tools.indicators.bollinger_bands import bandwidth as bb

class indicators():

    def __init__(self):

        self.bb_period = 20
        self.rsi_period = 14
        self.sd_period = 0
        self.sv_period = 0
        self.stoch_period = 14
        self.volatility_period = 20
        self.macd_long = 24
        self.macd_short = 12

    def build_indicators(self, data):
        names = ['RSI', 'MACD', 'Volatility', 'EMA20', 'EMA50','EMA100']
        indicators = pd.DataFrame(columns = names)

        print ("Building RSI")
        indicators['RSI'] = RSI(data, self.rsi_period)

        print ("Building MACD")
        indicators['MACD'] = macd(data, self.macd_short, self.macd_long)

        print ("Building Volatility")
        indicators['Volatility'] = vol(data, self.volatility_period)

        #print ("Building Stoch_D")
        #indicators['Stoch_D'] = D(data, self.stoch_period)

        #print ("Building Stoch_K")
        #indicators['Stock_K'] = K(data, self.stoch_period)

        print ("Building EMA20")
        indicators['EMA20'] = ema(data, 20)

        print ("Building EMA50")
        indicators['EMA50'] = ema(data, 50)

        print ("Building EMA100")
        indicators['EMA100'] = ema(data, 100)

        #print ("Building bollinger band")
        #indicators['BB'] = bb(data, self.bb_period)
        return indicators
