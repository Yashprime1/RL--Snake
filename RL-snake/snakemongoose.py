from numpy import inf
import pygame
import random
import json
import os
import itertools
import matplotlib.pyplot as plt
from scipy.spatial import  distance
from IPython import display

plt.ion()

def plot(scores1, mean_scores1,scores2, mean_scores2,player,save=False):
    if player==1:
        display.clear_output(wait=True)
        display.display(plt.gcf())
        plt.clf()
        plt.title('Training...')
        plt.xlabel('Number of Games')
        plt.ylabel('score1')
        plt.plot(scores1)
        plt.plot(mean_scores1)
        plt.ylim(ymin=0)
        plt.text(len(scores1)-1, scores1[-1], str(scores1[-1]))
        plt.text(len(mean_scores1)-1, mean_scores1[-1],  str(mean_scores1[-1]))
        plt.show(block=False)
        plt.pause(.1)
        if save: plt.savefig('qlearning_snake.png')
    else:
        display.clear_output(wait=True)
        display.display(plt.gcf())
        plt.clf()
        plt.title('Training...')
        plt.xlabel('Number of Games')
        plt.ylabel('score2')
        plt.plot(scores2)
        plt.plot(mean_scores2)
        plt.ylim(ymin=0)
        plt.text(len(scores2)-1, scores2[-1], str(scores2[-1]))
        plt.text(len(mean_scores2)-1, mean_scores2[-1], str(mean_scores2[-1]))
        plt.show(block=False)
        plt.pause(.1)
        if save: plt.savefig('qlearning_mongoose.png')



###### Initialization ######

# For screen
dimension_x=400
dimension_y=400

# For snake & mongoose
snake_color=(0,0,255) #blue
mongoose_color=(255,255,0) #yellow
head_x1=int(dimension_x/2)
head_y1=int(dimension_y/2)
snake_body1=[(head_x1,head_y1)]
head_x2=int(dimension_x/4)
head_y2=int(dimension_y/4)


# For food
food_color=(255,0,0) #Red
food_x=random.randrange(0,dimension_x,10)
food_y=random.randrange(0,dimension_y,10)

# For RL Agent

states1 = list(itertools.product(*[(0, 1)] * 11))
states2 = list(itertools.product(*[(0, 1)] * 15))
actions=[0,1,2]


q_table1={}
q_table2={}
for state in states1:
    for action1 in actions: 
        q_table1[(*state,action1)]=0
    
for state in states2:
    for action2 in actions: 
        q_table2[(*state,action2)]=0


try:
    with open('./q_table_snake.json') as json_file:
        if os.stat("./q_table_snake.json").st_size != 0:
            q_table1 = json.load(json_file)
            q_table1=dict((tuple(map(int,k.split(","))), v) for k,v in q_table1.items())
        else:
            print("File empty")
except OSError:
    print("File not found")


try:
    with open('./q_table_mongoose.json') as json_file:
        if os.stat("./q_table_mongoose.json").st_size != 0:
            q_table2 = json.load(json_file)
            q_table2=dict((tuple(map(int,k.split(","))), v) for k,v in q_table2.items())
        else:
            print("File empty")
except OSError:
    print("File not found")


epsilon1=1
LR1=0.1
discount1=0.9
epsilon2=1
LR2=0.1
discount2=0.9

state_next1=()
reward_next1=0

action1=1 # initially right
action2=1 # initially right
max_games=1000


# For game
black=(0,0,0)
scores1=[]
scores2=[]
mean_scores1=[]
mean_scores2=[]
record1=0
record2=0
score1=0
score2=0
n_games1=1
n_games2=1
total_score1=0
total_score2=0
game_over= False
current_direction1 = pygame.K_RIGHT
current_direction2 = pygame.K_LEFT

try:
    with open('./savedparams_snakemongoose.json') as json_file:
        if os.stat("./savedparams_snakemongoose.json").st_size != 0:
            saved_params = json.load(json_file)
            epsilon1=saved_params["epsilon1"]
            LR1=saved_params["LR1"]
            discount1=saved_params["discount1"]
            state_next1=saved_params["state_next1"]
            reward_next1=saved_params["reward_next1"]
            action1=saved_params["action1"]
            epsilon2=saved_params["epsilon2"]
            LR2=saved_params["LR2"]
            discount2=saved_params["discount2"]
            state_next2=saved_params["state_next2"]
            reward_next2=saved_params["reward_next2"]
            action2=saved_params["action2"]
            max_games=saved_params["max_games"]
            scores1=saved_params["scores1"]
            mean_scores1=saved_params["mean_scores1"]
            record1=saved_params["record1"]
            score1=saved_params["score1"]
            n_games1=saved_params["n_games1"]
            total_score1=saved_params["total_score1"]
            scores2=saved_params["scores2"]
            mean_scores2=saved_params["mean_scores2"]
            record2=saved_params["record2"]
            score2=saved_params["score2"]
            n_games2=saved_params["n_games2"]
            total_score2=saved_params["total_score2"]
            current_direction1=saved_params["current_direction1"]
            current_direction2=saved_params["current_direction2"]
            head_x1=saved_params["head_x1"]
            head_y1=saved_params["head_y1"]
            snake_body1=saved_params["snake_body1"]
            head_x2=saved_params["head_x2"]
            head_y2=saved_params["head_y2"]
            food_x=saved_params["food_x"]
            food_y=saved_params["food_y"]
        else:
            print("File empty")

except OSError:
    print("File not found")

pygame.init()
display_board=pygame.display.set_mode((dimension_x,dimension_y))
pygame.display.update()

###### Game ######

# place food on screen
def place_food():
    global dimension_x,dimension_y,display_board,food_color,food_x,food_y,snake_body1,head_x2,head_y2
    food_x=random.randrange(0,dimension_x,10)
    food_y=random.randrange(0,dimension_y,10)
    if((food_x,food_y) in snake_body1 or (food_x,food_y)==(head_x2,head_y2) ) : place_food()
    pygame.draw.rect(display_board,food_color,[food_x,food_y,10,10])     
    pygame.display.update()

def show_score():
    global score1,score2,display_board
    """system font"""
    font = pygame.font.SysFont("Segoe UI", 35)
    textsurface = font.render("score1 :{} ".format(score1), False,(0,255,0))  # "text", antialias, color
    display_board.blit(textsurface, (0, 0))
    textsurface = font.render("score2 :{} ".format(score2), False,(0,255,0))  # "text", antialias, color
    display_board.blit(textsurface, (0, dimension_y-40))

# move snake on screen
def move_snake1(speed=10):
    global game_over,black,head_x1,head_y1,snake_body1,snake_color,food_x,food_y,current_direction1,record1,score1,display_board    
    reward=0
    # remove previous snake from screen
    for (x,y) in snake_body1:
        pygame.draw.rect(display_board,black,[x,y,10,10])     
        pygame.display.update()

    if current_direction1 == pygame.K_LEFT:
        head_x1 -= speed
    if current_direction1 == pygame.K_RIGHT:
        head_x1 += speed
    if current_direction1 == pygame.K_UP:
        head_y1 -= speed
    if current_direction1 == pygame.K_DOWN:
        head_y1 += speed
    
    if snake_collided1(head_x1,head_y1):
        reward-=10
        init_snake_game()
    elif head_x1==food_x and head_y1==food_y:
        snake_body1.insert(0,(head_x1,head_y1))
        score1+=1
        reward+=10
        display_board.fill(black)
        place_food()
    else:
        reward+=(-0.01)
        snake_body1.insert(0,(head_x1,head_y1))
        snake_body1.pop()
    
    # add new snake from screen
    for (x,y) in snake_body1:
        pygame.draw.rect(display_board,snake_color,[x,y,10,10])     
        pygame.display.update()
    return reward

def move_mongoose2(speed=10):
    global game_over,black,head_x2,head_y2,snake_color,mongoose_color,food_x,food_y,current_direction2,record2,score2,display_board,snake_body1    
    reward=0
    # remove previous snake from screen
    pygame.draw.rect(display_board,black,[head_x2,head_y2,10,10])     
    pygame.display.update()

    if current_direction2 == pygame.K_LEFT:
        head_x2 -= speed
    if current_direction2 == pygame.K_RIGHT:
        head_x2 += speed
    if current_direction2 == pygame.K_UP:
        head_y2 -= speed
    if current_direction2 == pygame.K_DOWN:
        head_y2 += speed
    
    if mongoose_collided2(head_x2,head_y2):
        reward-=10
        init_mongoose_game()
    elif (head_x2,head_y2) in snake_body1[:]:
        score2+=1
        reward+=10
        display_board.fill(black)
        init_snake_game()
    elif (head_x2,head_y2)==(food_x,food_y):
        score2+=0.2
        reward+=1
        place_food()
    else:
        reward+=(-0.01)
        
    # add new mongoose from screen
    pygame.draw.rect(display_board,mongoose_color,[head_x2,head_y2,10,10])     
    pygame.display.update()
    return reward

def snake_collided1(x,y):
    global dimension_x,dimension_y,snake_body1,head_x2,head_y2
    if x<0 or y<0 or x>dimension_x or y>dimension_y or (x,y) in snake_body1[1:] or (x,y)==(head_x2,head_y2):
        return True
    return False


def mongoose_collided2(x,y):
    global dimension_x,dimension_y,snake_body1
    if x<0 or y<0 or x>dimension_x or y>dimension_y:
        return True
    return False

def init_snake_game():
    global head_x1,head_y1,snake_body1,head_x2,head_y2,food_x,food_y,current_direction1,current_direction2,display_board,score1,mean_scores1,scores1,total_score1,score2,mean_scores2,scores2,total_score2,epsilon1,epsilon2,n_games1,record1,record2
    if score1>record1:
        record1=score1
    scores1.append((score1))
    total_score1 += score1
    mean_score1 = total_score1 / n_games1
    n_games1+=1
    mean_scores1.append(mean_score1)
    plot(scores1,mean_scores1,scores2,mean_scores2,1)
    if(epsilon1>(n_games1/max_games)): epsilon1-=(n_games1/max_games)
    display_board.fill(black)
    head_x1=int(dimension_x/2)
    head_y1=int(dimension_y/2)
    snake_body1=[(head_x1,head_y1)]
    current_direction1 = pygame.K_RIGHT
    score1=0
    place_food()

def init_mongoose_game():
    global head_x1,head_y1,snake_body1,head_x2,head_y2,food_x,food_y,current_direction1,current_direction2,display_board,score1,mean_scores1,scores1,total_score1,score2,mean_scores2,scores2,total_score2,epsilon1,epsilon2,n_games2,record1,record2
    if score2>record2:
        record2=score2
    scores2.append((score2))
    total_score2 += score2
    mean_score2 = total_score2 / n_games2
    n_games2+=1
    mean_scores2.append(mean_score2)
    plot(scores1,mean_scores1,scores2, mean_scores2,2)
    if(epsilon2>(n_games2/max_games)): epsilon2-=(n_games2/max_games)
    display_board.fill(black)
    head_x2=int(dimension_x/4)
    head_y2=int(dimension_y/4)
    current_direction2 = pygame.K_LEFT
    score2=0
    place_food()


###### RL Agent ######
def play_agent1(state):
    global q_table1,epsilon1,actions
    print("Agent : ")
    # step 2: choose action1 e-greedy 
    if random.random()<epsilon1:
        max_action = random.randint(0,len(actions)-1)
        print("Exploration : ",max_action)
        return max_action
    else:
        max_action=-1
        max_qvalue=0
        for action1 in actions:
            if(q_table1[(*state,action1)]>max_qvalue): 
                max_qvalue=q_table1[(*state,action1)]
                max_action=action1
        if max_action==-1:
            max_action = random.randint(0,len(actions)-1)
        print("Exploitation : ",max_action)
        return max_action

def play_agent2(state):
    global q_table2,epsilon2,actions
    print("Agent : ")
    # step 2: choose action1 e-greedy 
    if random.random()<epsilon2:
        max_action = random.randint(0,len(actions)-1)
        print("Exploration : ",max_action)
        return max_action
    else:
        max_action=-1
        max_qvalue=0
        for action2 in actions:
            if(q_table2[(*state,action2)]>max_qvalue): 
                max_qvalue=q_table2[(*state,action2)]
                max_action=action2
        if max_action==-1:
            max_action = random.randint(0,len(actions)-1)
        print("Exploitation : ",max_action)
        return max_action

   
def update_qtable1(state,action1,state_next1,reward_next1):
    global q_table1,epsilon1,actions,LR1,discount1

    # step 3: update q_table1 
    
    max_action=0
    max_qvalue=0
    for act in actions:
        if(q_table1[(*state_next1,act)]>max_qvalue):
            max_qvalue=q_table1[(*state_next1,act)]
            max_action=act
    q_next = q_table1[(*state_next1,max_action)] 
    
    q_table1[(*state,action1)] = q_table1[(*state,action1)] + LR1 * (reward_next1 + discount1*q_next - q_table1[(*state,action1)] )

def update_qtable2(state,action2,state_next2,reward_next2):
    global q_table2,epsilon2,actions,LR2,discount2

    # step 3: update q_table1 
    
    max_action=0
    max_qvalue=0
    for act in actions:
        if(q_table2[(*state_next2,act)]>max_qvalue):
            max_qvalue=q_table2[(*state_next2,act)]
            max_action=act
    q_next = q_table2[(*state_next2,max_action)] 
    
    q_table2[(*state,action2)] = q_table2[(*state,action2)] + LR2 * (reward_next2 + discount2*q_next - q_table2[(*state,action2)] )

def take_action1(action1):
    global current_direction1
    key_actions=[pygame.K_LEFT,pygame.K_UP,pygame.K_RIGHT,pygame.K_DOWN]
    if(action1==0): pass
    elif(action1==1):
        current_direction1=key_actions[(key_actions.index(current_direction1)-1) % len(key_actions)] 
    elif(action1==2):
        current_direction1=key_actions[(key_actions.index(current_direction1)+1) % len(key_actions)]

def take_action2(action2):
    global current_direction2
    key_actions=[pygame.K_LEFT,pygame.K_UP,pygame.K_RIGHT,pygame.K_DOWN]
    if(action2==0): pass
    elif(action2==1):
        current_direction2=key_actions[(key_actions.index(current_direction2)-1) % len(key_actions)] 
    elif(action2==2):
        current_direction2=key_actions[(key_actions.index(current_direction2)+1) % len(key_actions)]

def get_state1(speed=10,lookahead=1):
    global current_direction1,head_x1,head_y1
    points_l=[]
    points_r=[]
    points_u=[]
    points_d=[]
    
    for look in range(1,lookahead+1):
        point_l = (head_x1-look*speed,head_y1)
        point_r = (head_x1+look*speed,head_y1)
        point_u = (head_x1,head_y1-look*speed)
        point_d = (head_x1,head_y1+look*speed)
        points_l.append(point_l)
        points_r.append(point_r)
        points_u.append(point_u)
        points_d.append(point_d)

    dir_l = current_direction1 == pygame.K_LEFT
    dir_r = current_direction1 == pygame.K_RIGHT
    dir_u = current_direction1 == pygame.K_UP
    dir_d = current_direction1 == pygame.K_DOWN

    danger_straight=False
    danger_right=False
    danger_left=False
    
    # Danger Straight
    for look in range(lookahead):
        danger_straight = (dir_r and snake_collided1(points_r[look][0],points_r[look][1])) or (dir_l and snake_collided1(points_l[look][0],points_l[look][1])) or  (dir_u and snake_collided1(points_u[look][0],points_u[look][1])) or  (dir_d and snake_collided1(points_d[look][0],points_d[look][1]))
        if danger_straight==True:
            break
    
    # Danger Right
    for look in range(lookahead):
        danger_right = (dir_r and snake_collided1(points_d[look][0],points_d[look][1])) or (dir_d and snake_collided1(points_l[look][0],points_l[look][1])) or  (dir_l and snake_collided1(points_u[look][0],points_u[look][1])) or  (dir_u and snake_collided1(points_r[look][0],points_r[look][1]))
        if danger_right==True:
            break
    
    # Danger Left
    for look in range(lookahead):
        danger_left = (dir_r and snake_collided1(points_u[look][0],points_u[look][1])) or (dir_u and snake_collided1(points_l[look][0],points_l[look][1])) or (dir_l and snake_collided1(points_d[look][0],points_d[look][1])) or (dir_d and snake_collided1(points_r[look][0],points_r[look][1]))
        if danger_left==True:
            break
    state= (
        # Danger straight
        danger_straight ,

        # Danger right
        danger_right,

        # Danger left
        danger_left,
        
        # Move direction
        dir_l,
        dir_r,
        dir_u,
        dir_d,
        
        # Food location 
        food_x<head_x1,
        food_x>head_x1,
        food_y<head_y1,
        food_y<head_y1,
    )
    return state



def get_state2(speed=10,lookahead=1):
    global current_direction2,head_x2,head_y2,head_x1,head_y1,head_x2,snake_body1
    points_l=[]
    points_r=[]
    points_u=[]
    points_d=[]
    
    for look in range(1,lookahead+1):
        point_l = (head_x2-look*speed,head_y2)
        point_r = (head_x2+look*speed,head_y2)
        point_u = (head_x2,head_y2-look*speed)
        point_d = (head_x2,head_y2+look*speed)
        points_l.append(point_l)
        points_r.append(point_r)
        points_u.append(point_u)
        points_d.append(point_d)

    dir_l = current_direction2 == pygame.K_LEFT
    dir_r = current_direction2 == pygame.K_RIGHT
    dir_u = current_direction2 == pygame.K_UP
    dir_d = current_direction2 == pygame.K_DOWN

    danger_straight=False
    danger_right=False
    danger_left=False
    
    # Danger Straight
    for look in range(lookahead):
        danger_straight = (dir_r and mongoose_collided2(points_r[look][0],points_r[look][1])) or (dir_l and mongoose_collided2(points_l[look][0],points_l[look][1])) or  (dir_u and mongoose_collided2(points_u[look][0],points_u[look][1])) or  (dir_d and mongoose_collided2(points_d[look][0],points_d[look][1]))
        if danger_straight==True:
            break
    
    # Danger Right
    for look in range(lookahead):
        danger_right = (dir_r and mongoose_collided2(points_d[look][0],points_d[look][1])) or (dir_d and mongoose_collided2(points_l[look][0],points_l[look][1])) or  (dir_l and mongoose_collided2(points_u[look][0],points_u[look][1])) or  (dir_u and mongoose_collided2(points_r[look][0],points_r[look][1]))
        if danger_right==True:
            break
    
    # Danger Left
    for look in range(lookahead):
        danger_left = (dir_r and mongoose_collided2(points_u[look][0],points_u[look][1])) or (dir_u and mongoose_collided2(points_l[look][0],points_l[look][1])) or (dir_l and mongoose_collided2(points_d[look][0],points_d[look][1])) or (dir_d and mongoose_collided2(points_r[look][0],points_r[look][1]))
        if danger_left==True:
            break

    # Find closest snake body point to mongoose
    d_min = inf
    closest_x,closest_y = head_x1,head_y1
    for (x,y) in snake_body1[:]:
        d_cur = distance.euclidean([head_x2,head_y2],[x,y])
        if d_cur<d_min:
            d_min=d_cur
            closest_x=x
            closest_y=y
    state= (
        # Danger straight
        danger_straight ,

        # Danger right
        danger_right,

        # Danger left
        danger_left,
        
        # Move direction
        dir_l,
        dir_r,
        dir_u,
        dir_d,
        
        # Food location 
        food_x<head_x2,
        food_x>head_x2,
        food_y<head_y2,
        food_y<head_y2,

        # closest snake part location 
        closest_x<head_x2,
        closest_x>head_x2,
        closest_y<head_y2,
        closest_y<head_y2
    )
    return state

clock = pygame.time.Clock()
place_food()

try:
    while not game_over:
        show_score()    
        for event in pygame.event.get():
            print(food_x,food_y,head_x1,head_y1)
            if event.type==pygame.QUIT:
                plot(scores1, mean_scores1,scores2, mean_scores2,1,save=True)
                plot(scores1, mean_scores1,scores2, mean_scores2,2,save=True)
                q_table1=dict((str(','.join(map(str, k))), v) for k,v in q_table1.items())
                q_table2=dict((str(','.join(map(str, k))), v) for k,v in q_table2.items())       
                out_file = open("q_table_snake.json", "w")  
                json.dump(q_table1, out_file)
                out_file.close()
                out_file = open("q_table_mongoose.json", "w")  
                json.dump(q_table2, out_file)
                out_file.close()
                saved_params={}
                saved_params["epsilon1"]=epsilon1
                saved_params["LR1"]=LR1
                saved_params["discount1"]=discount1
                saved_params["state_next1"]=state_next1
                saved_params["reward_next1"]=reward_next1
                saved_params["action1"]=action1
                saved_params["epsilon2"]=epsilon2
                saved_params["LR2"]=LR2
                saved_params["discount2"]=discount2
                saved_params["state_next2"]=state_next2
                saved_params["reward_next2"]=reward_next2
                saved_params["action2"]=action2
                saved_params["max_games"]=max_games
                saved_params["scores1"]=scores1
                saved_params["mean_scores1"]=mean_scores1
                saved_params["record1"]=record1
                saved_params["score1"]=score1
                saved_params["n_games1"]=n_games1
                saved_params["total_score1"]=total_score1
                saved_params["scores2"]=scores2
                saved_params["mean_scores2"]=mean_scores2
                saved_params["record2"]=record2
                saved_params["score2"]=score2
                saved_params["n_games2"]=n_games2
                saved_params["total_score2"]=total_score2
                saved_params["current_direction1"]=current_direction1
                saved_params["current_direction2"]=current_direction2
                saved_params["head_x1"]=head_x1
                saved_params["head_y1"]=head_y1
                saved_params["snake_body1"]=snake_body1
                saved_params["head_x2"]=head_x2
                saved_params["head_y2"]=head_y2
                saved_params["food_x"]=food_x
                saved_params["food_y"]=food_y
                out_file = open("./savedparams_snakemongoose.json", "w")  
                json.dump(saved_params, out_file)
                out_file.close()
                pygame.image.save(display_board, "./snapshot_snakemongoose.jpeg")
                game_over=True
        
        # agent playing
        state1=get_state1()
        state2=get_state2()
        action1 = play_agent1(state1)
        action2 = play_agent2(state2)
        take_action1(action1)
        take_action2(action2)
        reward_next1=move_snake1()
        reward_next2=move_mongoose2()
        # state stores current direction and food location and collision
        state_next1=get_state1(lookahead=1)
        state_next2=get_state2(lookahead=1)
        update_qtable1(state1,action1,state_next1,reward_next1)
        update_qtable2(state2,action2,state_next2,reward_next2)
        clock.tick(30)

except KeyboardInterrupt:
    plot(scores1, mean_scores1,scores2, mean_scores2,1,save=True)
    plot(scores1, mean_scores1,scores2, mean_scores2,2,save=True)
    q_table1=dict((str(','.join(map(str, k))), v) for k,v in q_table1.items())
    q_table2=dict((str(','.join(map(str, k))), v) for k,v in q_table2.items())       
    out_file = open("q_table_snake.json", "w")  
    json.dump(q_table1, out_file)
    out_file.close()
    out_file = open("q_table_mongoose.json", "w")  
    json.dump(q_table2, out_file)
    out_file.close()
    saved_params={}
    saved_params["epsilon1"]=epsilon1
    saved_params["LR1"]=LR1
    saved_params["discount1"]=discount1
    saved_params["state_next1"]=state_next1
    saved_params["reward_next1"]=reward_next1
    saved_params["action1"]=action1
    saved_params["epsilon2"]=epsilon2
    saved_params["LR2"]=LR2
    saved_params["discount2"]=discount2
    saved_params["state_next2"]=state_next2
    saved_params["reward_next2"]=reward_next2
    saved_params["action2"]=action2
    saved_params["max_games"]=max_games
    saved_params["scores1"]=scores1
    saved_params["mean_scores1"]=mean_scores1
    saved_params["record1"]=record1
    saved_params["score1"]=score1
    saved_params["n_games1"]=n_games1
    saved_params["total_score1"]=total_score1
    saved_params["scores2"]=scores2
    saved_params["mean_scores2"]=mean_scores2
    saved_params["record2"]=record2
    saved_params["score2"]=score2
    saved_params["n_games2"]=n_games2
    saved_params["total_score2"]=total_score2
    saved_params["current_direction1"]=current_direction1
    saved_params["current_direction2"]=current_direction2
    saved_params["head_x1"]=head_x1
    saved_params["head_y1"]=head_y1
    saved_params["snake_body1"]=snake_body1
    saved_params["head_x2"]=head_x2
    saved_params["head_y2"]=head_y2
    saved_params["food_x"]=food_x
    saved_params["food_y"]=food_y
    out_file = open("./savedparams_snakemongoose.json", "w")  
    json.dump(saved_params, out_file)
    out_file.close()
    pygame.image.save(display_board, "./snapshot_snakemongoose.jpeg")
    

pygame.quit()
quit()



