import gym
import numpy as np


class TagEnv2(gym.Env):
    """
    possible moves:
    
    0: stay
    1: up
    2: right
    3: down
    4: left
    
    for both agents
    
    
    info about the state:
        - direction of food on x axis
        - direction of food on y axis
        - distance
    
    """
    
    def __init__(self,n=10):
    
        self.ngrid = n
        self.action_space = gym.spaces.Discrete(5)
        self.observation_space = gym.spaces.Box(low=0,high=1,shape=(6,6,6,6,self.ngrid+1,self.ngrid+1), dtype=int)
        
        self.h_position = np.random.choice(range(self.ngrid),size=2)
        self.f_position = np.random.choice(range(self.ngrid),size=2)
        self.t_position = np.random.choice(range(self.ngrid),size=2)
        
        self.state = self.encode()
        
        self.agent = 0
        
        self.action = 0
        self.actions = { 0: "stop", 1: "down", 2: "right", 3: "up", 4: "left" }

    def encode(self):
        
        state = [ 0, 0, 0, 0, 0, 0]
        
        xh,yh = self.h_position
        xf,yf = self.f_position
        xt,yt = self.t_position
                
        diff_x = (xh - xf) % self.ngrid 
        x_diff = (xf - xh) % self.ngrid 
        
        if diff_x != 0:
            if diff_x < x_diff:
                state[0] = 1
                state[4] += diff_x
            else:
                state[0] = -1
                state[4] += x_diff
    
        #print( xh, xf, diff_x, x_diff, state[0] )

        diff_y = (yh - yf) % self.ngrid 
        y_diff = (yf - yh) % self.ngrid 
        
        if diff_y != 0:
            if diff_y < y_diff:
                state[1] = 1
                state[4] += diff_y
            else:
                state[1] = -1
                state[4] += y_diff
                
        #print( yh, yf, diff_y, y_diff, state[1] )
        
        diff_x = (xh - xt) % self.ngrid 
        x_diff = (xt - xh) % self.ngrid 
        
        if diff_x != 0:
            if diff_x < x_diff:
                state[2] = 1
                state[5] += diff_x
            else:
                state[2] = -1
                state[5] += x_diff
    
        #print( xh, xf, diff_x, x_diff, state[0] )

        diff_y = (yh - yt) % self.ngrid 
        y_diff = (yt - yh) % self.ngrid 
        
        if diff_y != 0:
            if diff_y < y_diff:
                state[3] = 1
                state[5] += diff_y
            else:
                state[3] = -1
                state[5] += y_diff

        return np.array(state)
        
    def step(self,action):
        
        done = False
        
        self.action = action
        
        if self.agent == 0:
        
            if action == 1:
                 self.h_position[0] = ( self.h_position[0] + 1 ) % self.ngrid
            elif action == 2:
                 self.h_position[1] = ( self.h_position[1] + 1 ) % self.ngrid
            elif action == 3:
                 self.h_position[0] = ( self.h_position[0] - 1 ) % self.ngrid
            elif action == 4:
                 self.h_position[1] = ( self.h_position[1] - 1 ) % self.ngrid

            state = self.encode()

            if state[4] == 0:
                reward = 10
                done = True
            else:
                reward = -1
                if state[5] == 0:
                    reward = -100
                    
        else:
        
            if action == 1:
                 self.t_position[0] = ( self.t_position[0] + 1 ) % self.ngrid
            elif action == 2:
                 self.t_position[1] = ( self.t_position[1] + 1 ) % self.ngrid
            elif action == 3:
                 self.t_position[0] = ( self.t_position[0] - 1 ) % self.ngrid
            elif action == 4:
                 self.t_position[1] = ( self.t_position[1] - 1 ) % self.ngrid
            
            state = self.encode()
            
            if state[5] == 0:
                reward = 100
                done = True
            else:
                reward = -1
                    
        self.agent = ( self.agent + 1 ) % 2

        info = {}
        
        return state, reward, done, info
        

    def reset(self):
        
        self.h_position = np.random.choice(range(self.ngrid),size=2)
        self.f_position = np.random.choice(range(self.ngrid),size=2)
        self.t_position = np.random.choice(range(self.ngrid),size=2)
        
        self.state = self.encode()
        
        return self.state
        
    def render(self):
    
        mapped_state = ""
        
        for i in range(self.ngrid):
            for j in range(self.ngrid):
                if np.all(self.h_position == (i,j)):
                    mapped_state += "O "
                elif np.all(self.f_position == (i,j)):
                    mapped_state += "* "
                elif np.all(self.t_position == (i,j)):
                    mapped_state += "H "
                else:
                    mapped_state += ". "
            mapped_state += "\n"
        
        print(mapped_state)
        print("(%s)" % self.actions[self.action] )
        print()
        
        
