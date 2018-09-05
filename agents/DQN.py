from .agent import Agent

class DQN(Agent):

    def __init__(self, env=None, device=None):
        Agent.__init__(self, env=env, device=device)

    def get_specs(env=None):
        specs = {
            "type": "dqn-nstep_agent",

            "update_mode": {
                "unit": "timesteps",
                "batch_size": 64,
                "frequency": 4
            },

            "memory": {
                "type": "replay",
                "capacity": 10000,
                "include_next_states": True
            },

            "optimizer": {
                "type": "clipped_step",
                "clipping_value": 0.1,
                "optimizer": {
                    "type": "adam",
                    "learning_rate": 1e-3
                }
            },

            "discount": 0.99,
            "entropy_regularization": None,
            "double_q_model": True,

            "target_sync_frequency": 1000,
            "target_update_weight": 1.0,

            "actions_exploration": {
                "type": "epsilon_anneal",
                "initial_epsilon": 0.5,
                "final_epsilon": 0.0,
                "timesteps": 10000
            },

            "saver": {
                "directory": None,
                "seconds": 600
            },

            "summarizer": {
                "directory": None,
                "labels": [],
                "seconds": 120
            },

            "execution": {
                "type": "single",
                "session_config": None,
                "distributed_spec": None
                }
            }
        return specs
