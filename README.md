# TradzQAI

Trading environnement for RL agents, backtesting and training.

- Available sessions:
    - Local
        - 1M bar datasets any size.
            - header should be ['Time', 'Open', 'High', 'Low', 'Close', 'Volume'] with ';' as separator
        - Tick datasets any size.
            - header should be ['Time', 'BID', 'ASK', 'VOL'] or ['Time', 'Price', 'Volume'] with ',' as separator
    - Live
        - Gdax API

- Available agents:
    - DDPG
    - DQFD
    - DQN
    - DQNN
    - NAF
    - PPO
    - TRPO
    - VPG

- Available contract type:
    - CFD
    - Classic

TradzQAI has been inspired by q-trader.

Indicators lib come from [pyti](https://github.com/kylejusticemagnuson/pyti)

More datasets available [here](http://www.histdata.com/download-free-forex-data/)

## Status

    Alpha in development
        It should be ready soon for live trading with gdax API

## Getting Started

- Dependencies :
  - [Tensorflow](https://github.com/tensorflow/tensorflow)
  - [Tensorforce](https://github.com/reinforceio/tensorforce)
  - [pyqtgraph](https://github.com/pyqtgraph/pyqtgraph)
  - Pandas
  - Numpy
  - PyQt5
  - tqdm
  - h5py

  ### Installation :
    ```pip install -r requirements.txt```

- Running the project
  ```
  Usage:
    python run.py -h (Show usage)
    python run.py -g on (Display interface, it does not support live session) # Gui is not available while not session is not fully integrated
    python run.py -s live (for live session) # Not fully fonctionnal
    python run.py -c config_dir/ # load config from directory, make sure you have agent, env and network json files in it
    python run.py (Run as default)
  ```
  When you run it for the first time, a config directory is created, you can change it to changes environnement settings and some agents settings.
  It save settings (env, agent, network) in a save directory, and create a new directory if make any changes.

  You can also do your own runner.
  ```
  from core import Local_session as Session
  session = Session() # Run with default values
  session.loadSession() # loading environnement, worker and agent
  session.start() # Start the session thread
  ```

## Relevant project
  - [TradingBrain](https://github.com/Prediction-Machines/Trading-Brain)
  - [q-trader](https://github.com/edwardhdlu/q-trader)
