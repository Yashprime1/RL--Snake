import pygame
import random
import random
import itertools
import json 
import os
import matplotlib.pyplot as plt
from IPython import display

plt.ion()

def plot(scores, mean_scores,save=False):
    display.clear_output(wait=True)
    display.display(plt.gcf())
    plt.clf()
    plt.title('Training...')
    plt.xlabel('Number of Games')
    plt.ylabel('Score')
    plt.plot(scores)
    plt.plot(mean_scores)
    plt.ylim(ymin=0)
    plt.text(len(scores)-1, scores[-1], str(scores[-1]))
    plt.text(len(mean_scores)-1, mean_scores[-1], str(mean_scores[-1]))
    plt.show(block=False)
    plt.pause(.1)
    if save==True:
        plt.savefig('qlearning_main.png')
    

###### Initialization ######

# For screen
dimension_x=200
dimension_y=200

# For snake
snake_color=(0,0,255) #blue
head_x=int(dimension_x/2)
head_y=int(dimension_y/2)
snake_body=[(head_x,head_y)]

# For food
food_color=(255,0,0) #Red
food_x=random.randrange(0,dimension_x,10)
food_y=random.randrange(0,dimension_y,10)

# For RL Agent

states = list(itertools.product(*[(0, 1)] * 11))
actions=[0,1,2]
q_table={}
for state in states:
    for action in actions: 
        q_table[(*state,action)]=0

try:
    with open('./q_table_main.json') as json_file:
        if os.stat("./q_table_main.json").st_size != 0:
            q_table = json.load(json_file)
            q_table=dict((tuple(map(int,k.split(","))), v) for k,v in q_table.items())
        else:
            print("File empty")
except OSError:
    print("File not found")

    
epsilon=0.7
LR=0.1
discount=0.6
state_next=()
reward_next=0
action=1 # initially right
t=1
max_games=10000


# For game
black=(0,0,0)
scores=[]
mean_scores=[]
record=0
score=0
n_games=1
total_score=0
game_over= False
current_direction = pygame.K_RIGHT


try:
    with open('./savedparams_main.json') as json_file:
        if os.stat("./savedparams_main.json").st_size != 0:
            saved_params = json.load(json_file)
            epsilon=saved_params["epsilon"]
            LR=saved_params["LR"]
            discount=saved_params["discount"]
            state_next=saved_params["state_next"]
            reward_next=saved_params["reward_next"]
            action=saved_params["action"]
            max_games=saved_params["max_games"]
            scores=saved_params["scores"]
            mean_scores=saved_params["mean_scores"]
            record=saved_params["record"]
            score=saved_params["score"]
            n_games=saved_params["n_games"]
            total_score=saved_params["total_scores"]
            current_direction=saved_params["current_direction"]
            head_x=saved_params["head_x"]
            head_y=saved_params["head_y"]
            snake_body=saved_params["snake_body"]
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
    global dimension_x,dimension_y,display_board,food_color,food_x,food_y,snake_body
    food_x=random.randrange(0,dimension_x,10)
    food_y=random.randrange(0,dimension_y,10)
    if((food_x,food_y) in snake_body) : place_food()
    pygame.draw.rect(display_board,food_color,[food_x,food_y,10,10])     
    pygame.display.update()

def show_score():
    global score,display_board
    """system font"""
    font = pygame.font.SysFont("Segoe UI", 35)
    textsurface = font.render("Score :{} ".format(score), False,(0,255,0))  # "text", antialias, color
    display_board.blit(textsurface, (0, 0))

# move snake on screen
def move_snake(speed=10):
    global game_over,black,head_x,head_y,snake_body,snake_color,food_x,food_y,current_direction,record,score,display_board
    reward=0
    # remove previous snake from screen
    for (x,y) in snake_body:
        pygame.draw.rect(display_board,black,[x,y,10,10])     
        pygame.display.update()

    if current_direction == pygame.K_LEFT:
        head_x -= speed
    if current_direction == pygame.K_RIGHT:
        head_x += speed
    if current_direction == pygame.K_UP:
        head_y -= speed
    if current_direction == pygame.K_DOWN:
        head_y += speed
    
    if snake_collided(head_x,head_y):
        reward-=10
        init_game()
    if head_x==food_x and head_y==food_y:
        snake_body.insert(0,(head_x,head_y))
        score+=1
        reward+=10
        display_board.fill(black)
        place_food()
    else:
        reward+=(-0.01)
        snake_body.insert(0,(head_x,head_y))
        snake_body.pop()
    
    # add new snake from screen
    for (x,y) in snake_body:
        pygame.draw.rect(display_board,snake_color,[x,y,10,10])     
        pygame.display.update()
    return reward

def snake_collided(x,y):
    global dimension_x,dimension_y,snake_body
    if x<0 or y<0 or x>dimension_x or y>dimension_y or (x,y) in snake_body[1:]:
        return True
    return False

def init_game():
    global head_x,head_y,snake_body,food_x,food_y,current_direction,display_board,score,mean_scores,scores,total_score,epsilon,n_games,record,max_games    
    if score>record:
        record=score
    print('Game ', n_games, 'Score', score, 'Record:', record)
    scores.append((score))
    total_score += score
    mean_score = total_score / n_games
    n_games+=1
    mean_scores.append(mean_score)
    plot(scores, mean_scores)
    if(epsilon>(n_games/max_games)): epsilon-=(n_games/max_games)
    display_board.fill(black)
    head_x=int(dimension_x/2)
    head_y=int(dimension_y/2)
    snake_body=[(head_x,head_y)]
    food_x=random.randrange(0,dimension_x,10)
    food_y=random.randrange(0,dimension_y,10)
    current_direction = pygame.K_RIGHT
    score=0
    if(epsilon>0): epsilon-=0.0001
    place_food()


###### RL Agent ######
def play_agent(state):
    global q_table,epsilon,actions
    print("Agent : ")
    # step 2: choose action e-greedy 
    if random.random()<epsilon:
        max_action = random.randint(0,len(actions)-1)
        print("Exploration : ",max_action)
        return max_action
    else:
        max_action=-1
        max_qvalue=0
        # t_exploit+=1
        for action in actions:
            if(q_table[(*state,action)]>max_qvalue): 
                max_qvalue=q_table[(*state,action)]
                max_action=action
        if max_action==-1:
            max_action = random.randint(0,len(actions)-1)
        print("Exploitation : ",max_action)
        # if t_exploit>100:
        #     if n_games>100:
        #         epsilon=0.1
        #     else:
        #         epsilon=0.4
        #     t_exploit=1
        return max_action
   
   
def update_qtable(state,action,state_next,reward_next):
    global q_table,epsilon,actions,LR,discount

    # step 3: update q_table 
    
    max_action=0
    max_qvalue=0
    for act in actions:
        if(q_table[(*state_next,act)]>max_qvalue):
            max_qvalue=q_table[(*state_next,act)]
            max_action=act
    q_next = q_table[(*state_next,max_action)] 
    
    q_table[(*state,action)] = q_table[(*state,action)] + LR * (reward_next + discount*q_next - q_table[(*state,action)] )

def take_action(action):
    global current_direction
    key_actions=[pygame.K_LEFT,pygame.K_UP,pygame.K_RIGHT,pygame.K_DOWN]
    if(action==0): pass
    elif(action==1):
        current_direction=key_actions[(key_actions.index(current_direction)-1) % len(key_actions)] 
    elif(action==2):
        current_direction=key_actions[(key_actions.index(current_direction)+1) % len(key_actions)]

def get_state(speed=10,lookahead=1):
    global current_direction,head_x,head_y
    points_l=[]
    points_r=[]
    points_u=[]
    points_d=[]
    
    for look in range(1,lookahead+1):
        point_l = (head_x-look*speed,head_y)
        point_r = (head_x+look*speed,head_y)
        point_u = (head_x,head_y-look*speed)
        point_d = (head_x,head_y+look*speed)
        points_l.append(point_l)
        points_r.append(point_r)
        points_u.append(point_u)
        points_d.append(point_d)

    dir_l = current_direction == pygame.K_LEFT
    dir_r = current_direction == pygame.K_RIGHT
    dir_u = current_direction == pygame.K_UP
    dir_d = current_direction == pygame.K_DOWN

    danger_straight=False
    danger_right=False
    danger_left=False
    
    # Danger Straight
    for look in range(lookahead):
        danger_straight = (dir_r and snake_collided(points_r[look][0],points_r[look][1])) or (dir_l and snake_collided(points_l[look][0],points_l[look][1])) or  (dir_u and snake_collided(points_u[look][0],points_u[look][1])) or  (dir_d and snake_collided(points_d[look][0],points_d[look][1]))
        if danger_straight==True:
            break
    
    # Danger Right
    for look in range(lookahead):
        danger_right = (dir_r and snake_collided(points_d[look][0],points_d[look][1])) or (dir_d and snake_collided(points_l[look][0],points_l[look][1])) or  (dir_l and snake_collided(points_u[look][0],points_u[look][1])) or  (dir_u and snake_collided(points_r[look][0],points_r[look][1]))
        if danger_right==True:
            break
    
    # Danger Left
    for look in range(lookahead):
        danger_left = (dir_r and snake_collided(points_u[look][0],points_u[look][1])) or (dir_u and snake_collided(points_l[look][0],points_l[look][1])) or (dir_l and snake_collided(points_d[look][0],points_d[look][1])) or (dir_d and snake_collided(points_r[look][0],points_r[look][1]))
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
        food_x<head_x,
        food_x>head_x,
        food_y<head_y,
        food_y<head_y,
    )
    return state

clock = pygame.time.Clock()
place_food()

try:
    while not game_over:
        
        show_score()    
        
        for event in pygame.event.get():
            print(food_x,food_y,head_x,head_y)
            if event.type==pygame.QUIT:
                plot(scores, mean_scores,save=True)
                # the json file where the output must be stored
                print(q_table,"It is getting saved\n")
                q_table=dict((str(','.join(map(str, k))), v) for k,v in q_table.items())
                pygame.image.save(display_board, "./snapshot_main.jpeg")
                out_file = open("./q_table_main.json", "w")  
                json.dump(q_table, out_file)
                out_file.close()
                saved_params={}
                saved_params["epsilon"]=epsilon
                saved_params["LR"]=LR
                saved_params["discount"]=discount
                saved_params["state_next"]=state_next
                saved_params["reward_next"]=reward_next
                saved_params["action"]=action
                saved_params["max_games"]=max_games
                saved_params["scores"]=scores
                saved_params["mean_scores"]=mean_scores
                saved_params["record"]=record
                saved_params["score"]=score
                saved_params["n_games"]=n_games
                saved_params["total_scores"]=total_score
                saved_params["current_direction"]=current_direction
                saved_params["head_x"]=head_x
                saved_params["head_y"]=head_y
                saved_params["snake_body"]=snake_body
                saved_params["food_x"]=food_x
                saved_params["food_y"]=food_y
                out_file = open("./savedparams_main.json", "w")  
                json.dump(q_table, out_file)
                out_file.close()
                game_over=True
        
        # agent playing
        state=get_state()
        action = play_agent(state)
        take_action(action)
        reward=move_snake()
        next_state=get_state()
        update_qtable(state,action,next_state,reward)
        t+=1
        clock.tick(30)

except KeyboardInterrupt:
    plot(scores, mean_scores,save=True)
    # the json file where the output must be stored
    print(q_table,"It is getting saved\n")
    q_table=dict((str(','.join(map(str, k))), v) for k,v in q_table.items())
    pygame.image.save(display_board, "./snapshot_main.jpeg")
    out_file = open("./q_table_main.json", "w")  
    json.dump(q_table, out_file)
    out_file.close()
    saved_params={}
    saved_params["epsilon"]=epsilon
    saved_params["LR"]=LR
    saved_params["discount"]=discount
    saved_params["state_next"]=state_next
    saved_params["reward_next"]=reward_next
    saved_params["action"]=action
    saved_params["max_games"]=max_games
    saved_params["scores"]=scores
    saved_params["mean_scores"]=mean_scores
    saved_params["record"]=record
    saved_params["score"]=score
    saved_params["n_games"]=n_games
    saved_params["total_scores"]=total_score
    saved_params["current_direction"]=current_direction
    saved_params["head_x"]=head_x
    saved_params["head_y"]=head_y
    saved_params["snake_body"]=snake_body
    saved_params["food_x"]=food_x
    saved_params["food_y"]=food_y
    out_file = open("./savedparams_main.json", "w")  
    json.dump(saved_params, out_file)
    out_file.close()
    game_over=True

pygame.quit()
quit()



