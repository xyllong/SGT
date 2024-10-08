import numpy as np
from gymnasium import utils
from gymnasium.envs.mujoco import MujocoEnv
from gymnasium import spaces
import gymnasium as gym
import os

class MultiAgentScene(MujocoEnv, utils.EzPickle):

    metadata = {
        "render_modes": [
            "human",
            "rgb_array",
            "depth_array",
        ],
        "render_fps": 67, #20 #67
    }

    def __init__(self, xml_path, n_agents, **kwargs,):
        self.n_agents = n_agents

        self._mujoco_init = False
        MujocoEnv.__init__(self, 
                           xml_path, 
                           frame_skip=5, 
                           observation_space=None, 
                           **kwargs,
                           )
        
        self._mujoco_init = True
        utils.EzPickle.__init__(self, **kwargs,)

    def simulate(self, actions):
        if self.render_mode == "human":
            self.render()
        a = np.concatenate(actions, axis=0)
        self.do_simulation(a, self.frame_skip)

    def _step(self, actions):
        '''
        Just to satisfy mujoco_init, should not be used
        '''
        assert not self._mujoco_init, '_step should not be called on Scene'
        return self._get_obs(), 0, False, None

    def _get_obs(self):
        '''
        Just to satisfy mujoco_init, should not be used
        '''
        assert not self._mujoco_init, '_get_obs should not be called on Scene'
        obs = np.concatenate([
            self.model.data.qpos.flat,
            self.model.data.qvel.flat
        ])
        return obs

    def euler2quat(self, roll, pitch, yaw):
        """
        Convert Euler angles to quaternion.
        Roll, pitch, yaw are in radians.
        """
        cy = np.cos(yaw * 0.5)
        sy = np.sin(yaw * 0.5)
        cp = np.cos(pitch * 0.5)
        sp = np.sin(pitch * 0.5)
        cr = np.cos(roll * 0.5)
        sr = np.sin(roll * 0.5)

        w = cr * cp * cy + sr * sp * sy
        x = sr * cp * cy - cr * sp * sy
        y = cr * sp * cy + sr * cp * sy
        z = cr * cp * sy - sr * sp * cy

        return np.array([w, x, y, z])

    def reset_model(self):
        # yaw = self.np_random.uniform(low=-np.pi, high=np.pi)
        # init_euler = (0, 0, yaw)
        # init_quat = self.euler2quat(*init_euler)
        # self.init_qpos[:2] = [0, 0] 
        # self.init_qpos[3:7] = init_quat
        qpos = self.init_qpos + self.np_random.uniform(size=self.model.nq, low=-.1, high=.1)
        qvel = self.init_qvel + self.np_random.integers(self.model.nv) * .1
        self.set_state(qpos, qvel)
        return None
    
    ##########################################
    # for deepmind mujoco use

    @property
    def body_names(self):
        body_names = []
        for i in range(self.model.nbody):
            body_names.append(self.model.body(i).name)
        return body_names
    
    @property
    def joint_names(self):
        joint_names = []
        for i in range(self.model.njnt):
            joint_names.append(self.model.jnt(i).name)
        return joint_names
    
    @property
    def geom_names(self):
        geom_names = []
        for i in range(self.model.ngeom):
            geom_names.append(self.model.geom(i).name)
        return geom_names