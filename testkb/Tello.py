
import tellopy
import sys
import av
import tellopy   
import cv2
import numpy
import time


class Tello():

    def __init__(self):
   
       
        #开始连接飞机
        self.drone=tellopy.Tello()
        try:
            self.drone.connect()
            self.drone.set_video_encoder_rate(2)
            self.drone.start_video()

            #订阅飞行数据信息
            #self.drone.subscribe(self.drone.EVENT_FLIGHT_DATA,self.flight_data_handler)

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