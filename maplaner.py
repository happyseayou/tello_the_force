import pandas as pd 
import cv2
import numpy as np 
from tkinter import*
import time
import tkinter.messagebox
import random


ls=[]
lscom=[]
xyi=[]
pointxy=[]#用来显示的，飞行坐标
pointxydrawer=[]#用来画的，画面坐标
inputing=False
img = np.zeros([900,1600,3], np.uint8)
guide1='chose a point and right clickdouble as a zero point'
cv2.putText(img, guide1, (50,350), cv2.FONT_HERSHEY_SIMPLEX, 1.8, (255, 255, 255), 2)
preimg=None  
nowimg=img
prelist=[]

#cv2.createTrackbar('mode','maplaner',0,1,nothing)

def draw_map(event,x,y,flags,param):
    #print(flags,event)
    #mode=cv2.getTrackbarPos('mode','maplaner')
    fontbig=2
    Scalexy=600/821
    global preimg
    global nowimg
    global inputing
    global raiseerror
    if raiseerror==0:
        if flags==1 and event == cv2.EVENT_LBUTTONDBLCLK:#左键双击go
            if ls!=[] and ls[len(ls)-1][0]!=4 and inputing!=True:
                prelist.append(nowimg.copy())
                if xyi!=[]:
                    #修正坐标为实际坐标
                    posx=(x-xyi[0])*Scalexy
                    posy=(-y+xyi[1])*Scalexy
                posz=getInput('输入','go高度厘米整数数默认110')
                if not posz.isdigit():
                    posz=110
                else:
                    posz=int(posz)
                print(posz,type(posz))
                cv2.circle(nowimg,(x,y),15,(255,255,255),2)
                cv2.circle(nowimg,(x,y),5,(0,255,255),-1)
                cv2.putText(nowimg, 'go', (x+20,y-20), cv2.FONT_HERSHEY_SIMPLEX , 1, (0, 0, 0), fontbig)
                cv2.rectangle(nowimg,(x+20,y-10),(x+60,y-40),(255,255,255),1)
                ls.append([2,x,y,0])
                lscom.append([2,posx,posy,posz])
                i=len(ls)-2
                if ls[i+1][0]!=4 and ls[i+1][0]!=1:
                    cv2.arrowedLine(nowimg, (ls[i][1],ls[i][2]), ((ls[i+1][1]+ls[i][1])//2,(ls[i+1][2]+ls[i][2])//2), (0,255,255),2,1,0,0.05)
                    cv2.line(nowimg, ((ls[i+1][1]+ls[i][1])//2,(ls[i+1][2]+ls[i][2])//2), (ls[i+1][1],ls[i+1][2]), (0,255,255), 2, 4)
        elif flags==33 and event == cv2.EVENT_LBUTTONDBLCLK:#alt+左键双击不旋转go
            if ls!=[] and ls[len(ls)-1][0]!=4 and inputing!=True:
                prelist.append(nowimg.copy())
                if xyi!=[]:
                    #修正坐标为实际坐标
                    posx=(x-xyi[0])*Scalexy
                    posy=(-y+xyi[1])*Scalexy
                posz=getInput('输入','closeon高度厘米整数数默认110')
                if not posz.isdigit():
                    posz=110
                else:
                    posz=int(posz)
                print(posz,type(posz))
                cv2.circle(nowimg,(x,y),15,(255,255,255),2)
                cv2.circle(nowimg,(x,y),5,(0,255,255),-1)
                cv2.putText(nowimg, 'CN', (x+20,y-20), cv2.FONT_HERSHEY_SIMPLEX , 1, (0, 0, 0), fontbig)
                cv2.rectangle(nowimg,(x+20,y-18),(x+60,y-45),(255,255,255),1)
                ls.append([8,x,y,0])
                lscom.append([8,posx,posy,posz])
                i=len(ls)-2
                if ls[i+1][0]!=4 and ls[i+1][0]!=1:
                    cv2.arrowedLine(nowimg, (ls[i][1],ls[i][2]), ((ls[i+1][1]+ls[i][1])//2,(ls[i+1][2]+ls[i][2])//2), (0,255,255),2,1,0,0.05)
                    cv2.line(nowimg, ((ls[i+1][1]+ls[i][1])//2,(ls[i+1][2]+ls[i][2])//2), (ls[i+1][1],ls[i+1][2]), (0,255,255), 2, 4)
        elif event == cv2.EVENT_RBUTTONDBLCLK:#右键双击起飞
            if ls==[] and inputing!=True:
                #prelist.append(nowimg.copy())
                xyi.append(x)
                xyi.append(y)
                #建立坐标系
                # nowimg[:, :, 0] = np.zeros([900,1600]) + 255
                # nowimg[:, :, 1] = np.ones([900,1600]) + 254
                # nowimg[:, :, 2] = np.ones([900,1600]) * 255
                nowimg=bgimg
                cv2.arrowedLine(nowimg, (0,xyi[1]), (1600,xyi[1]), (0,0,0),1,8,0,0.02)#x轴
                cv2.arrowedLine(nowimg, (xyi[0],900), (xyi[0],0), (0,0,0),1,8,0,0.03)#y轴
                cv2.putText(nowimg, 'x', (1600-30,xyi[1]), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), fontbig)
                cv2.putText(nowimg, 'y', (xyi[0],30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), fontbig)
                #标尺
                for i in [-6,-5,-4,-3,-2,-1,1,2,3,4,5,6]:
                    sx=str(i)+'m'
                    sy=str(-i)+'m'
                    cv2.circle(nowimg,(int(xyi[0]+100*i/Scalexy),xyi[1]),2,(0,0,0),-1)
                    cv2.putText(nowimg, sx, (int(xyi[0]+100*i/Scalexy),xyi[1]+25), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 1)
                    cv2.circle(nowimg,(xyi[0],int(xyi[1]+100*i/Scalexy)),2,(0,0,0),-1)
                    cv2.putText(nowimg, sy, (xyi[0],int(xyi[1]+100*i/Scalexy)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 1)

                height=getInput('输入','起飞高度分米整数默认10')
                if not height.isdigit():
                    height=10
                else:
                    height=int(height)
                print(height,type(height))
                cv2.circle(nowimg,(x,y),20,(160,160,160),2)
                cv2.putText(nowimg, 'home', (x+20,y+40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), fontbig)
                cv2.rectangle(nowimg,(x+20,y+15),(x+110,y+45),(255,255,255),1)
                ls.append([0,x,y,0])
                lscom.append([0,height,0,0])
        elif flags==4 and event==cv2.EVENT_MBUTTONDBLCLK:#中间键双击降落
            if ls!=[] and ls[len(ls)-1][0]!=4 and inputing!=True:
                prelist.append(nowimg.copy())
                cv2.circle(nowimg,(ls[len(ls)-1][1],ls[len(ls)-1][2]),10,(0,0,255),-1)
                cv2.putText(nowimg, 'land', (ls[len(ls)-1][1]-30,ls[len(ls)-1][2]+73), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), fontbig)
                cv2.rectangle(nowimg,(ls[len(ls)-1][1]-30,ls[len(ls)-1][2]+50),(ls[len(ls)-1][1]+37,ls[len(ls)-1][2]+75),(255,255,255),1)
                cv2.line(nowimg, (ls[-1][1],ls[-1][2]), (ls[-1][1],ls[-1][2]+50), (0,0,0), 2, 4)
                ls.append([4,ls[len(ls)-1][1],ls[len(ls)-1][2]])
                lscom.append([4,0,0,0])
        elif flags==10 and event==2:#ctrl+右键单击holdon
            if ls!=[] and ls[len(ls)-1][0]!=4 and inputing!=True:
                prelist.append(nowimg.copy())
                time=getInput('输入','悬停时间秒整数默认2')
                if not time.isdigit():
                    time=2
                else:
                    time=int(time)
                cv2.line(nowimg, (ls[-1][1]-15,ls[-1][2]-15), (ls[-1][1]+15,ls[-1][2]+15), (0,0,0), 2, 4)
                cv2.line(nowimg, (ls[-1][1]-15,ls[-1][2]+15), (ls[-1][1]+15,ls[-1][2]-15), (0,0,0), 2, 4)
                cv2.putText(nowimg, 'holdon', (ls[len(ls)-1][1]-118,ls[len(ls)-1][2]-15), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), fontbig)
                cv2.rectangle(nowimg,(ls[-1][1]-118,ls[-1][2]-40),(ls[len(ls)-1][1]-16,ls[len(ls)-1][2]-12),(255,255,255),1)
                ls.append([1,ls[len(ls)-1][1],ls[len(ls)-1][2],0])
                lscom.append([1,time,0,0])
        elif flags==9 and event==1 :#ctrl+左键返航
            if ls!=[] and ls[len(ls)-1][0]!=4 and ls[len(ls)-1][0]!=3 and ls[len(ls)-1][0]!=0 and ls[-1][1]!=0 and ls[-1][2]!=0 and inputing!=True:
                prelist.append(nowimg.copy())
                x=ls[0][1]
                y=ls[0][2]
                posx=0
                posy=0
                posz=getInput('输入','返航高度厘米整数默认110')
                if not posz.isdigit():
                    posz=110
                else:
                    posz=int(posz)
                print(posz)
                cv2.rectangle(nowimg,(x+10,y+10),(x-10,y-10),(200,0,200),1)
                ls.append([3,x,y,0])
                lscom.append([3,posx,posy,posz])
                #画箭头
                i=len(ls)-2
                if ls[i+1][0]!=4 and ls[i+1][0]!=1:
                    cv2.rectangle(nowimg,(ls[i][1]+10,ls[i][2]+10),(ls[i][1]-10,ls[i][2]-10),(200,0,200),1)
                    cv2.putText(nowimg, 'gohome', (ls[i][1]-145,ls[i][2]+30), cv2.FONT_HERSHEY_SIMPLEX , 1, (0, 0, 0), fontbig)
                    cv2.rectangle(nowimg,(ls[i][1]-145,ls[i][2]+4),(ls[i][1]-20,ls[i][2]+39),(255,255,255),1)
                    cv2.arrowedLine(nowimg, (ls[i][1],ls[i][2]), ((ls[i+1][1]+ls[i][1])//2,(ls[i+1][2]+ls[i][2])//2), (0,255,255),2,1,0,0.05)
                    cv2.line(nowimg, ((ls[i+1][1]+ls[i][1])//2,(ls[i+1][2]+ls[i][2])//2), (ls[i+1][1],ls[i+1][2]), (0,255,255), 2, 4)
        elif flags==1 and event==1:
            
            if ls!=[] and inputing!=True:
                preimg=nowimg.copy()
                #cv2.rectangle(img,(5,0),(120,80),(255,255,255),-1)
                if xyi!=[]:
                    #修正坐标为实际坐标
                    posx=(x-xyi[0])*Scalexy
                    posy=(-y+xyi[1])*Scalexy
                    pointxy.clear()
                    pointxy.append(posx)
                    pointxy.append(posy)
                    pointxydrawer.clear()
                    pointxydrawer.append(x)
                    pointxydrawer.append(y)
                    sx='x:'+str(int(pointxy[0]))+'cm'
                    sy='y:'+str(int(pointxy[1]))+'cm'
                    cv2.putText(nowimg, sx, (x+10,y+10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
                    cv2.putText(nowimg, sy, (x+10,y+40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
                    cv2.circle(nowimg,(x,y),5,(255,0,0),-1)
                    print(pointxydrawer,end="")
                    print(pointxy)
                    pointxydrawer.clear()
                    pointxy.clear()
        elif flags==0 and event==cv2.EVENT_LBUTTONUP:
            if ls!=[] and inputing!=True:
                nowimg=preimg.copy()
        elif event==cv2.EVENT_RBUTTONDOWN:#右键撤销上一步
            if ls!=[] and ls[len(ls)-1][0]!=0 and inputing!=True:
                ls.pop()
                lscom.pop()
                nowimg=prelist.pop()
        # elif event==cv2.EVENT_MOUSEMOVE:
        #     coloris=(random.randint(0,255),random.randint(0,255),random.randint(0,255))
        #     cv2.circle(nowimg,(x,y),2,coloris,-1)

def getInput(title, message):
    global inputing
    inputing=True 
    def return_callback(event):
        print('quit...')
        root.quit()
    def close_callback():
        tkinter.messagebox.showinfo("提示", '输入后回车...')
    root = Tk(className=title)
    root.wm_attributes('-topmost', 1)
    screenwidth, screenheight = root.maxsize()
    width = 300
    height = 100
    size = '%dx%d+%d+%d' % (width, height, (screenwidth - width)/2, (screenheight - height)/2)
    root.geometry(size)
    root.resizable(0, 0)
    lable = Label(root, height=2)
    lable['text'] = message
    lable.pack()
    entry = Entry(root)
    entry.bind('<Return>', return_callback)
    entry.pack()
    entry.focus_set()
    root.protocol("WM_DELETE_WINDOW", close_callback)
    root.mainloop()
    h= entry.get()
    root.destroy()
    inputing=False
    return h

def message_askyesno(title,Message):
    global raiseerror
    top =Tk() 
    top.withdraw()  
    top.update()
    raiseerror=1  
    tkinter.messagebox.showerror(title,Message)
    top.destroy()
    raiseerror=0

def nothing(value):
    pass

cv2.namedWindow('maplaner')
cv2.setMouseCallback('maplaner',draw_map)
raiseerror=0
bgimg=cv2.imread('./media/bg.jpg')
while(1):
    cv2.imshow('maplaner',nowimg)
    if cv2.waitKey(100) & 0xFF == 27:
        if ls[-1][0]==4:
            break
        else:
            message_askyesno("错误", '没有降落指令，不能保存')
cv2.destroyAllWindows()           
if ls!=[]:
    #退出前预览指令
    timestring=str(getInput('最后一步','请输入文件名回车'))  
    namejpg='./map/'+'map_'+timestring+'.jpg'
    namecsv='./map/'+'map_'+timestring+'.csv'
    namecsvls='./map/'+'mapdraw_'+timestring+'.csv'
    cv2.imwrite(namejpg, nowimg)
    save=pd.DataFrame(lscom)
    save.to_csv(namecsv,header=['op','v1','v2','v3'],index=0)
    save2=pd.DataFrame(ls)#用来画图的
    save2.to_csv(namecsvls,header=['op','v1','v2','v3'],index=0)









    