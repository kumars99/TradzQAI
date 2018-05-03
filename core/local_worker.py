from .worker import Worker
from environnement import Environnement
from tools import *

import time

import pandas as pd

from tqdm import tqdm
tqdm.monitor_interval = 0

class Local_Worker(Worker):

    def __init__(self, env):
        self.name = os.path.basename(__file__).replace(".py", "")
        #self.env.logger._add("", self.name)
        if env.gui == 0:
            env.init_logger()
            env.logger._save_conf(env)
        else:
            self.env = env
        env.logger.new_logs(self.name)
        env.logger._add("Initialization", self.name)
        Worker.__init__(self)

    def run(self, env=None):

        if env == None:
            env = self.env
        state = env.reset()
        self.init_agent(env)
        if env.gui == 0:
            ep = tqdm(range(env.episode_count + 1), desc="Episode processing ")
        else:
            ep = range(env.episode_count + 1)

        for e in ep:
            #env.cepisode = e + 1
            env.logger._add("Starting episode : " + str(env.current_step['episode']), self.name)
            env.start_t = time.time()
            if env.pause == 1:
                while (env.pause == 1):
                    time.sleep(0.01)
            state = env.reset()
            self.agent.reset()
            if env.gui == 0:
                dat = tqdm(range(len(env.data) - 1), desc="Step Processing ")
            else:
                dat = range(len(env.data) - 1)

            for t in dat:
                if env.pause == 1:
                    while (env.pause == 1):
                        time.sleep(0.01)
                tmp = time.time()
                #env.lst_data.append(state[0])

                action = self.agent.act(state) # Get action from agent
                # Get new state
                next_state, terminal, reward = env.execute(action)
                if env.manage_date() == 1:
                    env.lst_reward_daily.append(env.reward['daily'])
                    '''
                    env.logger._add("Daily reward : " + str(env.reward['daily']), self.name)
                    env.logger._add("Daily average rewards : " + str(env.avg_reward(env.lst_reward, 0)), self.name)
                    env.logger._add("Daily profit : " + str(env.wallet.profit['daily']), self.name)
                    env.logger._add("Daily trade : " + str(env.daily_trade['loss'] + env.daily_trade['win'] + env.daily_trade['draw']), self.name)
                    if env.daily_trade['win'] + env.daily_trade['loss'] > 1:
                        env.logger._add("Daily W/L : " + str('{:.3f}'.format(env.daily_trade['win'] / (env.daily_trade['loss'] + env.daily_trade['win']))), self.name)
                    else:
                        env.logger._add("Daily W/L : " + str('{:.3f}'.format(env.daily_trade['win'] / 1)), self.name)
                    '''
                    if env.wallet.profit['daily'] > 0:
                        env.logger._add("Saving training data with " +
                                        str(env.wallet.profit['daily']) +
                                        " daily profit", self.name)
                        env.logger.save_training_data(env.train_in,
                                                      env.train_out)
                    env.daily_reset()
                self.sig_step.emit() # Update GUI
                self.agent._memory.append((state,
                                          action,
                                          reward,
                                          next_state,
                                          terminal))
                state = next_state
                if "train" in env.mode:
                    self.agent.expReplay(reward, terminal)
                    if len(self.agent._memory) > env.batch_size:
                        self.sig_batch.emit()
                    if t % (len(env.data) // 10) == 0 and t > 0 :
                        self.agent._save_model()
                env.loop_t = time.time() - tmp
                if env.gui == 1:
                    time.sleep(0.07)

            env.logger._add("######################################################", self.name)
            env.logger._add("Total reward : " + str(env.reward['total']), self.name)
            env.logger._add("Average daily reward : " + str(env.avg_reward(env.lst_reward_daily, 0)), self.name)
            env.logger._add("Total profit : " + str(env.wallet.profit['total']), self.name)
            env.logger._add("Total trade : " + str(env.trade['loss'] + env.trade['win'] + env.trade['draw']), self.name)
            if env.trade['win'] + env.trade['loss'] > 0:
                env.logger._add("Trade W/L : " + str('{:.3f}'.format(env.trade['win'] / (env.trade['loss'] + env.trade['win']))), self.name)
            else:
                env.logger._add("Trade W/L : " + str('{:.3f}'.format(env.trade['win'] / 1)), self.name)
            env.logger._add("######################################################", self.name)
            self.sig_episode.emit()
