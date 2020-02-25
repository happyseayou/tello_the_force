"""

如何调用：

mapcom=Mapcom()
while：#视频帧循环里
    if userc[4]==2 or userc[4]==3:进入map
        mapcom.readflightdata(data)#第一步更新飞行数据data由飞机类给出

        comd=mapcom.com(userc)#需要传入用户控制指令，不然万一出错就放生了
        flightdata=mapcom.send_flightdata()#将所有飞行数据传出用于显示和其他端口调用
        if mapcom.checkalldone():
            ...退出该模式
            userc[4]=0#拨回控制开关
            keyuser.us[4]=0#拨回控制开关
            mapcom.cheakdone=None#这样子可以重新调用

"""
import math
import pandas as pd 
from simple_pid import PID
import time

class Mapcom:

    def __init__(self):
        #文件
        try:
            data=pd.read_csv("./map/map_.csv",usecols=[0,1,2,3])
            ls=data.values.tolist()
            self.listgo=ls
        except:
            print('打不开文件，请检查目录正确')
            self.listgo=None
        #指令相关
        self.index=None
        self.nowop=None
        self.nowdo=None
        self.startcomtime=None 
        self.isopsuccessful=None 
        self.changeoptime=None
        self.istakeoffok=None
        self.checkdone=None#用于存放是否全部指令都执行完
        self.userstatemod=None #监控键盘是否可以开始mapcom
        self.comd=None
        self.flymode=None
        #飞机的遥测数据
        self.battery=None
        self.isfly=None
        self.wifi=None
        self.anlroll=None
        self.anlpitch=None
        self.velz=None
        self.velxy=None
        self.state=None
        #pid
        self.tpid=0
        self.pid_yaw=PID(2,1.8,0,setpoint=0,output_limits=(-50,50))#这套pid目前最佳fps27
        self.pid_thro=PID(1.5,1.4,1,setpoint=0,output_limits=(-50,50))#有点波动
        self.pid_pith=PID(0.2,0.01,0.2,setpoint=0,output_limits=(-20,20))
        self.pid_roll= PID(1,0,0,setpoint=0,output_limits=(-20,20))
        #pid closeon，不修正指向
        self.pidfoward=PID(1.8,1.8,2,setpoint=0,output_limits=(-14,14))
        self.pidroll=PID(1.8,1.8,2,setpoint=0,output_limits=(-14,14))
        #读进来的未经处理坐标值
        self.heightraw=None 
        self.posxraw=None 
        self.posyraw=None 
        self.poszraw=None 
        self.pointyawraw=None 
        #初始的坐标值
        self.height0=None 
        self.posx0=None 
        self.posy0=None 
        self.posz0=None 
        self.pointyaw0=None 
        #变换后的坐标数据
        self.heightnow=None 
        self.posxnow=None 
        self.posynow=None 
        self.posznow=None
        self.pointyawnow=None
        #一些飞行中的误差统计
        self.offdistance=0.0
        self.offheight=0.0
        self.offpoint=0.0
        self.offroll=0.0
        self.offforword=0.0

    def reset(self):#飞行结束后清理到初始，重新进入模式后可以使用,不能self.checkdone,不能pid
        self.listgo=None
        self.index=None
        self.nowop=None
        self.nowdo=None
        self.startcomtime=None 
        self.isopsuccessful=None 
        self.changeoptime=None
        self.istakeoffok=None
        self.userstatemod=None
        self.comd=None
        self.flymode=None
        #self.checkdone=None#用于存放是否全部指令都执行完
        #飞机的遥测数据
        self.battery=None
        self.isfly=None
        self.wifi=None
        self.anlroll=None
        self.anlpitch=None
        self.velz=None
        self.velxy=None
        self.state=None
        self.tpid=0
        #pid
        # self.pid_yaw=PID(0.25,0,0,setpoint=0,output_limits=(-30,30))
        # self.pid_thro=PID(0.3,0.005,0.1,setpoint=0,output_limits=(-30,30))
        # self.pid_pith=PID(0.3,0.01,0.3,setpoint=0,output_limits=(-30,30))
        # self.pid_roll= PID(0.2,0.005,0.2,setpoint=0,output_limits=(-30,30))
        #读进来的未经处理坐标值
        self.heightraw=None 
        self.posxraw=None 
        self.posyraw=None 
        self.poszraw=None 
        self.pointyawraw=None 
        #初始的坐标值
        self.height0=None 
        self.posx0=None 
        self.posy0=None 
        self.posz0=None 
        self.pointyaw0=None 
        #变换后的坐标数据
        self.heightnow=None 
        self.posxnow=None 
        self.posynow=None 
        self.posznow=None
        self.pointyawnow=None
        #一些飞行中的误差统计
        self.offdistance=0.0
        self.offheight=0.0
        self.offpoint=0.0
        self.offroll=0.0
        self.offforword=0.0

    def flashdata(self):
        #变换到起飞点的坐标
        self.heightnow=self.heightraw
        #xt=xcosa+ysina
        #yt=ycosa-xsina
        #a=-pointyaw0
        self.posxnow=(self.posxraw-self.posx0)*math.cos(-math.radians(self.pointyaw0))+(self.posyraw-self.posy0)*math.sin(-math.radians(self.pointyaw0))
        self.posynow=(self.posyraw-self.posy0)*math.cos(-math.radians(self.pointyaw0))-(self.posxraw-self.posx0)*math.sin(-math.radians(self.pointyaw0))
        self.posznow=self.poszraw-self.posz0+self.height0*10
        self.pointyawnow=self.pointyawraw-self.pointyaw0
        
        if self.nowop==2 or self.nowop==3 or self.nowop==8:
            self.offdistance=math.sqrt((self.posxnow-self.nowdo[1])**2+(self.posynow-self.nowdo[2])**2)
            self.offheight=self.posznow-self.nowdo[3]
            #夹角
            anglepoint2y=math.degrees(math.atan2(self.nowdo[1]-self.posxnow,self.nowdo[2]-self.posynow))#目标点与y轴[-180,180]
            self.offpoint=self.pointyawnow-anglepoint2y
            if self.offpoint<=-180:
                self.offpoint=360+self.offpoint            
            elif self.offpoint>180:
                self.offpoint=360-self.offpoint#结果为-180~180
            self.offroll=self.offdistance*math.sin(math.radians(self.offpoint))#选择与off同向pid运输需要注意
            self.offforword=self.offdistance*math.cos(math.radians(self.offpoint))

    def checkop(self):#执行的操作更换器
        self.startcomtime=time.time()
        if self.isfly==1:
            if self.state==6:#判断是否正在悬停
                if self.isopsuccessful==1:
                    self.index+=1#下一条指令
                    if self.index<len(self.listgo):
                        self.nowdo=self.listgo[self.index]
                        self.nowop=self.nowdo[0]
                    self.isopsuccessful=0
                    self.changeoptime=time.time()
                if self.istakeoffok==1:#起飞成功更新数据之后
                    self.flashdata()#更新飞行中数据
        # else:
        #     if self.state==6:#判断是否可以起飞
        #         #起飞倒计时
        #         if time.time()-self.changeoptime>=5:
        #             self.index=0
        #             self.nowdo=self.listgo[self.index]
        #             self.changeoptime=time.time()
        
    def takeoffop(self):
        com=[0,0,0,0,0]
        if self.isfly==1:
            if self.state==6:
                if abs(self.heightraw-self.nowdo[1])<=1.5:
                    com[3]=0
                    if self.velxy<1 and abs(self.velz)<1:#判断是否静止
                        self.isopsuccessful=1
                        #记录初始坐标和初始角度用于后面的坐标变换
                        self.posx0=self.posxraw
                        self.posy0=self.posyraw
                        self.posz0=self.poszraw
                        self.height0=self.heightraw
                        self.pointyaw0=self.pointyawraw
                        self.istakeoffok=1
                        #print('起飞成功')

                else:
                    com[3]=int(self.pid_thro((self.heightraw-self.nowdo[1])*10))
                    #print('修正高度')
        else:
            if self.state==6:    
                com=[0,0,0,0,1]
                self.isopsuccessful=0
            else:
                self.index=None
                self.nowdo=None
                self.nowop=None
               # print('飞机状态不给起飞')
        #print(com)
        return com

    def holdonop(self):
        com=[0,0,0,0,0]
        if self.isfly==1:
            if self.state==6:
                if time.time()-self.changeoptime<=self.nowdo[1]:
                    com=[0,0,0,0,0]
                else:
                    self.isopsuccessful=1
                    com=[0,0,0,0,0]

        return com
        
    def goop(self):
        com=[0,0,0,0,0]
        if self.isfly==1:
            if self.state==6:#是否悬停正常
                if self.offdistance<11:#缓冲区大小未知
                    if self.velxy<1 and abs(self.velz<1):#判断是否静止
                        self.isopsuccessful=1
                        com=[0,0,0,0,0]
                    else:
                        com=[0,0,0,0,0]
                
                else:#pid上
                    #if self.tpid==0:
                    if abs(self.offheight)<12:
                        #if self.tpid==0:
                        if abs(self.offpoint)<5:#先对准指向
                            com[2]=int(self.pid_pith(-self.offdistance))
                            com[1]=int(self.pid_roll(self.offroll))
                            #com[3]=int(self.pid_thro(self.offheight))
                            #com[0]=int(self.pid_yaw(self.offpoint))
                        else:
                            com[0]=int(self.pid_yaw(self.offpoint))
                        # else:
                        #     com[0]=int(self.pid_yaw(self.offpoint))
                    else:
                        com[3]=int(self.pid_thro(self.offheight))
                    # else:
                    #     com[3]=int(self.pid_thro(self.offheight))

            else:
                com=[0,0,0,0,0]
            #print(com)
        return com

    def closeop(self):
        com=[0,0,0,0,0]
        if self.isfly==1:
            if self.state==6:#是否悬停正常
                if self.offdistance<11:#缓冲区大小未知
                    if self.velxy<1 and abs(self.velz<1):#判断是否静止
                        self.isopsuccessful=1
                        com=[0,0,0,0,0]
                    else:
                        com=[0,0,0,0,0]
                
                else:
                    if abs(self.offheight)<12:
                        #不修正指向
                        com[2]=int(self.pidfoward(-self.offforword))          
                        com[1]=int(self.pidroll(self.offroll))           
                    else:
                        com[3]=int(self.pid_thro(self.offheight))
            else:
                com=[0,0,0,0,0]
            #print(com)
        return com

    def backhome(self):
        com=[0,0,0,0,0]
        if self.isfly==1:
            if self.state==6:#是否悬停正常
                if self.offdistance<10:#缓冲区大小未知
                    if self.velxy<1 and abs(self.velz<1):#判断是否静止
                        self.isopsuccessful=1
                        com=[0,0,0,0,0]
                
                else:#pid上
                    if abs(self.offheight)<12:
                        if abs(self.offpoint)<5:#先对准指向
                            com[2]=int(self.pid_pith(-self.offdistance))
                            com[1]=int(self.pid_roll(self.offroll))
                            #com[3]=int(self.pid_thro(self.offheight))
                            #com[0]=int(self.pid_yaw(self.offpoint))
                        else:
                            com[0]=int(self.pid_yaw(self.offpoint))
                    else:
                        com[3]=int(self.pid_thro(self.offheight))

            else:
                com=[0,0,0,0,0]
        return com

    def land(self):
        com=[0,0,0,0,0]
        if self.isfly==1:
            if self.state==6:#是否悬停正常
                if self.velxy<1 and abs(self.velz<1):#判断是否静止
                    if abs(self.pointyawnow)<1:
                        self.isopsuccessful=1
                        com[4]=4
                        self.checkdone=1
                    else:
                        com[0]=int(self.pid_yaw(self.pointyawnow))
            else:
                com=[0,0,0,0,0]
        return com

    def stopmap(self):
        self.checkdone=1
        

    def checkfile(self):
        if self.listgo is None:
            try:
                data=data=pd.read_csv("./map/map_.csv",usecols=[0,1,2,3])
                ls=data.values.tolist()
                self.listgo=ls
                ok=1
            except:
                ok=0
                print('打不开文件，请检查目录正确')
                #self.reset()
                self.checkdone=1#在comd里找不到文件的话直接弹出执行完成退出模式
        else:
            ok=1
        return ok
    
    def userstate(self,userc):#判断用户控制状态，等待，执行中，暂停，强制降落并直接退出
        if userc[5]==1:       #如果已经起飞完成了，进入map后按起飞也可以开始
            self.index=0
            self.nowdo=self.listgo[self.index]
            self.nowop=self.nowdo[0]
            self.flymode=self.nowop
            self.userstatemod=2#开始
        elif userc[5]==4:#直接退出到普通并悬停
            self.nowdo=[5,0,0,0]
            self.nowop=self.nowdo[0]
            self.flymode=5
            self.userstatemod=2
        elif userc[4]==3:
            self.userstatemod=3#暂停模式b
            #self.nowdo=[7,0,0,0]
            self.flymode=7
        else:
            if self.isfly==1 and (self.index is not None):
                self.userstatemod=2
            else:
                self.userstatemod=0#等待
                # self.nowdo=[6,0,0,0]
                self.flymode=6
    #定义飞行指令发送,在main循环中调用
    def com(self,userc):
        ok=self.checkfile()
        self.userstate(userc)
        com=[0,0,0,0,0]#每轮循环归零
        # if self.tpid==1:
        #     self.pidtuning(pid)
        if self.userstatemod==2:
            if ok==1:#有文件才可以，没有文件不给玩
                self.checkop()
                if self.nowop==0:
                    com=self.takeoffop()
                    if self.nowop is not None:
                        self.flymode=self.nowop
                    else:
                        self.flymode=6
                elif self.nowop==1:
                    com=self.holdonop()
                    self.flymode=self.nowop
                elif self.nowop==2:
                    com=self.goop()
                    self.flymode=self.nowop
                elif self.nowop==8:
                    com=self.closeop()
                    self.flymode=self.nowop
                elif self.nowop==3:
                    com=self.backhome()
                    self.flymode=self.nowop
                elif self.nowop==4:
                    com=self.land()
                    self.flymode=self.nowop
                elif self.nowop==5:
                    self.stopmap()
                    self.flymode=self.nowop
                else:
                    pass
        
        elif self.userstatemod==0 or self.userstatemod==3:
            if self.isfly==1:
                if self.state==6:#判断是否正在悬停
                    if self.istakeoffok==1:#起飞成功更新数据之后
                        self.flashdata()#更新飞行中数据
        #用户超越控制
        if userc[0]!=0 or userc[1]!=0 or userc[2]!=0 or userc[3]!=0:
            com[0]=userc[3]
            com[1]=userc[2]
            com[2]=userc[1]
            com[3]=userc[0]
        #print(self.nowop)
        self.comd=com        
        return com

    # def pidtuning(self,value):
    #     #value=[[p,i,d,down,up]  yaw
    #     #       [p,i,d,down,up]  thro
    #     #       [p,i,d,down,up]  pith
    #     #       [p,i,d,down,up]] roll
    #     self.pid_yaw=PID(value[0][0],value[0][1],value[0][2],setpoint=0,output_limits=(value[0][3],value[0][4]))
    #     self.pid_thro=PID(value[1][0],value[1][1],value[1][2],setpoint=0,output_limits=(value[1][3],value[1][4]))
    #     self.pid_pith=PID(value[2][0],value[2][1],value[2][2],setpoint=0,output_limits=(value[2][3],value[2][4]))
    #     self.pid_roll= PID(value[3][0],value[3][1],value[3][2],setpoint=0,output_limits=(value[3][3],value[3][4]))

    def readflightdata(self,data):#定义从无人机获取遥测数据
        self.battery=data[0]
        self.isfly=data[1]
        self.heightraw=data[3]
        self.wifi=data[4]
        self.anlroll=data[5]
        self.anlpitch=data[6]
        self.velz=data[7]
        self.velxy=data[8]
        #xy要互换，#向上z正方向，向前y正方向，向右x正方向
        self.posxraw=data[10]
        self.posyraw=data[9]
        self.poszraw=-data[11]#更改为向上为正方向
        self.pointyawraw=data[14]
        self.state=data[15]#state的判断还要加一层保险
        if self.isfly:
            if abs(data[9])<=2 and abs(data[10])<=2 and abs(data[11])<=2:
                self.state=1#当三个值同时为这个范围时说明飘了
        #    if self.isfly==0:
        #         if abs(self.anlpitch)>16 or abs(self.anlroll)>16:#倾角过大，sin1=1/(1+tan1^2+tan2^2)
        #             self.state=1]

    def send_flightdata(self):#定义发送数据出来给ui等其他部件
        flightdata=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        #常规数据
        flightdata[0]=self.isfly
        flightdata[1]=self.battery
        #现在的指令
        flightdata[2]=self.flymode+20#[op,v1,v2,v3]加20区分其他模块
        flightdata[3]=self.index
        #舵量监控
        flightdata[4]=self.comd[3]
        flightdata[5]=self.comd[2]
        flightdata[6]=self.comd[1]
        flightdata[7]=self.comd[0]
        #地图跟踪数据
        if self.offdistance:
            flightdata[8]=self.offdistance
        if self.offheight:
            flightdata[9]=self.offheight
        if self.offpoint:
            flightdata[10]=self.offpoint
        flightdata[11]=self.heightraw
        flightdata[12]=self.wifi
        if self.offroll:
            flightdata[13]=self.offroll
        if self.offforword:
            flightdata[22]=self.offforword
        #姿态位置
        flightdata[14]=self.userstatemod
        flightdata[15]=self.anlroll
        flightdata[16]=self.anlpitch
        flightdata[17]=self.velxy
        flightdata[18]=self.velz
        if self.posxnow:
            flightdata[19]=self.posxnow
        if self.posynow:
            flightdata[20]=self.posynow
        if self.posznow:
            flightdata[21]=self.posznow
        #flightdata[22]=0
        flightdata[23]=self.pointyawraw
        if self.pointyawnow:
            flightdata[24]=self.pointyawnow
        flightdata[25]=self.state
        return flightdata

    def checkalldone(self):#检查是否完成降落，是则退出模式
        if self.checkdone==1:
            ok=1
            self.reset()#初始化并且自动退出map模式
        else:
            ok=0
        return ok
    

