#根据op的身体节点坐标，根据决策树，返回命令
import math
from simple_pid import PID
import time 

def distance(a,b):
    return int(sqrt((b[0]-a[0])**2+(b[1]-a[1])**2))

def angle(A,B,C):
    if A[0] is None or B[0] is None or C[0] is None:
        return None
    dg=degrees(atan2(C[1]-B[1],C[0]-B[0]) - atan2(A[1]-B[1],A[0]-B[0]))%360
    if dg>=180 and dg<360:
        dg=360-dg  #返回角度0-90
    return dg

class Com:
    def __init__(self):
        #飞行数据与状态
        self.isfly=None
        self.flymode=None
        self.isfly=None
        self.batry=None
        self.throwflytimer=None
        self.state=[0,0,0,0,0,0,0,0,0,0,0]
        self.comd=None 
        #是否飞行 电池 飞行模式  动作指令  油门 俯仰 副翼 偏航 备用
        self.pose=None    #用于判读手势操作
        self.posespeed=30
        #定义亮度
        self.brightness=None 
        #定义屏幕中的定点
        self.point=[320,240]#固定点
        #初始化pid控制
        self.pid_yaw=None
        self.pid_pith=None
        self.pid_roll=None
        self.pid_thro=None

        #定义各个点,每次循环都会更新
        self.nose=None
        self.letfhand=None
        self.righthand=None
        self.letfear=None
        self.rightear=None
        self.letfshd=None
        self.rightshd=None
        self.midp=None
        self.neck=None      
        #作为跟踪锁定点
        self.target=None 
        
        #定义距离，每次循环更新距离，lock距离更换模式会改变
        self.distance_shd=None
        self.distance_midneck=None
        self.lock_distance_mn= None#两种锁定距离方法   #切换模式清零
        self.lock_distance_sd= None

        #定义模式判断的距离角度等
        self.angleright=None
        self.anglerletf=None
        self.lethand_rigear=None
        self.righand_letear=None
        self.rihan_neck=None
        self.rihan_nose=None
        self.lehan_neck=None 
        self.lehan_nose=None 

        #定义模式时间用于切换判断
        self.flymodechange=time.time() 
        
        

    def reset(self):#每次降落后调用
        self.pid_yaw=None
        self.pid_pith=None
        self.pid_roll=None
        self.pid_thro=None

        self.distance_shd=None
        self.distance_midneck=None
        self.lock_distance_mn= None#两种锁定距离方法   #切换模式清零
        self.lock_distance_sd= None
        
        self.nose=None
        self.letfhand=None
        self.righthand=None
        self.letfear=None
        self.rightear=None
        self.letfshd=None
        self.rightshd=None
        self.midp=None
        self.neck=None

        self.isfly=None
        self.flymode=None
        self.pose=None

        self.flymodechange=time.time() 

    def get_data(self,kp):#很多if else是为了后面的判断以及保证每一帧如果失去某个点则这个点一定为none，后面判断才不会出错
         #if前面得i有预判断
        #每个点的坐标提取出来
        if kp[0][0]:
            self.nose=[kp[0][0],kp[0][1]]
        else:
            self.nose=None
        if kp[7][0]:      
            self.letfhand=[kp[7][0],kp[7][1]]
        else:
            self.letfhand=None
        if kp[6][0]:
            self.lerfhandmid=[kp[6][0],kp[6][1]]
        else:
            self.lerfhandmid=None
        if kp[4][0]:
            self.righthand=[kp[4][0],kp[4][1]]
        else:
            self.righthand=None
        if kp[3][0]:
            self.righthandmid=[kp[3][0],kp[3][1]]
        else:
            self.righthandmid=None
        if kp[18][0]:
            self.letfear=[kp[18][0],kp[18][1]]
        else:
            self.letfear=None
        if kp[17][0]:
            self.rightear=[kp[17][0],kp[17][1]]
        else:
            self.rightear=None
        if kp[5][0]:
            self.letfshd=[kp[5][0],kp[5][1]]
        else:
            self.letfshd=None
        if kp[2][0]:  
            self.rightshd=[kp[2][0],kp[2][1]]
        else:
            elf.rightshd=None
        if kp[8][0]:
            self.midp=[kp[8][0],kp[8][1]]
        else:
            self.midp=None
        if kp[1][0]:
            self.neck=[kp[1][0],kp[1][1]]
        else:
            self.neck=None
        #从listid[10]获取亮度
        if kp[10][0] and kp[10][1]:
            self.brightness=kp[10][0]
        else:
            self.brightness=None 

        #计算肩宽和中心点和脖子的长度用于模拟远近
        if self.letfshd and self.rightshd:
            self.distance_shd=distance(self.letfshd,self.rightshd)
        else:
            self.distance_shd=None
        if self.midp and self.neck:
            self.distance_midneck=distance(self.midp,self.neck)
        else:
            self.distance_midneck=None
        
        #定义手臂角度，手的距离，
        if self.righthand and self.righthandmid and self.rightshd:
            self.angleright=angle(self.righthand,self.righthandmid,self.rightshd)
        else:
            self.angleright=None
        if self.letfhand and self.lerfhandmid and self.letfshd:
            self.anglerletf=angle(self.letfshd,self.lerfhandmid,self.letfshd)
        else:
            self.anglerletf=None
        
        if self.letfhand and self.rightear:
            self.lethand_rigear=distance(self.letfhand,self.rightear)
        else:
            self.lethand_rigear=None
        if self.righthand and self.letfear:
            self.righand_letear=distance(self.righthand,self.letfear)
        else:
            self.righand_letear=None
        if self.righthand and self.neck:
            self.rihan_neck=distance(self.righthand,self.neck)
        else:
            self.rihan_neck=None 
        if self.righthand and self.nose:
            self.rihan_nose=distance(self.righthand,self.nose)
        else:
            self.rihan_nose=None
        if self.letfhand and self.neck:
            self.lehan_neck=distance(self.letfhand,self.neck)
        else:
            self.lehan_neck=None
        if self.letfhand and self.nose:
            self.lehan_nose=distance(self.letfhand,self.nose)
        else:
            self.lehan_nose=None


        
        
    def check_mode(self,kp):#完成两件事，首先根据姿势确定飞行模式，然后确定self.pose
        self.get_data(kp)#太长了丢到这个方法里
        #模式判断逻辑
            #pose    0无操作     
            #        1向前
            #        2向后
            #        3向左飘
            #        4向右
        #flymode 0普通跟踪，只修正偏航
        #        1跟随模式，修正偏航和锁定距离
        #        2平行跟随，修正roll和锁定距离
        #        3丢失目标，保持高度，同时旋转寻找目标，如果超过15秒则降落
        #        4降落，所有参数清零
        #        5靠近降落在手掌，所有参数清零
        #        6抛飞，
        #        7起飞，
        #        8紧急停机，
        if self.nose and self.letfear and self.rightear and self.neck and self.letfshd and self.rightshd and self.letfhand and self.lerfhandmid and self.righthand and self.righthandmid:
            #第0层判断是否满足判断条件，如果没有同时存在这些点则不做任何指令切换或动作
            #判断pose左右手操作互斥
            if self.isfly:
                if (self.righthand[1]<self.rightshd[1]) and (self.letfhand[1]>self.letfshd[1]) and (self.righthand[0]<self.neck[0]): #右手举起了决定左右飘
                    if self.angleright<=90:
                        self.pose=4
                    else:
                        self.pose=3
                elif (self.letfhand[1]<self.letfshd[1]) and (self.righthand[1]>self.rightshd[1])and (self.lerfhand[0]>self.neck[0]):#左手举起了决定前后
                    if self.anglerletf<=90:
                        self.pose=1
                    else:
                        self.pose=2
                else:
                    self.pose=0
            #判断fly_mode
            #首先是单手
               #手掌降落模式5
            if (self.righthand[1]<self.rightshd[1]) and (self.letfhand[1]>self.letfshd[1]):
                if self.righand_letear<30:#这个值还不知道，先这样设置
                    if self.flymode!=5:#将进入模式
                        if time.time()-self.flymodechange=time.time()<2:#判断时间是否小于一秒，否则不执行
                            self.flymodechange=time.time()
                            self.flymode=5
                    else:#退出模式
                        if time.time()-self.flymodechange=time.time()<2:
                            self.flymodechange=time.time()
                            self.flymode=0
              #降落4
            elif (self.righthand[1]>self.rightshd[1]) and (self.letfhand[1]<self.letfshd[1]):
                if self.lethand_rigear<30:#这个值还不知道，先这样设置
                    if self.flymode!=4:#将进入模式
                        if time.time()-self.flymodechange=time.time()<2:#判断时间是否小于一秒，否则不执行
                            self.flymodechange=time.time()
                            self.flymode=4
                    else:#退出模式
                        if time.time()-self.flymodechange=time.time()<2:
                            self.flymodechange=time.time()
                            self.flymode=0
            #双手的操作
                #跟随模式1
            elif :
                #平行跟随2
            elif :
            else:
                self.flymode=0

        

        else:
            self.pose=0
            self.flymode=0
        
        
            
        #判断是否存在target
        if self.neck:
            self.target=self.neck
        elif self.nose:
            self.target=self.nose
        elif self.midp:
            self.target=self.midp
        elif self.rightshd:
            self.target=self.rightshd
        elif self.letfshd:
            self.target=self.letfshd
        else:
            self.flymode=3

        #m没有起飞时则判断起飞方式
        if self.isfly is None:
            if :#抛飞#如果没有抛起来怎么办

            if :#起飞#判断是否起飞成功？？？
        
        if：#紧急停机通过键盘键位，最后一个修改，等级最高
           


            

    def get_comd(self,kp):
        comd=[0,0,0,0,0]#每轮循环都回中
        self.check_mode(kp)
        xoff=self.neck[0]-self.point[0]#计算修正量
        yoff=self.neck[1]-self.point[1]
        
        #flymode 0普通跟踪，只修正偏航
        #        1跟随模式，修正偏航和锁定距离
        #        2平行跟随，修正roll和锁定距离
        #        3丢失目标，保持高度，同时旋转寻找目标，如果超过15秒则降落
        #        4降落，所有参数清零
        #        5靠近降落在手掌，所有参数清零
        #        6抛飞，
        #        7起飞，
        #        8紧急停机，9拍照，10起飞失败，11起飞成功，12退出平行跟随，
        #        13退出跟随模式，14接近中，15，低电量警报
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
            if self.isfly:
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

            if self.lock_distance_mn and self.lock_distance_sd is None:#判断是否存在这两个值，没有则重建
                if self.distance_midneck:#优先使用中轴线
                    self.lock_distance_mn=self.distance_midneck
                elif: self.distance_shd:
                    self.lock_distance_sd=self.distance_shd
                
            comd[0]=int(self.pid_yaw(xoff))
            comd[3]=int(self.pid_thro(yoff))

            if self.distance_midneck and self.lock_distance_mn:#判断是否存在这两个值，存在才能给命令，不存在则使用初始值
                comd[2]=int(self.pid_pith(self.lock_distance_mn-self.distance_midneck))
            elif self.distance_shd and self.lock_distance_sd:
                comd[2]=int(self.pid_pith(self.lock_distance_sd-self.distance_shd))

            if self.isfly:
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
            self.pid_yaw=PID(0.25,0,0,setpoint=0,output_limits=(-100,100))
            self.pid_thro=PID(0.3,0.005,0.1,setpoint=0,output_limits=(-50,50))
            self.pid_pith=PID(0.4,0.04,0.4,setpoint=0,output_limits=(-50,50))
            self.pid_roll= PID(0.2,0.005,0.2,setpoint=0,output_limits=(-30,30))

            if self.lock_distance_mn and self.lock_distance_sd is None:#只赋值一次
                if self.distance_midneck:
                    self.lock_distance_mn=self.distance_midneck
                elif: self.distance_shd:
                    self.lock_distance_sd=self.distance_shd
                
            #comd[0]=int(self.pid_yaw(xoff))
            comd[3]=int(self.pid_thro(yoff))
            comd[1]=int(self.pid_roll(xoff))

            if self.distance_midneck and self.lock_distance_mn:
                comd[2]=int(self.pid_pith(self.lock_distance_mn-self.distance_midneck))
            elif self.distance_shd and self.lock_distance_sd:
                comd[2]=int(self.pid_pith(self.lock_distance_sd-self.distance_shd))

            if self.isfly:
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
               
        
        elif self.flymode==6:#        6抛飞
            comd[4]=2
           # self.is_fly=1   #判断是否起飞成功？？？
            self.flymode=0

        elif self.flymode==7:#        7起飞，
            comd[4]=1
            #self.is_fly=1
            self.flymode=0
        
        elif self.flymode==8:#        8紧急停机，
            comd[3]=-100        #暂时没有找到通信协议紧急停机的代码
            self.reset()
        self.comd = comd   
        return comd
        #comd[0] comd[1] comd[2]  comd[3]  comd[4]
        #旋转     左右    前后      上下     特殊命令

    def get_state(self):#发送状态给ui,所有飞行日志
        #self.state=[0,0,0,0,0,0,0,0,0,0]
        #是否飞行 电池 飞行模式  动作指令  油门 俯仰 副翼 偏航 锁定距离 实时距离
        self.state[0]=self.isfly
        self.state[1]=self.batry
        self.state[2]=self.flymode
        self.state[3]=self.pose
        self.state[4]=self.comd[3]
        self.state[5]=self.comd[2]
        self.state[6]=self.comd[1]
        self.state[7]=self.comd[0]
        if self.lock_distance_mn and self.distance_midneck:
            self.state[8]=self.lock_distance_mn
            self.state[9]=self.distance_midneck
        elif self.lock_distance_sd and self.distance_shd:
            self.state[8]=self.lock_distance_sd
            self.state[9]=self.distance_shd
        else:
            self.state[8]='***'
            self.state[9]='***'
        state=self.state
        return state

    def read_tello_data(self,data):
        self.isfly=data[1]
        self.batry=data[0]
        self.throwflytimer=data[2]

