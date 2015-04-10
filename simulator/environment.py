import numpy as np
import random

class Environment:
    TRACKER = 5

    OBJECT_MAX_DIM = 6
    OBJECT_MIN_DIM = 1

    MOVE_LEFT = 0
    MOVE_RIGHT = 1

    def __init__(self, width, height):
        #TODO: No need for matrix.
        #TODO: Need to keep track of object and tracker position oynl
        #Board dimensions. 30x15 for Beer's game
        self.board_width = width
        self.board_height = height

        #Position of agent

        self.recording = []

        #TODO: consider how scoring should be done
        self.score = 0

    def init_scoring(self):
        self.score = 0
        self.recording = []
        agent_x = random.randint(0, self.board_width-1)
        agent_y = self.board_height-1
        return agent_x, agent_y

    def score_agent(self, agent, timesteps=600, recording=False):
        x,y = self.init_scoring()

        object_x = 0
        object_y = 0
        object_dim = random.randint(Environment.OBJECT_MIN_DIM, Environment.OBJECT_MAX_DIM)

        for t in range(timesteps):

            #Shadow sensor gathering
            shadow_sensors = self._get_sensor_data(x,y ,object_x, object_y, object_dim)

            #Motor output
            motor_output = agent.feedforward(shadow_sensors)
            x, y = self._move_agent(motor_output)
            if recording:
                self.recording.append((t, (x,y, Environment.TRACKER), (object_x, object_y, object_dim)))

            #TODO: Handle object - On platform, or not. Move down 1
            #TODO: Move agent based on motor output
            #Spawn new object if object at bottom
        return self.score

    def _move_agent(self, motor_output):
        #TODO:Magnitude and direction of agent
        nx = 0
        ny = 0
        return (nx, ny)

    def get_recording(self):
        return self.recording

    def _get_sensor_data(self, x,y, ox, oy, odim):
        '''
        Shadow sensor creation. If the x of tracker and object overlap
        the shadow sensor for the tracker agent is set to 1, indicating
        that an object is above the platform at that position
        '''
        sensor = np.zeros(Environment.TRACKER)
        for i in range(Environment.TRACKER):
            if(x+i>=ox and x+i<ox+odim):
                sensor[i] = 1
        return sensor


    def __repr__(self):
        return "Environment of" + str(self.board_width) + "x" + str(self.board_height)

