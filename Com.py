#根据op的身体节点坐标，根据决策树，返回命令
import math
from simple_pid import PID

def distance(a,b):
    return int(sqrt((b[0]-a[0])**2+(b[1]-a[1])**2))


class Com:
    def __init__(self):
        self.flymode=None
        self.pose=None    #用于判读手势操作
        self.posespeed=30
        #定义屏幕中的定点
        self.point=[320,240]
        #初始化pid控制
        self.pid_yaw=None
        self.pid_pith=None
        self.pid_roll=None
        self.pid_thro=None

        #定义各个点
        self.nose=None
        self.letfhand=None
        self.righthand=None
        self.letfear=None
        self.rightear=None
        self.letfshd=None
        self.rightshd=None
        self.midp=None
        self.neck=None      #作为跟踪锁定点
        self.distance_shd=None
        self.distance_midneck=None
        self.lock_distance_mn= None#两种锁定距离方法
        self.lock_distance_sd= None
    def reset(self):

    def check_mode(self,kp):
        self.nose=[kp[0][0],kp[0][1]]       #每个点的坐标提取出来
        self.letfhand=[kp[7][0],kp[7][1]]
        self.righthand=[kp[4][0],kp[4][1]]
        self.letfear=[kp[18][0],kp[18][1]]
        self.rightear=[kp[17][0],kp[17][1]]
        self.letfshd=[kp[5][0],kp[5][1]]
        self.rightshd=[kp[2][0],kp[2][1]]
        self.midp=[kp[8][0],kp[8][1]]
        self.neck=[kp[1][0],kp[1][1]]
        #计算肩宽和中心点和脖子的长度用于模拟远近
        self.distance_shd=distance(self.letfshd,self.rightshd)
        self.distance_midneck=distance(self.midp,self.neck)

        if :#
        
        elif :

        elif :


        

    def get_comd(self,kp):
        comd=[0,0,0,0,0]
        self.flymode=self.check_mode(kp)
        xoff=self.neck[0]-self.point[0]
        yoff=self.neck[1]-self.point[1]
        
        #flymode 0普通跟踪，只修正偏航
        #        1跟随模式，修正偏航和锁定距离
        #        2平行跟随，修正roll和锁定距离
        #        3丢失目标，保持高度，同时旋转寻找目标，如果超过15秒则降落
        #        4降落，所有参数清零
        #        5靠近降落在手掌，所有参数清零
        #        6抛飞，
        #另外，左右手控制距离和偏转在除丢失模式下任何模式下都可用
        #pose    0无操作
        #        1向前
        #        2向后
        #        3向左飘
        #        4向右
        if self.flymode==0:#flymode 0普通跟踪，只修正偏航
            self.pid_yaw=PID(0.25,0,0,setpoint=0,output_limits=(-100,100))
            self.pid_thro=PID(0.3,0.005,0.1,setpoint=0,output_limits=(-50,50))
            comd[0]=int(self.pid_yaw(xoff))
            comd[3]=int(self.pid_thro(yoff))
            if self.pose==0:#这层判断用于控制前后左右
                pass
            elif self.pose==1:
                comd[2]=self.posespeed
            elif self.pose==2:
                comd[2]=-self.posespeed
            elif self.pose==3:
                comd[1]=self.posespeed
            elif self.pose==4:
                comd[1]=self.posespeed

        elif self.flymode==1:#        1跟随模式，修正偏航和锁定距离
            self.pid_yaw=PID(0.25,0,0,setpoint=0,output_limits=(-100,100))
            self.pid_thro=PID(0.3,0.005,0.1,setpoint=0,output_limits=(-50,50))
            self.pid_pith=PID(0.4,0.04,0.4,setpoint=0,output_limits=(-50,50))

            if self.lock_distance_mn and self.lock_distance_sd is None:#复制一次
                if self.distance_midneck:
                    self.lock_distance_mn=self.distance_midneck
                elif: self.distance_shd:
                    self.lock_distance_sd=self.distance_shd
                
            comd[0]=int(self.pid_yaw(xoff))
            comd[3]=int(self.pid_thro(yoff))

            if self.distance_midneck and self.lock_distance_mn is None:
                comd[2]=int(self.pid_pith(self.lock_distance_mn-self.distance_midneck))
            elif self.distance_shd and self.lock_distance_sd:
                comd[2]=int(self.pid_pith(self.lock_distance_sd-self.distance_shd))

            if self.pose==0:#这层判断用于控制前后左右
                pass
            elif self.pose==1:
                if self.lock_distance_mn and self.lock_distance_sd:
                    self.lock_distance_mn--
                    self.lock_distance_sd--
            elif self.pose==2:
                if self.lock_distance_mn and self.lock_distance_sd:
                    self.lock_distance_mn++
                    self.lock_distance_sd--
            elif self.pose==3:
                comd[1]=self.posespeed
            elif self.pose==4:
                comd[1]=-self.posespeed
        
        elif self.flymode==2:#        2平行跟随，修正roll和锁定距离
            #self.pid_yaw=PID(0.25,0,0,setpoint=0,output_limits=(-100,100))
            self.pid_thro=PID(0.3,0.005,0.1,setpoint=0,output_limits=(-50,50))
            self.pid_pith=PID(0.4,0.04,0.4,setpoint=0,output_limits=(-50,50))
            self.pid_roll= PID(0.2,0.005,0.2,setpoint=0,output_limits=(-30,30))

            if self.lock_distance_mn and self.lock_distance_sd is None:#复制一次
                if self.distance_midneck:
                    self.lock_distance_mn=self.distance_midneck
                elif: self.distance_shd:
                    self.lock_distance_sd=self.distance_shd
                
            #comd[0]=int(self.pid_yaw(xoff))
            comd[3]=int(self.pid_thro(yoff))
            comd[1]=int(self.pid_roll(xoff))

            if self.distance_midneck and self.lock_distance_mn is None:
                comd[2]=int(self.pid_pith(self.lock_distance_mn-self.distance_midneck))
            elif self.distance_shd and self.lock_distance_sd:
                comd[2]=int(self.pid_pith(self.lock_distance_sd-self.distance_shd))

            if self.pose==0:#这层判断用于控制前后左右
                pass
            elif self.pose==1:
                if self.lock_distance_mn and self.lock_distance_sd:
                    self.lock_distance_mn--
                    self.lock_distance_sd--
            elif self.pose==2:
                if self.lock_distance_mn and self.lock_distance_sd:
                    self.lock_distance_mn++
                    self.lock_distance_sd--
            elif self.pose==3:
                self.pid_yaw=PID(0.25,0,0,setpoint=0,output_limits=(-100,100))
                comd[0]=int(self.pid_yaw(xoff))
                comd[1]=self.posespeed
            elif self.pose==4:
                self.pid_yaw=PID(0.25,0,0,setpoint=0,output_limits=(-100,100))
                comd[0]=int(self.pid_yaw(xoff))
                comd[1]=-self.posespeed
        elif self.flymode==3: #        3丢失目标，保持高度，同时旋转寻找目标，如果超过15秒则降落
            comd[0]=self.posespeed
        elif self.flymode==4: #        4降落，所有参数清零
            comd[4]=4
            self.reset()
        elif self.flymode==5: #        5靠近降落在手掌，所有参数清零
            self.pid_yaw=PID(0.25,0,0,setpoint=0,output_limits=(-100,100))
            self.pid_thro=PID(0.3,0.005,0.1,setpoint=0,output_limits=(-50,50))
            self.pid_pith=PID(0.4,0.04,0.4,setpoint=0,output_limits=(-50,50))
            self.lock_distance_sd=246     #最近肩宽   
            comd[0]=int(self.pid_yaw(xoff))
            comd[3]=int(self.pid_thro(yoff))
            if self.distance_shd:
                comd[2]=int(self.pid_pith(self.lock_distance_sd-self.distance_shd))
            if int(self.distance_shd-self.lock_distance_sd)<10:
                comd[4]=3
                self.reset()


        return comd
        #comd[0] comd[1] comd[2]  comd[3]  comd[4]
         #旋转     左右    前后      上下     特殊命令

