#main函数，主循环代码放这里
import cv2
import pygame
import time
import numpy

import time 
from Tello import Tello
from simple_pid import PID
from UI import FPS,UID,Keyuser,Pydisplay
from math import atan2, degrees, sqrt,pi,atan
from Pose import Pose
from Com import*
#import profile


def main():
    tello=Tello()
    pydisplay=Pydisplay()
    keyuser=Keyuser()#键盘命令
    ui=UID()
    pose=Pose()
    com=Com()
    frame_skip=300
    try:
        for frame in tello.container.decode(video=0):#一定要用这个循环来获取才不会产生delay
            if 0 < frame_skip:
                frame_skip = frame_skip - 1
                continue
            start_time = time.time()
            image2surface=numpy.array(frame.to_image())#做个拷贝给pygame
            image = cv2.cvtColor(image2surface, cv2.COLOR_RGB2BGR)
            key_list = pygame.key.get_pressed()
            imageraw=image
            image = cv2.resize(image,(640,480))#这个太大会爆显存

            userc=keyuser.usec(key_list)#来自用户输入的命令
            #userc[0                1 2 3 4   5         ]
                #是否使用openpose    四个通道  模式
            if userc[4]==1:#判断使用跟踪
                kp=pose.get_kp(image)
            else:#不使用
                kp=[[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0]]
            comd=com.get_comd(kp,userc)#接受两个数组进行判断
            tello.send_comd(comd)
            flight=tello.send_data()#飞行数据
            com.read_tello_data(flight)#飞控获取数据用于判断指令
            flightstate=com.get_state()#命令状态
            pydisplay.display(image2surface,flightstate)#pygame飞行界面
            if userc[4]==1:#使用
                ui.show(image,kp,flightstate)#显示并负责播放声音
            else:#不用
                ui.show(imageraw,0,flightstate)
            
            if frame.time_base < 1.0/60:
                time_base = 1.0/60
            else:
                time_base = frame.time_base
            frame_skip = int((time.time() - start_time)/time_base)
            k = cv2.waitKey(1) & 0xff
            if k == 27 : 
                pygame.display.quit()
                tello.drone.quit()#退出
                break
        
    except:
        print('连接超时或发生错误退出辽')

    cv2.destroyAllWindows()#关掉飞机直接退出程序
    tello.drone.quit()
    pygame.display.quit()
    

if __name__=='__main__':
    main()
    #rofile.run("main()")

        