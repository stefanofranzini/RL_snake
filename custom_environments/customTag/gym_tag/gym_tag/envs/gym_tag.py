import gym
import numpy as np


class TagEnv(gym.Env):
    """
    possible moves:
    
    0: stay
    1: up
    2: right
    3: down
    4: left
       
    """
    
    def __init__(self,n=10):
    
        self.ngrid = n
        self.action_space = gym.spaces.Discrete(5)
        self.observation_space = gym.spaces.Discrete(243)
        
        self.h_position = np.random.choice(range(self.ngrid),size=2)
        self.f_position = np.random.choice(range(self.ngrid),size=2)
        self.t_position = np.random.choice(range(self.ngrid),size=2)
        
        self.state = self.encode()
        
        self.agent = 0
        
        self.action = 0
        self.actions = { 0: "stop", 1: "down", 2: "right", 3: "up", 4: "left" }
        self.iterations = 0

    def decode(self):
        
        return np.unravel_index(self.state,(3,3,3,3,3))

    def encode(self):
        
        state = [ 1, 1, 1, 1, 1 ]
        
        xh,yh = self.h_position
        xf,yf = self.f_position
        xt,yt = self.t_position
        
        fdist = 0
        hdist = 0
                
        diff_x = (xh - xf) % self.ngrid 
        x_diff = (xf - xh) % self.ngrid
        
        if diff_x != 0:
            if diff_x < x_diff:
                state[0] = 0
                fdist += diff_x
            else:
                state[0] = 2
                fdist += x_diff
    
        #print( xh, xf, diff_x, x_diff, state[0] )

        diff_y = (yh - yf) % self.ngrid 
        y_diff = (yf - yh) % self.ngrid 
        
        if diff_y != 0:
            if diff_y < y_diff:
                state[1] = 0
                fdist += diff_y
            else:
                state[1] = 2
                fdist += y_diff
                
        #print( yh, yf, diff_y, y_diff, state[1] )
        
        diff_x = (xh - xt) % self.ngrid 
        x_diff = (xt - xh) % self.ngrid 
        
        if diff_x != 0:
            if diff_x < x_diff:
                state[2] = 0
                hdist += diff_x
            else:
                state[2] = 2
                hdist += x_diff
    
        #print( xh, xf, diff_x, x_diff, state[0] )

        diff_y = (yh - yt) % self.ngrid 
        y_diff = (yt - yh) % self.ngrid 
        
        if diff_y != 0:
            if diff_y < y_diff:
                state[3] = 0
                hdist += diff_y
            else:
                state[3] = 2
                hdist += y_diff

        if fdist > hdist:
            state[4] = 0
        elif fdist < hdist:
            state[4] = 2

        return np.ravel_multi_index(state,(3,3,3,3,3))
        
    def step(self,action):
        
        done = False
        info = {}
        
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
            state_= self.decode()
            
            if state_[0] == 1 and state_[1] == 1:
                reward = 100
                info = {"wins":"hunter"}
                done = True
            else:
                reward = -1

            if state_[2] == 1 and state_[3] == 1:
                reward = -100
                info = {"wins":"monster"}
                done = True

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
            state_= self.decode()
            
            if state_[2] == 1 and state_[3] == 1:
                reward = 100
                info = {"wins":"monster"}
                done = True
            else:
                reward = -1
            
        self.iterations += 1
            
        if self.iterations >= 200:
            print("too much time elapsed")
            info = {"wins":"nobody"}
            done = True
            
        return state, reward, done, info
        

    def reset(self):
        
        self.h_position = np.random.choice(range(self.ngrid),size=2)
        self.f_position = np.random.choice(range(self.ngrid),size=2)
        self.t_position = np.random.choice(range(self.ngrid),size=2)
        
        self.state = self.encode()
        
        self.iterations = 0
        self.agent = 0
        
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
        
        
