from gym.envs.registration import register 

register(id='tag-v0',entry_point='gym_tag.envs:TagEnv',)
register(id='tag-v2',entry_point='gym_tag.envs:TagEnv2',) 
