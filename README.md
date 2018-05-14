# TradzQAI

Trading environnement for RL agents, backtesting and training.

TradzQAI has been inspired by q-trader.
Indicators lib come from [pyti](https://github.com/kylejusticemagnuson/pyti)

More datasets available [here](http://www.histdata.com/download-free-forex-data/?/ascii/1-minute-bar-quotes)

## Status

    Alpha in development

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
    python run.py -g on (Display interface, it does not support live session)
    python run.py -s live (for live session)
    python run.py (Run as default)
  ```
  When you run it for the first time, a file named "conf.cfg" is created, you can change it to changes environnement settings and some agents settings.
  If you launch it with the gui, the conf file is just saving the settings from gui.
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
