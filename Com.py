#根据op的身体节点坐标，根据决策树，返回命令
from math import atan2, degrees, sqrt,pi
from simple_pid import PID
import time 

def distance(a,b):
    if a[0] is None or b[0] is None:
        return None
    return int(sqrt((b[0]-a[0])**2+(b[1]-a[1])**2))

def angle(A,B,C):
    if A[0] is None or B[0] is None or C[0] is None:
        return None
    dg=degrees(atan2(C[1]-B[1],C[0]-B[0]) - atan2(A[1]-B[1],A[0]-B[0]))%360
    if dg>=180 and dg<360:
        dg=360-dg
    return dg


class Com:
    def __init__(self):
        #飞行数据与状态
        self.isfly=None
        self.flymode=None
        self.preflymode=None
        self.isfly=None
        self.batry=None
        self.throwflytimer=None
        self.height=None
        self.wifi=None
        self.state=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]#长度保持和reset一致
        self.comd=None 
        #遥测姿态数据等
        self.anglerroll=0.0
        self.anglerpitch=0.0
        self.velz=0.0
        self.velxy=0.0
        self.posx=0.0
        self.posy=0.0
        self.posz=0.0
        self.pitch=0.0#四元数解算
        self.roll=0.0
        self.yew=0.0
        self.visualstate=None
        #是否飞行 电池 飞行模式  动作指令  油门 俯仰 副翼 偏航 备用
        self.pose=None    #用于判读手势操作
        self.posespeed=30
        #定义按压摄像头
        self.press=None 
        #定义屏幕中的定点
        self.point=[320,240]#固定点
        #初始化pid控制
        self.pid_yaw=None
        self.pid_pith=None
        self.pid_roll=None
        self.pid_thro=None
        #flag
        self.palmflag=None
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
        self.hand_hand=None
        self.lehan_neck=None 
        

        #定义模式时间用于切换判断
        self.flymodechange=time.time() 
        
        

    def reset(self):#每次降落后调用
        #飞行数据与状态
        self.isfly=None
        self.flymode=0
        self.preflymode=0
        self.isfly=None
        self.batry=None
        self.throwflytimer=None
        self.height=None
        self.wifi=None
        self.state=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        self.comd=None 
        #是否飞行 电池 飞行模式  动作指令  油门 俯仰 副翼 偏航 备用
        self.pose=None    #用于判读手势操作
        self.posespeed=30
        #定义按压摄像头
        self.press=None 
        #定义屏幕中的定点
        self.point=[320,240]#固定点
        #初始化pid控制
        self.pid_yaw=None
        self.pid_pith=None
        self.pid_roll=None
        self.pid_thro=None

        self.palmflag=None
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
        self.hand_hand=None
        self.lehan_neck=None 
        

        #定义模式时间用于切换判断
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
            self.rightshd=None
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
            self.press=kp[10][0]
        else:
            self.press=None 

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
            self.anglerletf=angle(self.letfhand,self.lerfhandmid,self.letfshd)
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
        if self.letfhand and self.neck:
            self.lehan_neck=distance(self.letfhand,self.neck)
        else:
            self.lehan_neck=None
        if self.righthand and self.letfhand:
            self.hand_hand=distance(self.righthand,self.letfhand)
        else:
            self.hand_hand=None
        


        
        
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
        if self.preflymode is None:#看看是不是第一次捕捉目标
            self.preflymode=0
            
        self.pose=0#先归零
        if self.letfshd and self.neck and self.rightshd and self.letfhand and self.lerfhandmid and self.righthand and self.righthandmid:
            #第0层判断是否满足判断条件，如果没有同时存在这些点则不做任何指令切换或动作
            #判断pose左右手操作互斥
            #if self.isfly:感觉不需要了
            if (self.righthand[1]<self.rightshd[1]) and (self.letfhand[1]>self.letfshd[1]) and (self.righthand[0]<self.neck[0]): #右手举起了决定左右飘
                if self.angleright<=90:
                    self.pose=4
                elif self.angleright>90:
                    self.pose=3
            elif (self.letfhand[1]<self.letfshd[1]) and (self.righthand[1]>self.rightshd[1])and (self.letfhand[0]>self.neck[0]):#左手举起了决定前后
                if self.anglerletf<=90:
                    self.pose=1
                elif self.anglerletf>90:
                    self.pose=2
            else:
                self.pose=0
        else:
            self.pose=0

        if self.nose and self.letfear and self.rightear and self.neck and self.letfshd and self.rightshd and self.letfhand and self.lerfhandmid and self.righthand and self.righthandmid:
            #第0层判断是否满足判断条件，如果没有同时存在这些点则不做任何指令切换或动作
            #判断fly_mode
            #首先是单手
               #手掌降落模式5
            if (self.righthand[1]<self.rightshd[1]) and (self.letfhand[1]>self.letfshd[1]) and (self.righthand[0]>self.nose[0]):#还要判断手过鼻子
                if self.righand_letear<50:#这个值还不知道，先这样设置
                    if self.flymode!=5:#将进入模式
                        if time.time()-self.flymodechange>2:#判断时间是大于2秒，否则不执行
                            self.flymodechange=time.time()
                            self.flymode=5
                            self.preflymode=self.flymode
                    else:#退出模式
                        if time.time()-self.flymodechange>2:
                            self.flymodechange=time.time()
                            self.flymode=0
                            self.preflymode=self.flymode
              #降落4
            elif (self.righthand[1]>self.rightshd[1]) and (self.letfhand[1]<self.letfshd[1]) and (self.letfhand[0]<self.nose[0]):#还要判断手过鼻子
                if self.lethand_rigear<50:#这个值还不知道，先这样设置
                    if self.flymode!=4:#将进入模式
                        if time.time()-self.flymodechange>2:#判断时间是否大于2秒，否则不执行
                            self.flymodechange=time.time()
                            self.flymode=4
                            self.preflymode=self.flymode
                    else:#退出模式
                        if time.time()-self.flymodechange>2:
                            self.flymodechange=time.time()
                            self.flymode=0
                            self.preflymode=self.flymode
            #双手的操作
                #跟随模式1
            elif (self.righthand[1]<self.nose[1]) and (self.letfhand[1]<self.nose[1]) and (self.hand_hand<65):#手合并举高高数字待测试
                if self.flymode!=1:
                    if time.time()-self.flymodechange>2:
                        self.flymodechange=time.time()
                        if self.distance_midneck and self.distance_shd:
                            self.lock_distance_mn=self.distance_midneck
                            self.lock_distance_sd=self.distance_shd
                            self.flymode=1
                            self.preflymode=self.flymode
                        else:
                            self.flymode=self.preflymode#进入模式失败

                else:
                    if time.time()-self.flymodechange>2:
                        self.flymodechange=time.time()
                        self.lock_distance_mn=None
                        self.lock_distance_sd=None
                        self.flymode=0
                        self.preflymode=self.flymode
                #平行跟随2
            elif(self.hand_hand<65) and (self.rihan_neck<65) and (self.lehan_neck<65):#手合并在胸前
                if self.flymode!=2:
                    if time.time()-self.flymodechange>2:
                        self.flymodechange=time.time()
                        if self.distance_midneck and self.distance_shd:
                            self.lock_distance_mn=self.distance_midneck
                            self.lock_distance_sd=self.distance_shd
                            self.flymode=2
                            self.preflymode=self.flymode
                        else:
                            self.flymode=self.preflymode#进入模式失败
                else:
                    if time.time()-self.flymodechange>2:
                        self.flymodechange=time.time()
                        self.lock_distance_mn=None
                        self.lock_distance_sd=None
                        self.flymode=0
                        self.preflymode=self.flymode
            else:
                if self.preflymode:
                    self.flymode=self.preflymode#没有切换模式，则不改变
                else:
                    self.flymode=0
                    self.preflymode=self.flymode
                    
                
        
            
        #判断是否存在target
        if self.neck:
            self.target=self.neck
            self.flymode=self.preflymode#上一个模式，如果目标丢失后可以直接返回来
        elif self.nose:
            self.target=self.nose
            self.flymode=self.preflymode
        elif self.midp:
            self.target=self.midp
            self.flymode=self.preflymode
        elif self.rightshd:
            self.target=self.rightshd
            self.flymode=self.preflymode
        elif self.letfshd:
            self.target=self.letfshd
            self.flymode=self.preflymode
        else:
            self.target=None
            if (self.flymode==5) or (self.flymode==4):
                pass
            else:
                self.flymode=3#丢失目标直接滚动起来

        #m没有起飞时则判断起飞方式
       # print(self.press)
        if self.isfly!=1:
            if self.press==1:#抛飞#如果没有抛起来怎么办
                if self.flymode!=6:
                    if time.time()-self.flymodechange>2:
                        self.flymodechange=time.time()
                        self.flymode=6
             #   else:#退出抛飞
              #      if time.time()-self.flymodechange>2:
               #         sefl.flymodechange=time.time()  
               #         self.flymode=0
        #print(self.flymode)


           
           


            

    def get_comd(self,kp,userc):
        comd=[0,0,0,0,0]#每轮循环都回中
        if userc[4]==1:
            self.check_mode(kp)
            if self.target:
                xoff=self.target[0]-self.point[0]#计算修正量
                yoff=self.target[1]-self.point[1]
            else:
                xoff=0
                yoff=0
            
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
                comd[0]=int(-self.pid_yaw(xoff))
                comd[3]=int(self.pid_thro(yoff))
                if self.isfly:
                    if self.pose==0:#这层判断用于控制前后左右
                        pass
                    elif self.pose==1:
                        comd[2]=self.posespeed
                    elif self.pose==2:
                        comd[2]=-self.posespeed
                    elif self.pose==3:
                        comd[1]=-self.posespeed
                    elif self.pose==4:
                        comd[1]=self.posespeed

            elif self.flymode==1:#        1跟随模式，修正偏航和锁定距离
                self.pid_yaw=PID(0.25,0,0,setpoint=0,output_limits=(-100,100))
                self.pid_thro=PID(0.3,0.005,0.1,setpoint=0,output_limits=(-50,50))
                self.pid_pith=PID(0.4,0.04,0.4,setpoint=0,output_limits=(-50,50))

                comd[0]=int(-self.pid_yaw(xoff))
                comd[3]=int(self.pid_thro(yoff))

                if self.distance_midneck and self.lock_distance_mn:#判断是否存在这两个值，存在才能给命令，不存在则使用初始值
                    comd[2]=int(-self.pid_pith(self.lock_distance_mn-self.distance_midneck))
                elif self.distance_shd and self.lock_distance_sd:
                    comd[2]=int(-self.pid_pith(self.lock_distance_sd-self.distance_shd))

                if self.isfly:
                    if self.pose==0:#这层判断用于控制前后左右
                        pass
                    elif self.pose==1:
                        if self.lock_distance_mn and self.lock_distance_sd:
                            self.lock_distance_mn+=2
                            self.lock_distance_sd+=2
                    elif self.pose==2:
                        if self.lock_distance_mn and self.lock_distance_sd:
                            self.lock_distance_mn-=2
                            self.lock_distance_sd-=2
                    elif self.pose==3:
                        comd[1]=-self.posespeed
                    elif self.pose==4:
                        comd[1]=self.posespeed
            
            elif self.flymode==2:#        2平行跟随，修正roll和锁定距离
                self.pid_yaw=PID(0.25,0,0,setpoint=0,output_limits=(-100,100))
                self.pid_thro=PID(0.3,0.005,0.1,setpoint=0,output_limits=(-50,50))
                self.pid_pith=PID(0.4,0.04,0.4,setpoint=0,output_limits=(-50,50))
                self.pid_roll= PID(0.2,0.005,0.2,setpoint=0,output_limits=(-30,30))

                #comd[0]=int(self.pid_yaw(xoff))
                comd[3]=int(self.pid_thro(yoff))
                comd[1]=int(-self.pid_roll(xoff))

                if self.distance_midneck and self.lock_distance_mn:
                    comd[2]=int(-self.pid_pith(self.lock_distance_mn-self.distance_midneck))
                elif self.distance_shd and self.lock_distance_sd:
                    comd[2]=int(-self.pid_pith(self.lock_distance_sd-self.distance_shd))

                if self.isfly:
                    if self.pose==0:#这层判断用于控制前后左右
                        pass
                    elif self.pose==1:
                        if self.lock_distance_mn and self.lock_distance_sd:
                            self.lock_distance_mn+=2
                            self.lock_distance_sd+=2
                    elif self.pose==2:
                        if self.lock_distance_mn and self.lock_distance_sd:
                            self.lock_distance_mn-=2
                            self.lock_distance_sd-=2
                    elif self.pose==3:
                        self.pid_yaw=PID(0.25,0,0,setpoint=0,output_limits=(-100,100))
                        comd[0]=int(self.pid_yaw(xoff))
                        comd[1]=-self.posespeed
                    elif self.pose==4:
                        self.pid_yaw=PID(0.25,0,0,setpoint=0,output_limits=(-100,100))
                        comd[0]=int(self.pid_yaw(xoff))
                        comd[1]=self.posespeed
                
            elif self.flymode==3: #        3丢失目标，保持高度，同时旋转寻找目标，如果超过15秒则降落
                comd[0]=40

            elif self.flymode==4: #        4降落，所有参数清零
                if self.palmflag==1:
                    comd[4]=3
                else:
                    comd[4]=4
                if self.isfly==0:
                    self.reset()
                
            
            elif self.flymode==5: #        5靠近降落在手掌，所有参数清零
                self.pid_yaw=PID(0.25,0,0,setpoint=0,output_limits=(-100,100))
                self.pid_thro=PID(0.3,0.005,0.1,setpoint=0,output_limits=(-50,50))
                self.pid_pith=PID(0.3,0.005,0.1,setpoint=0,output_limits=(-20,20))
                self.lock_distance_sd=290     #最近肩宽   
                if self.palmflag is None:
                    comd[0]=int(-self.pid_yaw(xoff))
                    comd[3]=int(self.pid_thro(yoff))
                    if self.distance_shd:
                        comd[2]=int(-self.pid_pith(self.lock_distance_sd-self.distance_shd))
                if self.distance_shd and self.lock_distance_sd:
                    if self.distance_shd>self.lock_distance_sd:
                        if self.palmflag is None:
                            comd[0]=comd[1]=comd[2]=comd[3]=0#手掌降落时所有舵量为0
                            self.palmflag=1
                            self.flymode=4
                            self.preflymode=4
                            
                        
                
                    
                
            
            elif self.flymode==6:#        6抛飞
                comd[4]=2
            # self.is_fly=1   #判断是否起飞成功？？？
                if self.isfly:
                    self.flymode=0

            
        else:#不使用pose
            #self.reset()#清空
            #拷贝命令，命令来自ui.py的class Usercomd
            comd[0]=userc[3]
            comd[1]=userc[2]
            comd[2]=userc[1]
            comd[3]=userc[0]
            #特殊命令
            comd[4]=userc[5]
            self.flymode=userc[5]+7#接受特殊指令为飞行模式，仅在键盘模式下使用
                                 #从9开始，避开前面的模式


        self.comd = comd   
        return comd
        #comd[0] comd[1] comd[2]  comd[3]  comd[4]
        #旋转     左右    前后      上下     特殊命令

    def get_state(self):#发送状态给ui,所有飞行日志
        #self.state=[0,0,0,0,0,0,0,0,0,0]
        #是否飞行 电池 飞行模式  动作指令  油门 俯仰 副翼 偏航 锁定距离 实时距离
        #需要实时更新的
        
        self.state[0]=self.isfly
        self.state[1]=self.batry
        self.state[2]=self.flymode
        if self.pose is not None:
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
        self.state[10]=self.throwflytimer
        self.state[11]=self.height
        self.state[12]=self.wifi
        #特殊，用于跟踪点数据的传输
        if self.target:
            self.state[13]=self.target[0]
            self.state[14]=self.target[1]
        else:
            self.state[13]=None
            self.state[14]=None
        #遥测数据
        self.state[15]=self.anglerroll
        self.state[16]=self.anglerpitch
        self.state[17]=self.velxy
        self.state[18]=self.velz
        self.state[19]=self.posx
        self.state[20]=self.posy
        self.state[21]=self.posz
        self.state[22]=self.pitch
        self.state[23]=self.roll
        self.state[24]=self.yew  
        self.state[25]=self.visualstate
        
            
        state=self.state
        return state

    def read_tello_data(self,data):
        self.isfly=data[1]
        self.batry=data[0]
        self.throwflytimer=data[2]
        self.height=data[3]
        self.wifi=data[4]
        #遥测数据
        self.anglerroll=data[5]
        self.anglerpitch=data[6]
        self.velxy=data[8]
        self.velz=data[7]
        self.posx=data[9]
        self.posy=data[10]
        self.posz=data[11]
        self.pitch=data[12]
        self.roll=data[13]
        self.yew=data[14]
        self.visualstate=data[15]

