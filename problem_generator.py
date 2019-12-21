import numpy as np 
import json,sys,os,argparse,random,copy

class generator:
    def __init__(self,port,site,goods,size,dataname):
        self.port=port
        self.site=site
        self.size=size
        self.goods=goods
        self.dataname = dataname
        self.get_ports()
        self.get_sites()
        self.data={
            'port':self.port,
            'site':self.site,
            'size':self.size,
            'port_position':self.ports_position,
            'site_position':self.sites_position,
            'goods':self.goods,
            'goods_data':[]
        }

    def generate(self):
        self.goods_data=[[random.choice(range(1,self.site+1)) for _ in range(self.goods)] for _ in range(self.port)]
        self.data['goods_data']=self.goods_data

    def save_data(self):
        if self.data['goods_data']==[]:
            self.generate()
        json.dump(self.data,open(self.dataname,"w"))
        print("Data is saved in %s ."%self.dataname)

    def load_data(self,file_name):
        data=json.load(open(file_name))
        for key,value in data.items():
            print(key,value)
        
    def get_ports(self):
        inteval=(self.size-self.port)//(self.port-1)
        self.ports_position=[[0,0]]
        x=0
        for i in range(1,self.port-1):
            x+=inteval+1
            self.ports_position.append([x,0])
        self.ports_position.append([self.size-1,0])
        print("Ports position generated.")

    def get_sites(self):
        self.sites_position=copy.deepcopy(self.ports_position)
        for i in range(len(self.sites_position)):
            tmp=self.sites_position[i]
            if i%2==0:
                tmp[1]+=self.size-1
            else:
                tmp[1]+=self.size*2//3
            self.sites_position[i]=tmp
        print("Sites position generated. ")




if __name__ == "__main__":
    parse=argparse.ArgumentParser()
    parse.add_argument('--port',type=int,default=5)
    parse.add_argument('--site',type=int,default=5)
    parse.add_argument('--goods',type=int,default=50)
    parse.add_argument('--dataname',type=str,default='data.json')
    parse.add_argument('--size',type=int,default=17)

    args=parse.parse_args()

    g=generator(args.port,args.site,args.goods,args.size,args.dataname)
    g.save_data()
    g.load_data(args.dataname)

