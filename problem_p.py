import numpy as np 
import sys,os,time,argparse,json,random
from queue import Queue

width=20
height=20
sites_num=5
destiny_num=5
length=50

direction={'up':[-1,0],'down':[1,0],'right':[0,1],'stay':[0,0]}
sites_position=[np.array([height//(sites_num-1)*i,0]) for i in range(sites_num-1)]+[np.array([height-1,0])]
destiny_position=[np.array([height//(destiny_num-1)*i,width-1]) for i in range(destiny_num-1)]+[np.array([height-1,width-1])]

def data_generator(num=length):
    return [[random.choice(range(1,destiny_num+1)) for i in range(num)] for i in range(sites_num)]

def data_show(data):
    for i in range(len(data)):
        print(f"第{i+1}个货物序列",end=': ')
        for j in data[i]:
            print(f"{j}",end=' ')
        print("end")

class board:
    def __init__(self,data=None):
        self.count=0
        self.width=width
        self.height=height
        self.boxes=list()
        if data==None:
            self.data=data_generator(length)
        else:
            self.data=data
        self.init_view()
        self.total_stay=0
        self.run()

        

    def init_view(self):
        self.view=np.array([[' ' for i in range(self.width)] for j in range(self.height)])
        for site in sites_position:
            self.view[site[0],site[1]]='S'
        for des in destiny_position:
            self.view[des[0],des[1]]='D'
        

    def add_box(self,origin,destiny):
        b=box(origin,destiny)
        self.boxes.append(b)

    def new_boxes(self):
        for site in range(len(self.data)):
            if len(self.data[site])!=0:
                des=self.data[site].pop(0)-1
                self.add_box(site,des)

    def move_boxes(self):
        temp_remove=[]
        for b in self.boxes:
            b.move(self.view)
            if (b.position==b.destiny_position).all():
                temp_remove.append(b)
            else:
                self.update_view_single(b)
        for b in temp_remove:
            self.boxes.remove(b)
            self.total_stay+=b.stay
    
    def update_view(self):
        # self.init_view()
        for box in self.boxes:
            self.view[box.position[0],box.position[1]]=box.destiny+1
    
    def update_view_single(self,b):
        self.view[b.position[0],b.position[1]]=b.destiny+1

    def step(self):
        self.init_view()
        self.count+=1
        self.move_boxes()
        #self.update_view()
        self.new_boxes()
        #self.show()

    def show(self):
        print("----------new step-----------")
        for i in self.view:
            print("|",end=' ')
            for j in i:
                print(j,end=' ')
            print("|")

    def run(self):
        self.new_boxes()
        while len(self.boxes)>0:
            self.step()
            #time.sleep(0.2)
        print(f"All box are delivered.The total time is {self.count}.The total stay time is :{self.total_stay}")



class box:
    def __init__(self,origin,destiny):
        self.origin=origin
        self.destiny=destiny
        self.destiny_position=destiny_position[self.destiny]
        self.position=sites_position[origin]
        self.route=self.set_route()
        self.stay=0

    def set_route(self):
        o=self.position
        d=self.destiny_position
        route=[]
        hori=d[1]-o[1]
        vert=d[0]-o[0]
        if vert<0:
            for i in range(-vert):
                route.append('up')
        else:
            for i in range(vert):
                route.append('down')
        for i in range(hori):
            route.append('right')
        
        np.random.shuffle(route)
        return list(route)

    def step(self,d,view):
        if d=='stay':
            return True
        tmp_position=self.position+direction[d]
        if self.check_out(tmp_position) and self.check_block(tmp_position,view):
            self.position=tmp_position
            return True
        else:
            #self.route.append(d)
            return False


    def check_out(self,p):
        if p[0]>=width or p[0]<0 or p[1]>=height or p[1]<0:
            return False
        # elif somecondition:
        #     pass
        else:
            return True
    
    def check_block(self,p,view):
        if view[p[0],p[1]] not in [' ','D']:
            return False
        else:
            return True

    def move(self,view):
        if len(self.route)==0:
            return
        block=set()
        not_success=[]
        try_num=len(self.route)
        step_success=False
        while try_num!=0:
            try_num-=1
            d=self.route.pop(0)
            if d in block:
                not_success.append(d)
            else:
                f=self.step(d,view)
                if f==True:
                    step_success=True
                    break
                else:
                    block.add(d)
                    not_success.append(d)
        self.route+=not_success
        if step_success==True:
            pass
        else:
            self.step('stay',view)
            self.stay+=1

class solution_generator:
    def __init__(self,data):
        pass
        

if __name__=="__main__":
    b=board()

        
        
                