import pygame,sys,json,sqlite3,time
from pygame.locals import QUIT,MOUSEBUTTONUP,BUTTON_WHEELUP,BUTTON_WHEELDOWN

pygame.init()

WHITE=(255,255,255)
B_GREY=(50,50,50)
BLACK=(0,0,0)
SITE=(255,0,0)
PORT=(255,255,0)
LOCK=(177,0,0)
OVER=(199,199,199)
Colors=[(128,128,0),(0,128,128),(0,128,0),(128,0,128),(0,0,128),(128,0,0),(45,72,88),(93,172,44),(80,23,0)]
Colors_site=[(192,192,0),(0,192,192),(0,192,0),(192,0,192),(0,0,192),(192,0,0),(45,72,88),(93,172,44),(80,23,0)]

screen=pygame.display.set_mode((1250,850))
pygame.display.set_caption("Evolution Display")
fpsClock=pygame.time.Clock()

board=pygame.Rect(25,25,800,800)

data=json.load(open('data.json'))
sp=data['site_position']
pp=data['port_position']

conn=sqlite3.connect('record.db')
cur=conn.cursor()

def get_rects(size):
    rects=[[] for _ in range(size)]
    r_size=800//size-4
    for i in range(size):
        for j in range(size):
            tmp=pygame.Rect(j*(2+r_size)+42,i*(2+r_size)+42,r_size,r_size)
            rects[i].append(tmp)
    return rects

rects=get_rects(data['size'])

def draw_info(ID,Delay,Remaind,s=screen):
    title,t_r=set_text((1050,200),'Solution')
    sub_title,st_r=set_text((1050,300),"Size:%s"%data['size'],size=30)
    iid,id_r=set_text((1050,350),"Step: %s"%ID,size=30)
    delay,delay_r=set_text((1050,400),"Delayd: %d"%Delay,size=30)
    s.blit(title,t_r)
    s.blit(sub_title,st_r)
    s.blit(iid,id_r)
    s.blit(delay,delay_r)
    draw_text((1050,450),"Remain: %d"%Remaind,size=30)


def set_text(center,text,anti=True,color=WHITE,size=60,family='freesansbold.ttf'):
    title=pygame.font.Font(family,size)
    titleSObj=title.render(text,anti,color)
    titleRect=titleSObj.get_rect()
    titleRect.center=center
    return titleSObj,titleRect

def draw_text(center,text,anti=True,color=WHITE,size=60,family='freesansbold.ttf',s=screen):
    res,res_r=set_text(center,text,anti,color,size,family)
    s.blit(res,res_r)

def draw_board(rs=rects,s=screen):
    s.fill(BLACK)
    pygame.draw.rect(s,WHITE,board)
    for rss in rs:
        for r in rss:
            pygame.draw.rect(s,B_GREY,r)

def draw_site_port(s=screen):
    ind=0
    for t in sp:
        r=rects[t[0]][t[1]]
        #pygame.draw.rect(s,Colors_site[ind],r)
        pygame.draw.ellipse(s,Colors_site[ind],r)
        ind+=1
    for t in pp:
        r=rects[t[0]][t[1]]
        pygame.draw.ellipse(s,PORT,r)

def draw_lock(lock_block,s=screen):
    for lb in lock_block:
        r=rects[lb[0]][lb[1]]
        pygame.draw.rect(s,LOCK,r)

def draw_box(boxes,actions,move_num,s=screen):
    drc={'U':[0,-1],'D':[0,1],'R':[1,0],'S':[0,0],'A':[0,0]}
    def move(box,a):
        new_box=pygame.Rect(box.left+move_num*(drc[a][0]),box.top+move_num*(drc[a][1]),box.width,box.height)
        return new_box
    for i in range(len(boxes)):
        for j in range(len(boxes[i])):
            b=boxes[i][j]
            a=actions[i][j]
            r=move(rects[b[0]][b[1]],a)
            pygame.draw.rect(s,Colors[i],r)

def draw_over():
    draw_text((425,425),'Completed!',True,OVER,80)


def get_step(id):
    res=cur.execute("SELECT ID,STEP,DELAYED,REMAIND from RECORD where ID=%d"%id)
    s=res.fetchone()
    if s==None:
        return False,False,False,False
    return s[0],json.loads(s[1].decode()),s[2],s[3]

def get_lock(step):
    lock_block=[]
    for i in range(len(step)):
        for j in range(len(step[i])):
            if 'X' in step[i][j]:
                lock_block.append([i,j])
    return lock_block

def get_box(step):
    boxes=[[] for _ in range(data['site'])]
    actions=[[] for _ in range(data['site'])]
    for i in range(len(step)):
        for j in range(len(step[i])):
            if len(step[i][j])>=2:
                s=eval(step[i][j][0])
                a=step[i][j][1]
                boxes[s-1].append([i,j])
                actions[s-1].append(a)
    return boxes,actions

# def draw_over(s=screen):
#     draw_board()
#     draw_info(ID,delay,remaind)
#     lk=get_lock(step)
#     draw_lock(lk)
#     boxes,actions=get_box(step)
#     draw_box(boxes,actions,f)
#     draw_site_port()
#     pygame.display.update()

last_ID=0
last_step=[]
last_delay=0
last_remaind=0

def set_last(ID,step,delay,remaind):
    global last_ID,last_delay,last_step,last_remaind
    last_ID,last_step,last_delay,last_remaind=ID,step,delay,remaind

def get_last():
    global last_ID,last_delay,last_step,last_remaind
    return last_ID,last_step,last_delay,last_remaind

def draw_one_step(id):
    f=0
    flag=True
    ID,step,delay,remaind=get_step(id)
    if ID==False:
        flag=False
        ID,step,delay,remaind=get_last()
    else:
        set_last(ID,step,delay,remaind)
    draw_board()
    draw_info(ID,delay,remaind)
    lk=get_lock(step)
    draw_lock(lk)
    boxes,actions=get_box(step)
    if flag==True:
        draw_box(boxes,actions,f)
    draw_site_port()
    if flag==False:
        draw_over()
    pygame.display.update()

id=1
p=5
while True:
    for event in pygame.event.get():
        if event.type==QUIT:
            quit()
            sys.exit()
        elif event.type==MOUSEBUTTONUP:
            time.sleep(5)
        # elif event.type==BUTTON_WHEELUP:
        #     p=min(2,3+p)
        # elif event.type==BUTTON_WHEELDOWN:
        #     p=max(1,p-3)


    draw_one_step(id)
    id+=1
    # draw_board()
    # draw_site_port()
    # draw_info()
    # pygame.display.update()
    fpsClock.tick(p)
    # print(get_step(10))
    

