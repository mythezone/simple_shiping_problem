import numpy as np 
import sys,os,time,argparse,json,random,copy,collections,argparse
from queue import Queue
import sqlite3


def new_database(db_file):
    if os.path.exists(db_file):
        os.remove(db_file)
    conn=sqlite3.connect('record.db')
    c=conn.cursor()
    c.execute('''
            CREATE TABLE RECORD (
                ID INT PRIMARY_KEY NOT NULL,
                STEP BLOB NOT NULL,
                DELAYED INT,
                REMAIND INT

            );''')
    conn.commit()
    return conn

class Evolution:
    def __init__(self,population):
        pass

class Mid:
    def __init__(self,problem):
        self.site_position=problem['site_position']
        self.port_position=problem['port_position']
        self.data=problem
        self.set_path()
        self.goods_data=problem['goods_data']
        #self.get_solution()

    def get_priority(self):
        priority=range(self.data['port'])
        random.shuffle(priority)
        return priority

    def generator(self,population):
        popu=[]
        for _ in range(population):
            solution=self.get_solution()
            popu.append(solution)
        #priority=self.get_priority()
        return popu#,priority

    def get_solution(self):
        self.solution=[[] for _ in range(self.data['port'])]
        for i in range(self.data['port']):
            goods=self.goods_data[i]
            for g in goods:
                p=self.path[i][g-1]
                path=self.generate_path(p)
                self.solution[i].append(path)
        #print("Solutions generated.")
        return self.solution

    def generate_path(self,p):
        down=p[0]
        right=p[1]
        path=[]
        def add_path(c,num,path):
            for _ in range(num):
                path.append(c)
        if down>=0:
            add_path('D',down,path)
        else:
            add_path('U',-down,path)
        add_path('R',right,path)
        random.shuffle(path)
        random.shuffle(path)
        random.shuffle(path)
        return path

    def check_path(self,path):
        count=0
        if 'U' in path:
            count+=1
        if 'R' in path:
            count+=1
        if 'D' in path:
            count+=1
        if count==3:
            return False
        return True

    def set_path(self):
        self.path=[[[0,0] for _ in range(self.data['port'])] for _ in range(self.data['site'])]
        for i in range(self.data['port']):
            for j in range(self.data['site']):
                d=self.get_distance(self.port_position[i],self.site_position[j])
                self.path[i][j]=d

    def get_distance(self,p1,p2):
        down=p2[0]-p1[0]
        right=p2[1]-p1[1]
        return [down,right]

class Simulator:
    def __init__(self,data_name,population,generation):
        self.data=json.load(open(data_name))
        self.s=Mid(self.data)
        self.size=self.data['size']
        self.port_position=self.data['port_position']
        self.site_position=self.data['site_position']
        self.goods_data=self.data['goods_data']
        self.one_port_goods_num=len(self.goods_data[0])
        self.locked=self.init_lock()
        self.view=self.init_view()
        
        self.population=population
        self.generation=generation

    def acceptable(self,ss):
        threshold=self.one_port_goods_num+2*self.size
        if self.fitness(ss[0][0])<=threshold:
            return True
        else:
            return False

    def evolution(self):
        population_lst = self.s.generator(self.population)
        population_lst = [(item, self.fitness(item)) for item in population_lst]
        population_lst = self.sorter(population_lst)
        for i in range(self.generation):
            child_lst = list()
            for single_item in population_lst:
                if self.selector(single_item, population_lst):
                    result_item = self.mutation(single_item)
                    child_lst.append(result_item)
                    result_item=self.crossover(single_item,population_lst)
                    child_lst += result_item
            for _ in range(5):
                child_lst.append(self.s.get_solution())
            child_lst=self.s.generator(10)
            child_lst = [(item, self.fitness(item)) for item in child_lst]
            population_lst += child_lst
            population_lst = self.sorter(population_lst)
            population_lst = population_lst[: self.population]
            print("In " + str(i+1) + " generation: ",end=' ')
            if self.acceptable(population_lst):
                return population_lst[0], i+1
        
        return population_lst[0], self.generation
    
    def init_view(self):
        return [[' ' for _ in range(self.size)] for _ in range(self.size)]

    def init_record(self):
        return [['' for _ in range(self.size)] for _ in range(self.size)]
    
    def init_lock(self):
        return [[[] for _ in range(self.size)] for _ in range(self.size)]

    def init_delay_matrix(self):
        return [[0 for _ in range(self.one_port_goods_num)] for _ in range(self.data['port'])]

    def sorter(self,ss):
        h=[ss[i][1] for i in range(len(ss))]
        print(sorted(h)[:10])
        #a=np.array(ss)
        #print(a.shape)
        def func(s):
            return s[1]
        return sorted(ss,key=func)

    def selector(self,s,ss):
        
        l=len(ss)
        if ss.index(s)<l//2:
            return True
        else:
            return False

    def crossover_two(self,sx,s2):
        s1=copy.deepcopy(sx)
        m1=self.init_delay_matrix()
        self.fitness(s1[0],matrix=m1)
        #print("m1\n",m1)
        #time.sleep(2)
        m2=self.init_delay_matrix()
        self.fitness(s2[0],matrix=m2)
        minus=np.array(m1)-np.array(m2)
        #print(minus)
        change_index=[]
        for i in range(len(minus)):
            change_index.append([i,np.argmax(minus[i])])
        for index in change_index:
            s1[0][index[0]][index[1]]=s2[0][index[0]][index[1]]
        #res=self.fitness(s1[0])
        # print("S1[0] crossover:",s1[0])
        # exit()
        return s1[0]#(s1,res)
    
    def crossover(self,s1,ss):
        ls=[]
        for i in range(2):
            ls.append(self.crossover_two(s1,ss[i]))
        return ls

    def mutation(self,s2):
        s1=copy.deepcopy(s2)
        m1=self.init_delay_matrix()
        self.fitness(s1[0],matrix=m1)
        change_index=[]
        for i in range(len(m1)):
            change_index.append([i,np.argmax(m1[i])])
        for index in change_index:
            random.shuffle(s1[0][index[0]][index[1]])
        #res=self.fitness(s1[0])
        # print("S1[0] mutation:",s1[0])
        # exit()
        return s1[0]#(s1,res)
        
        #print("m1\n",m1)
        #time.sleep(2)
        # self.show_view(m1,self.locked)
        # self.show_view(m2,self.locked)

    def set_default_view(self,view):
        for s in self.data['site_position']:
            view[s[0]][s[1]]='S'
        for p in self.data['port_position']:
            view[p[0]][p[1]]='P'
        return view

    def set_box_in_view(self,box,view):
        pos=box.pos
        if view[pos[0]][pos[1]]==' ':
            view[pos[0]][pos[1]]=box.dist
            return True
        else:
            return False

    def show_view(self,view,lock):
        d='--'*((self.data['size']+2)//2)

        def l2s(arr):
            res=''
            for s in arr:
                res+=s+" "
            return res

        def ll2s(arr):
            res=''
            for s in arr:
                if s==[]:
                    res+="  "
                else:
                    res+="X "
            return res

        print("%s Map %s%s Lock %s"%(d,d,d,d))
        for i in range(len(view)):
            s=l2s(view[i])
            lk=ll2s(lock[i])
            print('|',s,'|',lk,'|')
        print("%s%s  End  %s%s"%(d,d,d,d))

    def fitness(self,solution,priority=None,matrix=None,show=False,record=False):
        priority=range(self.data['port'])
        self.view=self.init_view()
        self.locked=self.init_lock()
        steps=1
        self.total_delay=0
        s=copy.deepcopy(solution)
        goods=copy.deepcopy(self.goods_data)
        self.goods_num=0
        for _ in goods:
            self.goods_num+=len(_)
        boxes=[]
        conn=None
        self.count=1
        if record!=False:
            conn=new_database(record)
        
        def set_action(b,record):
            record[b.pos[0]][b.pos[1]]=b.dist+b.action

        def set_lock(record):
            for i in range(len(self.locked)):
                for j in range(len(self.locked[i])):
                    if self.locked[i][j]!=[]:
                        record[i][j]+='X'

        def step():
            step_record=self.init_record()
            temp_remove=[]
            #record_file='record.json'
            for b in boxes:
                #if box.complete:
                if record!=False:
                    set_action(b,step_record)
                b.move(self.view,self.locked)
                if len(b.path)==0:
                    self.view[b.pos[0]][b.pos[1]]=' '
                    temp_remove.append(b)
            if record!=False:
                set_lock(step_record)
            #json.dump(step_record,open(record_file,'+w'))
            for b in temp_remove:
                if matrix!=None:
                    #print(b.port,b.num)
                    matrix[b.port][b.num]=b.delay
                self.goods_num-=1
                self.total_delay+=b.delay
                boxes.remove(b)
            add_box()
            if conn!=None:
                c=conn.cursor()
                #print(step_record)
                tmp=json.dumps(step_record).encode()
                c.execute("INSERT INTO RECORD (ID,STEP,DELAYED,REMAIND) \
                            VALUES (?,?,?,?)",(self.count,tmp,self.total_delay,self.goods_num))
                conn.commit()
            self.count+=1
        
            
        def add_box():
            for i in priority:
                port_pos=self.port_position[i]
                if self.view[port_pos[0]][port_pos[1]] !=' ':
                    continue
                # try:
                if len(s[i])==0:
                    continue
                # except Exception as e:
                #     print(e)
                #     print(s[i])
                #     exit()
                path=s[i].pop(0)
                num=self.one_port_goods_num-len(goods[i])
                site=goods[i].pop(0)
                b=box(port_pos,i,site,path,self.view,num)
                boxes.append(b)
                #if record!=None:

        step()
        while self.goods_num>0:
            step()
            steps+=1
            if show:
                time.sleep(0.1)
                self.show_view(self.view,self.locked)
        if conn!=None:
            conn.close()
        #print("Total steps:%s, Total delay:%s"%(steps,self.total_delay))
        return steps#,self.total_delay

    # def fitness2(self,solution):
    #     goods=copy.deepcopy(self.goods_data)
    #     self.goods_num=0
    #     self.view=self.init_view()
    #     s=copy.deepcopy(solution)
    #     self.total_collision=0
    #     for _ in goods:
    #         self.goods_num+=len(_)
    #     self.boxes=[]
    #     while self.goods_num>0:
    #         self.move_box()
    #         self.add_box(s,goods)
    #         time.sleep(0.2)
    #         self.show_view(self.view,self.locked)
    #     return self.total_collision

    # def set_view(self,pos,c):
    #     self.view[pos[0]][pos[1]]=c

    # def move_box(self):
    #     tmp_remove=[]
    #     tl=[i for i in range(len(self.boxes))]
    #     random.shuffle(tl)
    #     for i in tl:
    #         b=self.boxes[i]
    #         if len(b.path)==0:
    #             tmp_remove.append(b)
    #             self.set_view(b.pos,' ')
    #             continue
    #         b.move2(self.view)
    #     for b in tmp_remove:
    #         self.total_collision+=b.collision
    #         #print("Total collision:",self.total_collision)
    #         self.boxes.remove(b)
    #         self.goods_num-=1
            
    
    # def add_box(self,s,goods):
    #     for i in range(self.data['port']):
    #         port_pos=self.port_position[i]
    #         if self.view[port_pos[0]][port_pos[1]] !=' ':
    #             continue
    #         if len(s[i])==0:
    #             continue
    #         path=s[i].pop(0)
    #         site=goods[i].pop(0)
    #         b=box(port_pos,i,site,path,self.view,0)
    #         self.boxes.append(b)
        
        


class box:
    def __init__(self,port_pos,port,site,path,view,num):
        self.num=num
        self.port=port
        self.site=site
        self.dist=str(site)
        self.pos=port_pos
        self.path=path
        self.real_path=[]
        self.delay=0
        self.complete=False
        view[self.pos[0]][self.pos[1]]=self.dist
        self.collision=0
        self.id=time.time()
        self.action='A'

    def tmp_position(self,direction):
        pos=self.pos
        d={"U":[-1,0],"D":[1,0],"R":[0,1],"S":[0,0]}
        return [pos[0]+d[direction][0],pos[1]+d[direction][1]]

    def set_view(self,pos,c,view):
        view[pos[0]][pos[1]]=c

    def release_lock(self,pos,lock):
        # if lock[pos[0]][pos[1]]!=[]:
        lock[pos[0]][pos[1]].pop(0)

    def step(self,d,view,lock,last=False):
        if d=='S':
            #self.action='S'
            return True
        tmp_p=self.tmp_position(d)

        # if last==True and view[tmp_p[0]][tmp_p[1]]==' ':
        #     #tmp_p=self.tmp_position(d)
        #     self.set_view(self.pos,' ',view)
        #     self.set_view(tmp_p,self.dist,view)
        #     self.pos=tmp_p
        #     return True
        # if last==True:
        #     return True
        
        #tmp_p=self.tmp_position(d)
        #if self.check_view(tmp_p,view,lock):
        if view[tmp_p[0]][tmp_p[1]]!=' ':
            return False
        mono=self.check_mono(self.path+self.not_success)

        # if mono==False:
        #     self.set_view(self.pos,' ',view)
        #     self.set_view(tmp_p,self.dist,view)
        #     self.pos=tmp_p
        #     return True


        if lock[tmp_p[0]][tmp_p[1]]==[]:
            self.set_view(self.pos,' ',view)
            self.set_view(tmp_p,self.dist,view)
            self.pos=tmp_p
            if mono!=False:
                self.lock_path(self.pos,self.path+self.not_success,lock)
            return True

        

        if lock[tmp_p[0]][tmp_p[1]][0]==self.id:
            self.release_lock(tmp_p,lock)
            self.set_view(self.pos,' ',view)
            self.set_view(tmp_p,self.dist,view)
            self.pos=tmp_p
            return True
        return False

    def move(self,view,lock):
        if len(self.path)==0:
            return
        # elif len(self.path)==1:
        #     self.final_pos=self.tmp_position(self.path[0])
        #     if view[self.final_pos[0]][self.final_pos[1]]==' ':
        #         view[self.pos[0]][self.pos[1]]=' '
        #         view[self.final_pos[0]][self.final_pos[1]]=self.dist
        #         self.pos=self.final_pos
        #         return

        block=set()
        self.not_success=[]
        try_num=len(self.path)
        step_success=False
        
        while try_num!=0:
            try_num-=1
            d=self.path.pop(0)
            # if len(self.path)+len(self.not_success)==0:
            #     step_success=True
            #     self.action=d
            #     self.step(d,view,lock,True)
            #     return
            if d in block:
                self.not_success.append(d)
            else:
                
                f=self.step(d,view,lock)
                if f==True:
                    step_success=True
                    self.action=d
                    break
                else:
                    block.add(d)
                    self.not_success.append(d)
        self.path+=self.not_success
        if step_success==True:
            pass
        else:
            self.step("S",view,lock)
            self.delay+=1
            self.action='S'

    def lock_pos(self,pos,locked):
        locked[pos[0]][pos[1]].append(self.id)

    def next_pos(self,pos,direction):
        d={"U":[-1,0],"D":[1,0],"R":[0,1],"S":[0,0]}
        return [pos[0]+d[direction][0],pos[1]+d[direction][1]]
    
    def lock_path(self,pos,path,locked):
        for d in path:
            pos=self.next_pos(pos,d)
            self.lock_pos(pos,locked)

    def check_path(self,pos,path,lock):
        for d in path:
            pos=self.next_pos(pos,d)
            if lock[pos[0]][pos[1]]!=[]:
                return False
        return True
            

    def check_mono(self,path):
        res=''
        if 'U' in path:
            res+='U'
        if 'D' in path:
            res+='D'
        if 'R' in path:
            res+='R'
        if len(res)==1 and res!='R':
            return res
        else:
            return False

    def check_view(self,pos,view,lock):
        if view[pos[0]][pos[1]] != ' ':
            return False
        else:
            if lock[pos[0]][pos[1]]==[]:
                return True
            elif lock[pos[0]][pos[1]][0]==self.id:
                return True
            else:
                return False

    def check_view2(self,pos,view):
        if view[pos[0]][pos[1]] != ' ':
           self.collision+=1

    def move2(self,view):
        tmp_d=self.path.pop(0)
        tmp_p=self.tmp_position(tmp_d)  
        self.check_view2(tmp_p,view)
        self.set_view(self.pos,' ',view)
        self.set_view(tmp_p,self.dist,view)    
        self.pos=tmp_p  

if __name__ == "__main__":
    parse=argparse.ArgumentParser()
    parse.add_argument('--population',type=int,default=10)
    parse.add_argument('--generation',type=int,default=150)
    # parse.add_argument('--goods',type=int,default=50)
    # parse.add_argument('--dataname',type=str,default='data.json')
    # parse.add_argument('--size',type=int,default=17)

    args=parse.parse_args()

    p=Simulator('data.json',population=args.population,generation=args.generation)
    # s1=p.s.get_solution()
    # s2=p.s.get_solution()
    #x1=p.fitness(solution)
    #print(x)
    sol,res=p.evolution()
    #print(sol)
    x=p.fitness(sol[0],record='record.db')
    print("The best result found is :",x)
    #x=solution
    #s2=p.s.get_solution()
    #json.dump(s2,open('solution.json','w'))

    #print(p.fitness2(solution))
    #print(p.fitness2(s2))
