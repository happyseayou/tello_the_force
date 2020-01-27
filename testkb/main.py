import sys
import av
import tellopy   
import cv2
import numpy
import time
import pygame
import time
from Tello import Tello
from Com import Com
from UI import FPS



    
        #[0  1  2  3   4         5]
           #四个通道   ispose    模式
        #油 pitch roll yaw ispose   模式 0   1   2     3         4       5      
      #shift w     e    a    t          无  起飞 降落  抛飞  手掌降落  停机
       #ctrl  s    q    d    t              up down   0         0   spece

def usec(key_list):
    speed=50
    
    
    us=[0,0,0,0,0,0]
    if key_list[pygame.K_w]:#W 前进
        us[1]=speed
    if key_list[pygame.K_s]:#s后退
        us[1]=-speed
    if key_list[pygame.K_a]:#q
        us[2]=-speed
    if key_list[pygame.K_d]:#e
        us[2]=speed
    if key_list[pygame.K_q]:#a
        us[3]=-speed
    if key_list[pygame.K_e]:#d
        us[3]=speed
    if key_list[pygame.K_LSHIFT]:#shitf
        us[0]=speed
    if key_list[pygame.K_LCTRL]:#ctrl
        us[0]=-speed
    

    #特殊指令执行时通道指令无效且归零
    if key_list[pygame.K_0]:#0
        us[5]=2
        us[0]=us[1]=us[2]=us[3]=0
        
    if key_list[pygame.K_9]:#退出
        us[5]=3
        us[0]=us[1]=us[2]=us[3]=0
        
    
    elif key_list[pygame.K_UP]:#up
        #四通道值刷为0
        us[5]=1
        us[0]=us[1]=us[2]=us[3]=0
        
    elif key_list[pygame.K_DOWN]: #down
        #四通道值刷为0
        us[5]=4
        us[0]=us[1]=us[2]=us[3]=0

    elif key_list[pygame.K_SPACE]:#space紧急停机
        pass
        #四个通道刷为0
    
    #八向翻滚：5  6 7 8  9 10  11 12 
    #对应键位  8  2 4 6  7  9  1  3
    elif key_list[pygame.K_KP8]:
        us[5]=5
        us[0]=us[1]=us[2]=us[3]=0
    elif key_list[pygame.K_KP2]:
        us[5]=6
        us[0]=us[1]=us[2]=us[3]=0
    elif key_list[pygame.K_KP4]:
        us[5]=7
        us[0]=us[1]=us[2]=us[3]=0
    elif key_list[pygame.K_KP6]:
        us[5]=8
        us[0]=us[1]=us[2]=us[3]=0
    elif key_list[pygame.K_KP7]:
        us[5]=9
        us[0]=us[1]=us[2]=us[3]=0
    elif key_list[pygame.K_KP9]:
        us[5]=10
        us[0]=us[1]=us[2]=us[3]=0
    elif key_list[pygame.K_KP1]:
        us[5]=11
        us[0]=us[1]=us[2]=us[3]=0
    elif key_list[pygame.K_KP3]:
        us[5]=12
        us[0]=us[1]=us[2]=us[3]=0
    return us


def main():
    pygame.init()
    screen = pygame.display.set_mode((20, 20), 0, 32)
    
    fps = FPS()

    tello=Tello()
    com=Com()
    
    frame_skip=300
    for frame in tello.container.decode(video=0):#一定要用这个循环来获取才不会产生delay
        if 0 < frame_skip:
            frame_skip = frame_skip - 1
            continue
        fps.update()
        start_time = time.time()
        image = cv2.cvtColor(numpy.array(frame.to_image()), cv2.COLOR_RGB2BGR)
        key_list = pygame.key.get_pressed()
        userc=usec(key_list)
        comd=com.get_comd(userc)
        tello.send_comd(comd)
        pygame.display.update()
        fps.display(image)
        cv2.imshow('t',image)
        if frame.time_base < 1.0/60:
            time_base = 1.0/60
        else:
            time_base = frame.time_base
        frame_skip = int((time.time() - start_time)/time_base)
        k = cv2.waitKey(1) & 0xff
        if k == 27 : 
            pygame.display.quit()
            break
    cv2.destroyAllWindows()
    

if __name__=='__main__':
    main()