#与tello进行通信，包括视频信号处理转换为图为pose调用，然后发送conmmand产生的命令发送给飞机
import sys
import av
import tellopy   
import cv2
import numpy
import time
from Pose import *
from UI import FPS
from math import atan2, degrees, sqrt,pi,atan,asin





class Tello:

    def __init__(self):
        #传感器数据
         #mvo单目视觉里程计
        self.pos_x = 0.0
        self.pos_y = 0.0
        self.pos_z = 0.0
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.vel_z = 0.0
        self.visual_state=None
        #imu惯性测量单元
        self.acc_x = 0.0
        self.acc_y = 0.0
        self.acc_z = 0.0
        self.gyro_x = 0.0
        self.q0=0.0
        self.q1=0.0
        self.q2=0.0
        self.q3=0.0
   
        #初始参数
        self.battery=None
        self.is_fly=None
        self.height=None
        self.wifi=None
        self.throw_fly_timer=None

        #开始连接飞机
        self.drone=tellopy.Tello()
        try:
            self.drone.set_loglevel(2)
            self.drone.connect()
            self.drone.set_video_encoder_rate(1)#2=1.6Mbps,1=1.1Mbps,3=2.1Mbps,4=3.2Mbps,5=4.2Mbps
            self.drone.start_video()

            #订阅飞行数据信息
            self.drone.subscribe(self.drone.EVENT_FLIGHT_DATA,self.flight_data_handler)
            self.drone.subscribe(self.drone.EVENT_LOG_DATA,self.log_data_handler)

            
            self.drone.wait_for_connection(5.0)
            retry = 3
            self.container=None   #container用于存放帧
            while self.container is None and 0 < retry:
                retry-=1
                try:
                    self.container=av.open(self.drone.get_video_stream())
                except av.AVError as ave:
                    print(ave)
                    print('retry...')
        except:
            print('ooooooooooooooops')
            self.drone.quit()
            #pygame.display.quit()
        
        self.frame_skip=300

    """
    def send_super_comd(self,comd):#通过命令直接控制飞机
        #self.drone.sock.sendto('command',('192.168.10.1', 8889))
        x=comd[0]
        y=comd[1]
        z=comd[2]
        speed=comd[4]
        supercmd=comd[5]#直接是文本命令
        if supercmd==0:
            cmd=supercmd
        else:
            cmd='go'+' '+str(x)+' '+str(y)+' '+str(z)+' '+str(speed)
        self.drone.sock.sendto(cmd,('192.168.10.1', 8889))
    """

    def send_comd(self,comd):#comd[]是一个数组，一共五个分别代表yaw，roll，pitch，throttle，command这个代表起飞等命令
        if comd[4]==0:#有特殊命令的时候不能执行任何操作
            #if comd[0]!=0:#不等于0才发送
            self.drone.clockwise(comd[0])       #这里的comd是速度的量
           #if comd[0]!=0:
            self.drone.right(comd[1])
            #if comd[0]!=0:
            self.drone.forward(comd[2])
            #if comd[0]!=0:
            self.drone.up(comd[3])
        else:                               #cond[4]是命令
            if comd[4]==1:
                self.drone.takeoff()
            elif comd[4]==2:
                self.drone.throw_and_go()
            elif comd[4]==3:
                self.drone.palm_land()
            elif comd[4]==4:
                self.drone.land()
            #八向翻滚
            elif comd[4]==5:
                self.drone.flip_forward()
            elif comd[4]==6:
                self.drone.flip_back()
            elif comd[4]==7:
                self.drone.flip_left()
            elif comd[4]==8:
                self.drone.flip_right()
            elif comd[4]==9:
                self.drone.flip_forwardleft()
            elif comd[4]==10:
                self.drone.flip_forwardright()
            elif comd[4]==11:
                self.drone.flip_backleft()
            elif comd[4]==12:
                self.drone.flip_backright()

    #comd[0] comd[1] comd[2]  comd[3]  comd[4]
    #旋转     左右    前后      上下     特殊命令

    def flight_data_handler(self,event,sender,data):
        self.battery=data.battery_percentage
        self.is_fly=data.em_sky
        self.throw_fly_timer=data.throw_fly_timer
        #self.height=data.height
        self.height=data.height
        self.wifi=data.wifi_strength
        self.visual_state=data.fly_mode#起飞11，降落12，没有起飞：6静止可以起飞，1未静止不可起飞：飞行中：6视觉定位正常，1飘了
        #这个一个接受数据1的函数

    def log_data_handler(self, event, sender, data):
        """
            Listener to log data from the drone.
        """  
        #mvo单目视觉里程计
        self.pos_x = data.mvo.pos_x*100#厘米
        self.pos_y = data.mvo.pos_y*100
        self.pos_z = data.mvo.pos_z*100
        
        #imu惯性测量单元
        self.acc_x = 100*data.imu.acc_x#用于计算roll和pitch的角度
        self.acc_y = 100*data.imu.acc_y
        self.acc_z = 100*data.imu.acc_z
        self.vel_x = data.imu.vg_x*10#这个数据比视觉的准x10单位分米
        self.vel_y = data.imu.vg_y*10
        self.vel_z = data.imu.vg_z*10
        #四元数
        self.q0=data.imu.q0
        self.q1=data.imu.q1
        self.q2=data.imu.q2
        self.q3=data.imu.q3
        
        
        

    def send_data(self):#用于发送数据给com
        bat=self.battery
        is_fly=self.is_fly
        tftimer=self.throw_fly_timer
        height=self.height
        wifi=self.wifi
        #传感器数据
         #mvo单目视觉里程计
        posx=self.pos_x #位置信息以后可用于轨道规划
        posy=self.pos_y 
        posz=self.pos_z 
        #print(posx,posy,posz)
        velz=self.vel_z #垂直速度
        velxy=sqrt(self.vel_x**2+self.vel_y**2)      #水平速度
        #imu惯性测量单元
        
        #用四元数算
        q0=self.q0
        q1=self.q1
        q2=self.q2
        q3=self.q3#注意对应坐标
        #需要起飞后修正的值,每次起飞0点都不一样，只有yaw每次开机更新，有时定位失败要将进行暂停
        

        pitch=degrees(asin(2*q0*q2-2*q3*q1))
        roll=degrees(atan2(2*q0*q1+2*q3*q2,1-2*q1**2-2*q2**2))
        yew= degrees(atan2(2*q1*q2+2*q0*q3,1-2*q2**2-2*q3**2))

        # #用重力加速度算俯仰角与翻滚角   
        # anglerroll=degrees(atan(self.acc_y/self.acc_z))
        # anglerpitch=degrees(atan(self.acc_x/self.acc_z))
        anglerroll=roll
        anglerpitch=-pitch

        visual_state=self.visual_state
        return bat,is_fly,tftimer,height,wifi,anglerroll,anglerpitch,velz,velxy,posx,posy,posz,pitch,roll,yew,visual_state
        #       0    1       2       3     4    5            6         7   8      9   10   11    12    13   14    15           
    
    
  






if __name__=='__main__':

    ispose=0
    fps=FPS()
    tello=Tello()
    if ispose==1:
        my_pose=Pose()
    
    frame_skip = 300
    
    for frame in tello.container.decode(video=0):
        if 0 < frame_skip:
            frame_skip = frame_skip - 1
            continue
        fps.update()
        start_time = time.time()
        image = cv2.cvtColor(numpy.array(frame.to_image()), cv2.COLOR_RGB2BGR)
        if ispose==1:
            image = cv2.resize(image,(640,480))
            show=my_pose.get_kp(image)
            if show[2][0]:#值判断一个就好
                cv2.circle(image, (show[2][0], show[2][1]), 3, (0, 0, 255), -1)
            if show[3][0]:
                cv2.circle(image, (show[3][0], show[3][1]), 3, (0, 0, 255), -1)
            if show[4][0]:
                cv2.circle(image, (show[4][0], show[4][1]), 3, (0, 0, 255), -1)
            if show[5][0]:#值判断一个就好
                cv2.circle(image, (show[5][0], show[5][1]), 3, (0, 0, 255), -1)
            if show[6][0]:
                cv2.circle(image, (show[6][0], show[6][1]), 3, (0, 0, 255), -1)
            if show[7][0]:
                cv2.circle(image, (show[7][0], show[7][1]), 3, (0, 0, 255), -1)
        
        
        fps.display(image)
        cv2.imshow('Original', image)
        
       
        if frame.time_base < 1.0/60:
            time_base = 1.0/60
        else:
            time_base = frame.time_base
        frame_skip = int((time.time() - start_time)/time_base)
        k = cv2.waitKey(1) & 0xff
        if k == 27 : 
            tello.drone.quit()#退出
            break
            
    
    cv2.destroyAllWindows()