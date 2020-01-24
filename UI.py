#根据opese的数据和tello的图像把画面显示出来添加紧急停机按钮
import cv2
import time
import winsound
import pygame

class FPS: #这个模块摘自tello_openpose
    def __init__(self):
        self.nbf=0
        self.fps=0
        self.start=0
        
    def update(self):
        if self.nbf%10==0:
            if self.start != 0:
                self.stop=time.time()
                self.fps=10/(self.stop-self.start)
                self.start=self.stop
            else :
                self.start=time.time()    
        self.nbf+=1
    
    def get(self):
        return self.fps

    def display(self, win, orig=(10,30), font=cv2.FONT_HERSHEY_PLAIN, size=2, color=(0,255,0), thickness=2):
        cv2.putText(win,f"FPS={self.get():.2f}",orig,font,size,color,thickness)

class Usercomd():#用户控制ui

    def __init__(self):
        self.pyg=pygame.init()
        self.screen = pygame.display.set_mode((640,480),0,32)

    def keyborad_read(self):
        key_list=self.pyg.key.get_pressed()
        kb=[0,0,0,0,0]#回中
        if key_list[self.pygame.K_UP]:
            kb[0]=50
        
        


        return kb
        #[0  1  2  3   4         5]
        #四个通道      ispose    模式

    def usec(self):
        kbs=self.keyborad_read


        return us
    #userc[0                1 2 3 4   5         ]
      #是否使用openpose    四个通道  模式

        
class player():

    def __init__(self):
        pass

    def sound(self,mode):
        if mode == 0:
            winsound.PlaySound('playsounds\\普通锁定.wav',winsound.SND_ALIAS)
        elif mode == 1:
            winsound.PlaySound('playsounds\\跟随模式.wav',winsound.SND_ALIAS)
        elif mode == 2:
            winsound.PlaySound('playsounds\\平行跟随.wav',winsound.SND_ALIAS)
        elif mode == 3:
            winsound.PlaySound('playsounds\\目标丢失.wav',winsound.SND_ALIAS)
        elif mode == 4:
            winsound.PlaySound('playsounds\\降落.wav',winsound.SND_ALIAS)
        elif mode == 5:
            winsound.PlaySound('playsounds\\即将降落.wav',winsound.SND_ALIAS)
        elif mode == 6:
            winsound.PlaySound('playsounds\\抛出即可飞行.wav',winsound.SND_ALIAS)
        elif mode == 7:
            winsound.PlaySound('playsounds\\起飞.wav',winsound.SND_ALIAS)
        elif mode == 8:
            winsound.PlaySound('playsounds\\紧急停机.wav',winsound.SND_ALIAS)
        elif mode == 9:
            winsound.PlaySound('playsounds\\拍照.wav',winsound.SND_ALIAS)
        elif mode == 10:
            winsound.PlaySound('playsounds\\起飞失败.wav',winsound.SND_ALIAS)
        elif mode == 11:
            winsound.PlaySound('playsounds\\起飞成功.wav',winsound.SND_ALIAS)
        elif mode == 12:
            winsound.PlaySound('playsounds\\退出平行跟随.wav',winsound.SND_ALIAS)
        elif mode == 13:
            winsound.PlaySound('playsounds\\退出跟随模式.wav',winsound.SND_ALIAS)
        elif mode == 14:
            winsound.PlaySound('playsounds\\接近中.wav',winsound.SND_ALIAS)
        elif mode == 15:
            winsound.PlaySound('playsounds\\低电量警报.wav',winsound.SND_ALIAS)  
            




class UID():#显示类

    def __init__(self):
        self.fps=FPS()

    def show(self,image,kp,flightstate):
        if kp==0:#两种显示模式
            image=self.hubw(image,flightdata)
            cv2.imshow('telloraw',image)
        else:
            self.drawer(image,kp)
            image=self.hubw(image,flightdata)
            image=cv2.resize(image,(960,720))
            cv2.imshow('tello',image)


    def drawer(self,image,kp):
        #画点
        for i in [0,1,2,3,4,5,6,7,8,17,18]:
            if k[i][0] and k[i][1]:
                cv2.circle(image, (kp[i][0], kp[i][1]), 3, (0, 0, 255), -1)
        #画线
        color=(0,255,0)
        thickness = 1
        lineType = 8
        linep=[[0,1],[0,18],[0,17],[1,2],[1,8],[1,5],[2,3],[3,4],[5,6],[6,7]]
        for i in range(len(linep)):
            x1=kp[linep[i][0]][0]
            y1=kp[linep[i][0]][1]
            x2=kp[linep[i][1]][0]
            y2=kp[linep[i][1]][1]
            if x1 and x2 and y1 and y2:
                cv.line(image, (x1, y1), (x2,y2 ), color, thickness, lineType)
        #这里有点绕，就是标记出线段的id然后遍历所有io带入对应的(x1,y1)(x2,y2)
    
    def hubw(self,image,flightdata):
        #这里摘自tello_openpose
        class hud:
            def __init__(self,def_color=(255,170,0)):
                self.def_color=def_color
            def add(self, info, color=None):
                if color is None: color = self.def_color
                self.infos.append((info, color))
            def draw(self, image):
                i=0
                for (info, color) in self.infos:
                    cv2.putText(image, info, (0, 30 + (i * 30)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1.0, color, 2) #lineType=30)
                    i+=1
        hub=hud()

        #self.state=[0,0,0,0,0,0,0,0,0,0]
        #是否飞行 电池 飞行模式  动作指令  油门 俯仰 副翼 偏航 锁定距离 实时距离
        hud.add(datetime.datetime.now().strftime('%H:%M:%S'))
        hud.add(f"FPS {self.fps.get():.2f}")
        if flightdata[0]!=0:
            hud.add(f"flying")
        else:
            hud.add(f"nofly}")
        hud.add(f"bat {flightstate[1]}")
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
        if flightdata[2]==0:
            hud.add(f"普通跟踪")
        elif flightdata[2]==1:
            hud.add(f"跟随模式")
        elif flightdata[2]==2:
            hud.add(f"平行跟随")
        elif flightdata[2]==3:
            hud.add(f"丢失目标")
        elif flightdata[2]==4:
            hud.add(f"降落")
        elif flightdata[2]==5:
            hud.add(f"手掌降落")
        elif flightdata[2]==6:
            hud.add(f"抛飞")
        elif flightdata[2]==7:
            hud.add(f"起飞")
        elif flightdata[2]==8:
            hud.add(f"紧急停机")
        #pose    0无操作
            #        1向前
            #        2向后
            #        3向左飘
            #        4向右
        if:
            hud.add(f"pose {flightstate[3]}")

        hud.add(f"thr {flightstate[4]}")
        hud.add(f"pith {flightstate[5]}")
        hud.add(f"roll {flightstate[6]}")
        hud.add(f"yaw {flightstate[7]}")
        hud.add(f"lockd {flightstate[8]}")
        hud.add(f"dist {flightstate[9]}")
       
        

        hud.draw(image)
        return image