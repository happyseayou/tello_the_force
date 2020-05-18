#main函数，主循环代码放这里
import cv2
import pygame
import time
import numpy

import time 
from Tello import Tello
from simple_pid import PID
from UI import FPS,UID,Keyuser,Pydisplay,Mapui
from math import atan2, degrees, sqrt,pi,atan
from Pose import Pose
from Com import*
from mapcom import Mapcom
#import profile
import numpy as np
import gc
from multiprocessing import Process, Pipe

def write(sd,imge) -> None:#用管道效率比缓冲区高
    try:
        sd.send(imge)
    except:
        sd.close()

def read(stack) -> None:
    fourcc = cv2.VideoWriter_fourcc(*'avc1')
    out = cv2.VideoWriter('video_out.mp4',fourcc , 25, (960, 720))
    while 1:
        try:
            frame=stack.recv()
            out.write(frame)
            cv2.imshow("REC", frame)
            cv2.waitKey(1)#与pygame的键盘存在未知冲突
        except:
            break
    out.release()
    stack.close()
    cv2.destroyAllWindows()
def nothing(x):
    pass

# def mapread(mapstack) -> None:
#     mapui=Mapui()
#     while 1:
#         try:
#             flightstate=mapstack.recv()
#             mapui.mapshow(flightstate)
#         except:
#             break
#     mapstack.close()
#     cv2.destroyAllWindows()

# def mapsand(mapsd,flightstate) -> None:
#     try:
#         mapsd.send(flightstate)
#     except:
#         mapsd.close()

def main():
    isrec=0
    #muitmap=0
    tello=Tello()
    pydisplay=Pydisplay()
    keyuser=Keyuser()#键盘命令
    ui=UID()
    mapui=Mapui()
    # if muitmap==0:
    #     mapui=Mapui()
    # else:
    #     mapstack,mapsd = Pipe()
    #     #stack= Manager().list()
    #     mapshowing = Process(target=mapread, args=(mapstack,))
    #     mapshowing.start()
    pose=Pose()
    com=Com()
    mapcom=Mapcom()
    frame_skip=300
    #pidtuning
    # if mapcom.tpid==1:
    #     pidimg=np.zeros((500, 512, 3), np.uint8)
    #     cv2.namedWindow('pidyaw')
    #     cv2.namedWindow('pidthro')
    #     cv2.namedWindow('pidpith')
    #     cv2.namedWindow('pidroll')

    #     cv2.createTrackbar('p', 'pidyaw', 0, 100, nothing)
    #     cv2.createTrackbar('i', 'pidyaw', 0, 100, nothing)
    #     cv2.createTrackbar('d', 'pidyaw', 0, 100, nothing)
    #     cv2.createTrackbar('down', 'pidyaw', 0, 100, nothing)
    #     cv2.createTrackbar('up', 'pidyaw', 0,100, nothing)

    #     cv2.createTrackbar('p', 'pidthro', 0, 100, nothing)
    #     cv2.createTrackbar('i', 'pidthro', 0, 100, nothing)
    #     cv2.createTrackbar('d', 'pidthro', 0, 100, nothing)
    #     cv2.createTrackbar('down', 'pidthro', 0, 100, nothing)
    #     cv2.createTrackbar('up', 'pidthro', 0,100, nothing)

    #     cv2.createTrackbar('p', 'pidpith', 0, 100, nothing)
    #     cv2.createTrackbar('i', 'pidpith', 0, 100, nothing)
    #     cv2.createTrackbar('d', 'pidpith', 0, 100, nothing)
    #     cv2.createTrackbar('down', 'pidpith', 0, 100, nothing)
    #     cv2.createTrackbar('up', 'pidpith', 0,100, nothing)

    #     cv2.createTrackbar('p', 'pidroll', 0, 100, nothing)
    #     cv2.createTrackbar('i', 'pidroll', 0, 100, nothing)
    #     cv2.createTrackbar('d', 'pidroll', 0, 100, nothing)
    #     cv2.createTrackbar('down', 'pidroll', 0, 100, nothing)
    #     cv2.createTrackbar('up', 'pidroll',  0,100, nothing)

    #录像功能
    if isrec:
        stack,sd= Pipe()
        #stack= Manager().list()
        pr = Process(target=read, args=(stack,))
        pr.start()
    #try:
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
        if userc[4]==0 or userc[4]==1:
            if userc[4]==1:#判断使用跟踪
                kp,out=pose.get_kp(image)
            else:#不使用
                kp=[[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0]]
            comd=com.get_comd(kp,userc)#接受两个数组进行判断
            tello.send_comd(comd)
            flight=tello.send_data()#飞行数据
            com.read_tello_data(flight)#飞控获取数据用于判断指令
            flightstate=com.get_state()#命令状态
            
            if userc[4]==1:#使用
                rec=ui.show(out,kp,flightstate)#显示并负责播放声音
            else:#不用
                rec=ui.show(imageraw,0,flightstate)
            if isrec:
                write(sd,rec)

        #print(userc[4])

        elif userc[4]==2 or userc[4]==3:
            # if mapcom.tpid==1:
            #     cv2.imshow('pidyaw', pidimg)
            #     cv2.imshow('pidthro', pidimg)
            #     cv2.imshow('pidpith', pidimg)
            #     cv2.imshow('pidroll', pidimg)
            #     pid=[[cv2.getTrackbarPos('p', 'pidyaw')/10,cv2.getTrackbarPos('i', 'pidyaw')/100,cv2.getTrackbarPos('d', 'pidyaw')/10,-cv2.getTrackbarPos('down', 'pidyaw'),cv2.getTrackbarPos('up', 'pidyaw')],
            #         [cv2.getTrackbarPos('p', 'pidthro')/10,cv2.getTrackbarPos('i', 'pidthro')/100,cv2.getTrackbarPos('d', 'pidthro')/10,-cv2.getTrackbarPos('down', 'pidthro'),cv2.getTrackbarPos('up', 'pidthro')],
            #         [cv2.getTrackbarPos('p', 'pidpith')/10,cv2.getTrackbarPos('i', 'pidpith')/100,cv2.getTrackbarPos('d', 'pidpith')/10,-cv2.getTrackbarPos('down', 'pidpith'),cv2.getTrackbarPos('up', 'pidpith')],
            #         [cv2.getTrackbarPos('p', 'pidroll')/10,cv2.getTrackbarPos('i', 'pidroll')/100,cv2.getTrackbarPos('d', 'pidroll')/10,-cv2.getTrackbarPos('down', 'pidroll'),cv2.getTrackbarPos('up', 'pidroll')]]
            data=tello.send_data()
            mapcom.readflightdata(data)
            # if mapcom.tpid==1:
            #     comd=mapcom.com(userc,pid)
            # else:
            comd=mapcom.com(userc)
            flightstate=mapcom.send_flightdata()
            tello.send_comd(comd)
            checkoutmap=mapcom.checkalldone()
            if checkoutmap==1:
                userc[4]=0
                keyuser.us[4]=0
                mapcom.checkdone=None
            if isrec:
                write(sd,imageraw)
            mapui.mapshow(flightstate)
            # if muitmap==0:
            #     mapui.mapshow(flightstate)
            # else:
            #     mapsand(mapsd,flightstate)

        pydisplay.display(image2surface,flightstate)#pygame飞行界面

        #目前对丢帧策略的理解，只要分母不要小于飞机发送回来的最大帧速率则不会产生延迟同时保证帧率
        #例子里的60是不合理的，会多丢弃一半的帧，浪费辽
        if frame.time_base < 1.0/35:
            if userc[4]==1:
                time_base = 1.0/35#使用pose稍微保守一点
            else:
                time_base = 1.0/35
        else:
            time_base = frame.time_base
        frame_skip = int((time.time() - start_time)/time_base)
        
        k = cv2.waitKey(1) & 0xff#与pygame的键盘存在未知冲突
        if k == 27 : 
            pygame.display.quit()
            tello.drone.quit()#退出
            break
        #print(time.time()-start_time)
    
    # except:
    #     print('连接超时或发生错误退出辽')

    cv2.destroyAllWindows()#关掉飞机直接退出程序
    tello.drone.quit()
    pygame.display.quit()
    

if __name__=='__main__':
    main()
    #rofile.run("main()")

        