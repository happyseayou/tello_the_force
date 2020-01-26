#与tello进行通信，包括视频信号处理转换为图为pose调用，然后发送conmmand产生的命令发送给飞机
import sys
import av
import tellopy   
import cv2
import numpy
import time
from Pose import *
from UI import FPS




class Tello:

    def __init__(self):
   
        #初始参数
        self.battery=None
        self.is_fly=None
        self.height=None
        self.wifi=None
        self.throw_fly_timer=None

        #开始连接飞机
        self.drone=tellopy.Tello()
        try:
            self.drone.connect()
            self.drone.set_video_encoder_rate(2)
            self.drone.start_video()

            #订阅飞行数据信息
            self.drone.subscribe(self.drone.EVENT_FLIGHT_DATA,self.flight_data_handler)

            #self.drone.wait_for_connection(60.0)
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
            print('ooooooooooooooo')
        
        self.frame_skip=300




    def send_comd(self,comd):#comd[]是一个数组，一共五个分别代表yaw，roll，pitch，throttle，command这个代表起飞等命令
        if comd[4]==0:#有特殊命令的时候不能执行任何操作
            self.drone.clockwise(comd[0])       #这里的comd是速度的量
            self.drone.right(comd[1])
            self.drone.forward(comd[2])
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
        #这个一个接受数据的函数

    def send_data(self):#用于发送数据给com
        bat=self.battery
        is_fly=self.is_fly
        tftimer=self.throw_fly_timer
        height=self.height
        wifi=self.wifi
        return bat,is_fly,tftimer,height,wifi
    
  






if __name__=='__main__':



    tello=Tello()
    my_pose=Pose()
    fps=FPS()
    frame_skip = 300
    
    for frame in tello.container.decode(video=0):
        if 0 < frame_skip:
            frame_skip = frame_skip - 1
            continue
        fps.update()
        start_time = time.time()
        image = cv2.cvtColor(numpy.array(frame.to_image()), cv2.COLOR_RGB2BGR)
        image = cv2.resize(image,(640,480))
        show=my_pose.get_kp(image)
        angle234=angle((show[2][0],show[2][1]),(show[3][0],show[3][1]),(show[4][0],show[4][1]))
        angle567=angle((show[7][0],show[7][1]),(show[6][0],show[6][1]),(show[5][0],show[5][1]))
        #if angle567:
        print('左'+str(angle234)+' '+'右'+str(angle567))
        
       # print(str(tello.is_fly))
        #else:
          #  print('ooooops')
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
        if k == 27 : break
    
    cv2.destroyAllWindows()