import random
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator
from time import time
import sys
from outputParse import parse


class RandomAgent(Agent):
    """An agent that learns to drive in the smartcab world."""

    def __init__(self, env):
        super(RandomAgent, self).__init__(env)
        # sets self.env = env, state = None, next_waypoint = None,
        # and a default color
        self.color = 'red'  # override color
        self.planner = RoutePlanner(self.env, self)
        # simple route planner to get next_waypoint
        # TODO: Initialize any additional variables here

    def reset(self, destination=None):
        self.planner.route_to(destination)
        # TODO: Prepare for a new trip; reset any variables here, if required
        self.state = None

    def update(self, t):
        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()
        # from route planner, also displayed by simulator
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)

        # TODO: Update state

        # TODO: Select action according to your policy
        possible_actions = []
        if(inputs['light'] == 'red'):
            if(inputs['left'] != 'forward'):
                possible_actions = ['right']
        else:
            if(inputs['oncoming'] == 'forward'):
                possible_actions = ['forward', 'right']
            else:
                possible_actions = ['right', 'forward', 'left']
        if len(possible_actions) == 0:
            action = None
        else:
            action = random.sample(possible_actions, 1)
            action = action[0]

        # Execute action and get reward
        reward = self.env.act(self, action)

        # TODO: Learn policy based on state, action, reward

        print "LearningAgent.update(): deadline = {}, inputs = {}, action = {}\
              ,reward = {}".format(deadline, inputs, action, reward)  # [debug]


class LearningAgent(Agent):
    """An agent that learns to drive in the smartcab world."""

    def __init__(self, env, learning_rate=0.6, discount_factor=0.4):
        super(LearningAgent, self).__init__(env)
        # sets self.env = env, state = None, next_waypoint = None,
        # and a default color
        self.color = 'red'  # override color
        self.planner = RoutePlanner(self.env, self)
        # simple route planner to get next_waypoint
        # TODO: Initialize any additional variables here
        self.alpha = learning_rate
        self.gamma = discount_factor
        self.state = None
        self.Qvalues = self.initialize_Qvalues()

    def reset(self, destination=None):
        self.planner.route_to(destination)
        # TODO: Prepare for a new trip; reset any variables here, if required
        self.state = None

    def initialize_Qvalues(self, val=5.0):
        Qvalues = {}
        for waypoint in ['left', 'right', 'forward']:
            Qvalues[((waypoint, 'red'), 'forward')] = 0
            Qvalues[((waypoint, 'red'), 'left')] = 0
            Qvalues[((waypoint, 'red'), 'right')] = val
            Qvalues[((waypoint, 'red'), None)] = val
        for waypoint in ['left', 'right', 'forward']:
            Qvalues[((waypoint, 'green'), 'forward')] = val
            Qvalues[((waypoint, 'green'), 'left')] = val
            Qvalues[((waypoint, 'green'), 'right')] = val
            Qvalues[((waypoint, 'green'), None)] = val
        return Qvalues

    def Qmax(self, state):
        action = None
        max_Q = 0.0
        for a in self.env.valid_actions:
            Q = self.Qvalues[(state, a)]
            if Q > max_Q:
                action = a
                max_Q = Q
        return (max_Q, action)

    def update(self, t):
        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()
        # from route planner, also displayed by simulator
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)

        # TODO: Update state
        self.state = (self.next_waypoint,  inputs['light'])

        # TODO: Select action according to your policy
        (Q, action) = self.Qmax(self.state)

        # Execute action and get reward
        reward = self.env.act(self, action)

        # TODO: Learn policy based on state, action, reward
        next_waypoint = self.planner.next_waypoint()
        inputs = self.env.sense(self)
        stateNew = (next_waypoint,   inputs['light'])
        (Qnew, actionPrime) = self.Qmax(stateNew)
        Q += self.alpha * (reward + self.gamma*Qnew - Q)
        self.Qvalues[(self.state, action)] = Q

        # print "LearningAgent.update(): state = {}, deadline = {},\
        #        inputs = {}, action = {}, reward = {}".format(self.state,
        #                                                      deadline,
        #                                                      inputs,
        #                                                      action,
        #                                                      reward)
        # [debug]


def run():
    """Run the agent for a finite number of trials."""

    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create learning agent
    # a = e.create_agent(RandomAgent)  # create random agent
    e.set_primary_agent(a, enforce_deadline=True)  # set agent to track

    # Now simulate it
    sim = Simulator(e, update_delay=0.01)
    # reduce update_delay to speed up simulation
    sys.stdout = open("./output.txt", "w")
    tic = time()
    sim.run(n_trials=100)  # press Esc or close pygame window to quit
    toc = time()
    sys.stdout = sys.__stdout__

    print "Totoal time used: {}.".format(toc - tic)
    parse("./output.txt")

if __name__ == '__main__':
    run()
