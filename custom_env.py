import numpy as np
from PIL import Image
import cv2
import matplotlib.pyplot as plt
import pickle
from matplotlib import style
import time

style.use("ggplot")

#Variables
SIZE = 10 #grid size 10x10
EPISODES = 250000 #HOW MANY TIMES IT WILL ITERATE
MOVE_PENALTY =1
ENEMY_PENALTY = 300
FOOD_REWARD = 25
EPS_DECAY = 0.9998
SHOW_EVERY = 3000
epsilon = 0.9
start_q_table = None
LEARNING_RATE =0.1
DISCOUNT = 0.95
episode_rewards =[]
#Labels and keys for dict
PLAYER_N = 1
FOOD_N = 2
ENEMY_N = 3
#COLOR CODE
d = {1: (255,175,0),
    2: (0,255,0),
    3:(0,0,255)} 

# observations going to be relative position of food and relative position of enemy

class Blob():

    def __init__(self):
        self.x = np.random.randint(0,SIZE)
        self.y = np.random.randint(0,SIZE)
    
    def __str__(self):
        return ('x:{}, y:{}'.format(self.x,self.y))
    
    def __sub__(self,other):
        return(self.x-other.x, self.y-other.y)
    
    def action(self,choice):
        if choice == 0:
            self.move(x=1,y=1)
        elif choice == 1:
            self.move(x=-1,y=-1)
        elif choice == 2:
            self.move(x=-1,y=1)
        elif choice == 3:
            self.move(x=1,y=-1)


    def move(self, x= False, y=False):
        #if no value passed then it is going to move randomly
        if not x:
            self.x += np.random.randint(-1,2) #-1 , 0 , 1
        else: 
            self.x += x

        if not y:
            self.y += np.random.randint(-1,2) #-1 , 0 , 1
        else: 
            self.y += y
        
        if self.x <0:
            self.x =0
        elif self.x > SIZE-1:
            self.x = SIZE-1
        
        if self.y <0:
            self.y =0
        elif self.y > SIZE-1:
            self.y = SIZE-1
        
if start_q_table is None:
    q_table ={} 

    #(x1,y1) (x2,y2)
    for x1 in range(-SIZE+1, SIZE):

        for y1 in range(-SIZE+1, SIZE):

            for x2 in range(-SIZE+1, SIZE):

                for y2 in range(-SIZE+1, SIZE):
                    # As there is four actions four values are passing in the q_table
                    q_table[((x1,y1),(x2,y2))] = [np.random.uniform(-5,0) for i in range(4)]
else: 
    with open(start_q_table,'rb') as f: #rb is filename
        q_table = pickle.load()


for episode in range(EPISODES):

    player = Blob()
    food = Blob()
    enemy = Blob()

    if episode % SHOW_EVERY == 0:
        print("on # {}, epsilon: {}".format(episode,epsilon))
        print("{} ep mean {}".format(SHOW_EVERY,np.mean(episode_rewards[-SHOW_EVERY:])))
        show = True
    else:
        show = False

    episode_reward = 0

    #how many steps agent will take
    for i in range(200):
        obs = (player-food,player-enemy)

        if np.random.random() > epsilon:
            action = np.argmax(q_table[obs])
        else:
            action = np.random.randint(0,4)
        player.action(action)

        ######
        #enemy.move()
        #food.move()

        #REWARDS
        if player.x == enemy.x and player.y == enemy.y:
            reward = -ENEMY_PENALTY
        elif player.x ==food.x and player.y == food.y:
            reward = FOOD_REWARD
        else: 
            reward = -MOVE_PENALTY
        
        new_obs = (player - food, player-enemy)
        max_future_q = np.max(q_table[new_obs])
        current_q = q_table[obs][action]

        if reward == FOOD_REWARD:
            new_q = FOOD_REWARD
        elif reward == -ENEMY_PENALTY:
            new_q = -ENEMY_PENALTY
        else: 
            new_q = (1- LEARNING_RATE)*current_q + LEARNING_RATE*(reward + DISCOUNT*max_future_q)
        
        q_table[obs][action] = new_q

        if show:
            env = np.zeros((SIZE,SIZE,3),dtype=np.uint8)
            env[food.y][food.x] = d[FOOD_N]
            env[player.y][player.x] = d[PLAYER_N]
            env[enemy.y][enemy.x] = d[ENEMY_N]

            img = Image.fromarray(env, "RGB")
            img = img.resize((300,300))
            cv2.imshow("", np.array(img))

            if reward == FOOD_REWARD or reward == -ENEMY_PENALTY:
                if cv2.waitKey(500) & 0xFF == ord('q'):
                    break
            else: 
                if cv2.waitKey(500) & 0xFF == ord('q'):
                    break
        episode_reward += reward
        if reward == FOOD_REWARD or reward == -ENEMY_PENALTY:
            break
    episode_rewards.append(episode_reward)
    epsilon *= EPS_DECAY

moving_avg = np.convolve(episode_rewards, np.ones((SHOW_EVERY,))/ SHOW_EVERY, mode='valid')
plt.plot([i for i in range(len(moving_avg))],moving_avg)
plt.ylabel('reward {}'.format(SHOW_EVERY))
plt.xlabel('episode #')
plt.show()

with open ('q_table -{}.pickle'.format(int(time.time())),'wb') as f: 
    pickle.dump(q_table,f)



