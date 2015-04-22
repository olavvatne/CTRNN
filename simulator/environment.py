import numpy as np
import random
import math

class Environment:
    TRACKER = 5

    OBJECT_MAX_DIM = 6
    OBJECT_MIN_DIM = 1

    MOVE_LEFT = 0
    MOVE_RIGHT = 1

    DIM_INDEX = 2
    Y_INDEX = 1
    X_INDEX = 0

    def __init__(self, width, height, pull=False, wrap=False):
        #Board dimensions. 30x15 for Beer's game
        self.board_width = width
        self.board_height = height
        self.wrap = wrap
        self.pull = pull
        #Position of agent
        self.recording = []


    def make_object_pool(self, timesteps):
        n = 6
        o = [i for i in range(1, n+1) for j in range(math.ceil(timesteps/(15*6)))]
        random.shuffle(o)
        return o


    def score_agent(self, agent, timesteps=600, rec=False):
        if rec:
            self.recording = []
        score = [0,0,0,0, 0, 0, 0]

        tracker= self._init_agent(agent)
        objects = self.make_object_pool(timesteps)
        object = self._spawn_object(objects)

        self.succ_pull = 0
        self.total_pull = 0
        self.speed = 0
        self.max_speed = 1
        #Tracker at egde does not work it seems . Remove later
        self.min_x = 30
        self.max_x = 0

        for t in range(timesteps):
            #Shadow sensor gathering
            shadow_sensors = self._get_sensor_data(tracker, object)
            #Motor output
            motor_output = agent.input(shadow_sensors)


            #Score if at bottom
            #Move agent
            pulled = False
            if self.pull and motor_output[2]>0.5:
                object[Environment.Y_INDEX] = self.board_height-1
                pulled = True

            if rec:
                self.recording.append((t,list(score), list(tracker), shadow_sensors, pulled, list(object)))

            if self._object_at_bottom(object):
                s = self._score_target(tracker, object, pulled)
                score[s] += 1
                object = self._spawn_object(objects)
            else:
                #Move object closer to bottom
                object[Environment.Y_INDEX] += 1

            if not pulled:
                tracker= self._move_agent(tracker ,object, motor_output, shadow_sensors)

        score[-3] = self.speed/self.max_speed
        if not self.wrap:
            score[-2] = (self.max_x - self.min_x)/(self.board_width-Environment.TRACKER)
        if self.pull:
            if self.total_pull > 0:
                score[-1] = self.succ_pull/(self.total_pull)
        return score

    def _spawn_object(self, objects):
        #Assume objects cant wrap around. Will make no-wrap scenario easier
        if len(objects)>0:
            dim = objects.pop()
        else:
            dim = random.randint(Environment.OBJECT_MIN_DIM, Environment.OBJECT_MAX_DIM)
        return [random.randint(0, self.board_width-1-dim), 0, dim]

    def _init_agent(self, agent):
        agent.reset()
        agent_x = 12 #random.randint(0, self.board_width-Environment.TRACKER)
        agent_y = self.board_height-1
        return [agent_x, agent_y, Environment.TRACKER]

    def _object_at_bottom(self, object):
        return object[Environment.Y_INDEX] == self.board_height-1

    def _score_target(self, tracker, object, pulled):
        '''
        Full overlap  1,2,3,4 --> capture
        Full overlap 5 --> failure
        No overlap of 5,6 --> avoidance
        No overlap of 1,2,3,4 --> failure
        Partial overlap of 1,2,3,4,5,6 --> failure
        '''
        x, y, dim = tracker
        ox, oy, odim = object
        #TODO: decrement avoidance instead of failure?
        target_set = set([i%self.board_width for i in range(x, x+dim)])
        object_set = set([i for i in range(ox, ox+odim)])
        if object_set.issubset(target_set) and odim < 5:
            self.total_pull +=1
            if pulled:
                self.succ_pull += 1.1
            return 0
            #self.capture += 1

        elif (not object_set & target_set) and odim > 4:
            if pulled:
                self.succ_pull -= 0.25
            return 1
        else:
            if pulled:
                self.succ_pull -= 0.5
            if odim> 4:
                return 3
                #self.failure_avoidance += 1
            else:
                return 2
                #self.failure_capture += 1



    def _move_agent(self, tracker, object, motor_output, sensor):
        diff = motor_output[0] - motor_output[1]
        x = tracker[Environment.X_INDEX]
        value = abs(diff)

        magnitude = int(value>=0.2) + int(value>=0.4) + int(value>=0.6)+ int(value>=0.8)

        dir = -1
        if diff< 0:
            dir = 1


        if self.wrap:
            self.speed += magnitude
            self.max_speed += 4
            tracker[Environment.X_INDEX] = (x + (magnitude*dir))%self.board_width #Wrap around
        else:
            self.max_speed += 4
            temp = tracker[Environment.X_INDEX]
            tracker[Environment.X_INDEX] = max(0, min(self.board_width-Environment.TRACKER, x + (magnitude*dir)))
            self.speed += abs(tracker[Environment.X_INDEX] - temp)

            if tracker[Environment.X_INDEX] < self.min_x:
                self.min_x = tracker[Environment.X_INDEX]
            elif tracker[Environment.X_INDEX] > self.max_x:
                self.max_x = tracker[Environment.X_INDEX]

        return tracker

    def get_recording(self):
        return self.recording

    def _get_sensor_data(self, tracker, object):
        '''
        Shadow sensor creation. If the x of tracker and object overlap
        the shadow sensor for the tracker agent is set to 1, indicating
        that an object is above the platform at that position
        '''

        x, y, dim = tracker
        ox, oy, odim = object

        if not self.wrap:
            w = 1
            sensor = np.zeros(dim+ 2)
            sensor[0] = int(x == 0)
            sensor[-1] = int(x + dim == self.board_width)
        else:
            w = 0
            sensor = np.zeros(dim)

        for i in range(dim):
            #TODO: handle wrap around. Think spawn assumption handles it
            target_element = (x+i)%self.board_width
            if(target_element>=ox and target_element<ox+odim):
                sensor[i + w] =1 #/max(self.board_height - oy-5, 1.0)
        return sensor


    def __repr__(self):
        return "Environment of" + str(self.board_width) + "x" + str(self.board_height)

