#!/usr/bin/python3.8

import gym
import numpy as np
from IPython.display import clear_output
from time import sleep
import matplotlib.pyplot as plt
import sys

def pick_action(state,q_table):
    
    my_qs = q_table[state]
    
    epsilon = 0.00
    
    if np.random.uniform(0,1) < epsilon:
        return np.random.choice(range(len(my_qs)))
    else:
        return np.argmax(my_qs)
        
def pick_agent(n):
    if n < 2:
        return 0
    else:
        return 1

env = gym.make("gym_tag:tag-v0",n=int(sys.argv[1])).env

q_table = np.load("q_table_tag.npy")


# 3 x 3 x 3 x 3 x 3 x 5
'''
print(q_table[0].shape)

for i in range(243):
    print(i, q_table[0][i], np.unravel_index(i,(3,3,3,3,3)))
    plt.plot(q_table[0][i],'C0',marker='o')
    plt.show()
''' 


# For plotting metrics
all_epochs = []

wins = {"hunter":0, "monster":0, "nobody":0}

for i in range(0,10000):
    state = env.reset()
    
    n = 0
    
    epochs,penalties,reward = 0,0,0
    
    done = False
    
    while not done:
        
        action = pick_action(state,q_table[env.agent])
            
        next_state, reward, done, info = env.step(action)

        env.render()
        sleep(0.03)

        env.state = next_state
        state = next_state
        n = (n+1)%5
        env.agent = pick_agent(n)

        epochs += 1

    wins[info["wins"]] += 1
        
    print("ended")
    print('----------------------------')
    print()
            
    all_epochs += [ epochs ]
    
plt.plot(all_epochs,'o')
plt.show()

print(wins)















