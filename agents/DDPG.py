from .agent import Agent

from keras.models import Model
from keras.layers import Dense, Input
from keras.layers.merge import Add
from keras.optimizers import Adam

import keras.backend as K

import tensorflow as tf


class DDPG(Agent):

    def __init__(self, state_size, env=None, is_eval=False, model_name=""):
        self.name = "DDPG"
        Agent.__init__(self, state_size, env=None, is_eval=False, model_name="")
        self.sess = tf.Session()

    def build_model(self):
        # Actor model
        self.actor_state_input, self.actor_model = self._actor_model()
        _, self.target_actor_model = self._actor_model()
        self.actor_critic_grad = tf.placeholder(tf.float32, [None, self.action_size])
        actor_model_weights = self.actor_model.trainable_weights
        self.actor_grads = tf.gradients(self.actor_model.output,
                                        actor_model_weights,
                                        -self.actor_critic_grad)
        grads = zip(self.actor_grads, actor_model_weights)
        self.optimize = tf.train.AdamOptimizer(self.learning_rate).apply_gradients(grads)

        # Critic model

        self.critic_state_input, self.critic_action_input, self.critic_model = self._critic_model()
        _, _, self.target_critic_model = self._critic_model()
        self.critic_grads = tf.gradients(self.critic_model.output,
                                         self.critic_action_input)

        self.sess.run(tf.global_variables_initializer())

    def _actor_model(self):
        state_input = Input(shape=(self.state_size.shape[1], ))
        h1 = Dense(32, activation='relu')(state_input)
        h2 = Dense(64, activation='relu')(h1)
        h3 = Dense(32, activation='relu')(h2)
        output = Dense(self.action_size, activation='relu')(h3)

        model = Model(input=state_input, output=output)
        model.compile(loss="mse", optimizer=Adam(lr=self.learning_rate))

        return state_input, model

    def _critic_model(self):
        state_input = Input(shape=(self.state_size.shape[1], ))
        state_h1 = Dense(32, activation='relu')(state_input)
        state_h2 = Dense(64)(state_h1)

        action_input = Input(shape=(self.action_size, ))
        action_h1 = Dense(64)(action_input)

        merged = Add()([state_h2, action_h1])
        merged_h1 = Dense(32, activation='relu')(merged)
        merged_h2 = Dense(8, activation='relu')(merged_h1)
        output = Dense(1, activation='relu')(merged_h2)

        model = Model(input=[state_input, action_input], output=output)
        model.compile(loss='mse', optimizer=Adam(lr=self.learning_rate))

        return state_input, action_input, model

    def update_target_model(self):
        self._update_actor_target()
        self._update_critic_target()

    def _update_actor_target(self):
        actor_model_weights = self.actor_model.get_weights()
        actor_target_weights = self.target_actor_model.get_weights()

        for i in range(len(actor_target_weights)):
            actor_target_weights[i] = actor_model_weights[i]
        self.target_actor_model.set_weights(actor_target_weights)

    def _update_critic_target(self):
        critic_model_weights = self.critic_model.get_weights()
        critic_target_weights = self.target_critic_model.get_weights()

        for i in range(len(critic_target_weights)):
            critic_target_weights[i] = critic_model_weights[i]
        self.critic_target_weights.set_weights(critic_target_weights)
