#根据opese的数据和tello的图像把画面显示出来添加紧急停机按钮
import cv2
import time

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


class player():
    def __init__(self):
        #pose下
        self.sound_mode_0 = pygame.mixer.Sound("playsounds\\普通锁定.wav")
        self.sound_mode_1 = pygame.mixer.Sound("playsounds\\跟随模式.wav")
        self.sound_mode_2 = pygame.mixer.Sound("playsounds\\平行跟随.wav")
        self.sound_mode_3 = pygame.mixer.Sound("playsounds\\目标丢失.wav")
        self.sound_mode_4 = pygame.mixer.Sound("playsounds\\降落.wav")
        self.sound_mode_5 = pygame.mixer.Sound("playsounds\\接近中.wav")
        self.sound_mode_6 = pygame.mixer.Sound("playsounds\\抛出即可飞行.wav")
        #self.sound_mode_7 = pygame.mixer.Sound("playsounds\\起飞.wav")
        #键盘操作下
        self.key_mode_8=pygame.mixer.Sound("playsounds\\起飞.wav")#起飞
        self.key_mode_9=self.sound_mode_6#抛飞
        self.key_mode_10=pygame.mixer.Sound("playsounds\\手掌降落.wav")
        self.key_mode_11=self.sound_mode_4
        #键盘下，翻滚动作
        self.key_mode_12=pygame.mixer.Sound("playsounds\\前空翻.wav")
        self.key_mode_13=pygame.mixer.Sound("playsounds\\后空翻.wav")
        self.key_mode_14=pygame.mixer.Sound("playsounds\\左空翻.wav")
        self.key_mode_15=pygame.mixer.Sound("playsounds\\右空翻.wav")
        self.key_mode_16=pygame.mixer.Sound("playsounds\\左前空翻.wav")
        self.key_mode_17=pygame.mixer.Sound("playsounds\\右前空翻.wav")
        self.key_mode_18=pygame.mixer.Sound("playsounds\\左后空翻.wav")
        self.key_mode_19=pygame.mixer.Sound("playsounds\\右后空翻.wav")
        




    def sound(self,mode):
        if mode == 0:
            self.sound_mode_0.play()
        elif mode == 1:
            self.sound_mode_1.play()
        elif mode == 2:
            self.sound_mode_2.play()
        elif mode == 3:
            self.sound_mode_3.play()
        elif mode == 4:
            self.sound_mode_4.play()
        elif mode == 5:
            self.sound_mode_5.play()
        elif mode == 6:
            self.sound_mode_6.play()
        #key mode
        elif mode == 7:
            pass
        elif mode == 8:
            self.key_mode_8.play()
        elif mode == 9:
            self.key_mode_9.play()
        elif mode == 10:
            self.key_mode_10.play()
        elif mode == 11:
            self.key_mode_11.play()
        elif mode == 12:
            self.key_mode_12.play()
        elif mode == 13:
            self.key_mode_13.play()
        elif mode == 14:
            self.key_mode_14.play()
        elif mode == 15:
            self.key_mode_15.play()
        elif mode == 16:
            self.key_mode_16.play()
        elif mode == 17:
            self.key_mode_17.play()
        elif mode == 18:
            self.key_mode_18.play()
        elif mode == 19:
            self.key_mode_19.play()
        

class UID():#显示类

    def __init__(self):
        self.fps=FPS()
        self.player=player()
        self.preflightstate2=-1
        #self.hubw=hubw()

    def show(self,image,kp,flightstate):
        if kp==0:#两种显示模式
            image=self.hubw(image,flightstate)
            self.player.sound(flightstate[2])
            self.fps.update()
            #cv2.imshow('tello',image)
        else:
            self.drawer(image,kp,flightstate)
            image=cv2.resize(image,(960,720))
            image=self.hubw(image,flightstate)
            if flightstate[2]!=self.preflightstate2:#判断当前模式是否与先前的不一样
                self.player.sound(flightstate[2])#只有不一样才可以播放声音，不然一直叫个不停
                self.preflightstate2=flightstate[2]
            self.fps.update()
        cv2.imshow('tello',image)


    def drawer(self,image,kp,flightstate):
        #画点
        for i in [0,1,2,3,4,5,6,7,8,17,18]:
            if kp[i][0] and kp[i][1]:
                cv2.circle(image, (kp[i][0], kp[i][1]), 3, (0, 0, 255), -1)
        #画线
        color=(0,255,0)
        thickness = 3
        lineType = 8
        linep=[[0,1],[0,18],[0,17],[1,2],[1,8],[1,5],[2,3],[3,4],[5,6],[6,7]]
        for i in range(len(linep)):
            x1=kp[linep[i][0]][0]
            y1=kp[linep[i][0]][1]
            x2=kp[linep[i][1]][0]
            y2=kp[linep[i][1]][1]
            if x1 and x2 and y1 and y2:
                cv2.line(image, (x1, y1), (x2,y2 ), color, thickness, lineType)
        #这里有点绕，就是标记出线段的id然后遍历所有io带入对应的(x1,y1)(x2,y2)
        #以下是跟踪箭头部分
        x11=320#起点
        y11=240
        x22=flightstate[13]#终点kp
        y22=flightstate[14]
        if x11 and x22 and y11 and y22:
            cv2.arrowedLine(image, (x11,y11), (x22,y22), (0,0,255),5,8,0,0.1)
            cv2.circle(image, (x11,y11), 7, (0, 255, 255), -1)
            cv2.circle(image, (x22,y22), 7, (255, 0, 255), -1)

    def hubw(self,image,flightstate):
        #这里摘自tello_openpose
        class HUD: 
            def __init__(self, def_color=(255, 170, 0)):
                self.def_color = def_color
                self.infos = []
            def add(self, info, color=None):
                if color is None: color = self.def_color
                self.infos.append((info, color))
            def draw(self, frame):
                i=0
                for (info, color) in self.infos:
                    cv2.putText(frame, info, (0, 30 + (i * 30)),cv2.FONT_HERSHEY_SIMPLEX,1.0, color, 2) #lineType=30)
                    i+=1

        hud=HUD()

        #self.state=[0,0,0,0,0,0,0,0,0,0]
        #是否飞行 电池 飞行模式  动作指令  油门 俯仰 副翼 偏航 锁定距离 实时距离
        #hud.add(datetime.datetime.now().strftime('%H:%M:%S'))
        if self.fps.get():
            hud.add(f"FPS {self.fps.get():.2f}")
        if flightstate[0]!=0:
            hud.add("flying", (0,255,0))
        else:
            hud.add("nofly", (0,255,0))
        if flightstate[1]<20:
            hud.add(f"bat {flightstate[1]}% battary low",(0,0,255))#低电量
        else:
            hud.add(f"bat {flightstate[1]}%")
        
        #flymode 0普通跟踪，只修正偏航
        #        1跟随模式，修正偏航和锁定距离
        #        2平行跟随，修正roll和锁定距离
        #        3丢失目标，保持高度，同时旋转寻找目标，如果超过15秒则降落
        #        4降落，所有参数清零
        #        5靠近降落在手掌，所有参数清零
        #        6抛飞，
        if flightstate[2]==0:
            hud.add("normal tracking", (0,255,0))
        elif flightstate[2]==1:
            hud.add("tracking mode", (0,255,0))
        elif flightstate[2]==2:
            hud.add("parallox mode", (0,255,0))
        elif flightstate[2]==3:
            hud.add("target lose", (0,255,0))
        elif flightstate[2]==4:
            hud.add("land", (0,255,0))
        elif flightstate[2]==5:
            hud.add("palm land", (0,255,0))
        elif flightstate[2]==6:
            hud.add("throw and go", (0,255,0))
        elif flightstate[2]==8:
            hud.add("takeoff", (0,255,0))
        elif flightstate[2]==9:
            hud.add("throw and go", (0,255,0))
        elif flightstate[2]==10:
            hud.add("palm land", (0,255,0))
        elif flightstate[2]==11:
            hud.add("land", (0,255,0))
        elif flightstate[2]==12:
            hud.add("flip forward", (0,255,0))
        elif flightstate[2]==13:
            hud.add("flip back", (0,255,0))
        elif flightstate[2]==14:
            hud.add("flip left", (0,255,0))
        elif flightstate[2]==15:
            hud.add("flip right", (0,255,0))
        elif flightstate[2]==16:
            hud.add("flip forward left", (0,255,0))
        elif flightstate[2]==17:
            hud.add("flip forward right", (0,255,0))
        elif flightstate[2]==18:
            hud.add("flip back left", (0,255,0))
        elif flightstate[2]==19:
            hud.add("flip back right", (0,255,0))
        
        
        #pose    0无操作
            #        1向前
            #        2向后
            #        3向左飘
            #        4向右
        if flightstate[3]==0:
            hud.add("pose :normal", (0,255,0))
        elif flightstate[3]==1:
            hud.add("pose :forward", (0,255,0))
        elif flightstate[3]==2:
            hud.add("pose :backward", (0,0,255))
        elif flightstate[3]==3:
            hud.add("pose :left roll", (0,255,0))
        elif flightstate[3]==4:
            hud.add("pose :right roll", (0,255,0))
        else:
            hud.add("data error!")
        hud.add(f"thr {flightstate[4]}")
        hud.add(f"pith {flightstate[5]}")
        hud.add(f"roll {flightstate[6]}")
        hud.add(f"yaw {flightstate[7]}")
        hud.add(f"lockd {flightstate[8]}")
        hud.add(f"dist {flightstate[9]}")
        hud.add(f"throw and go timer {flightstate[10]}")
        hud.add(f"height {flightstate[11]}")
        hud.add(f"velxy {flightstate[17]:8.1f}")
        hud.add(f"velz {flightstate[18]:8.1f}")
        #hud.add(f"anglerroll {flightstate[15]:8.1f}")
        #hud.add(f"anglerpitch {flightstate[16]:8.1f}")
        hud.add(f"wifi {flightstate[12]:8.1f}")
        hud.add(f"posx {flightstate[19]:8.1f}")
        hud.add(f"posy {flightstate[20]:8.1f}")
        hud.add(f"posz {flightstate[21]:8.1f}")
        #hud.add(f"zero pitch {flightstate[22]:8.1f}")#四元数解算的旋转是与启动点为原点的，可用于定位
        #hud.add(f"zero roll {flightstate[23]:8.1f}")
        hud.add(f"zero yew {flightstate[24]:8.1f}")
        hud.add(f"visualstate {flightstate[25]}")
        #print(f"posx {flightstate[19]:8.1f},visualstate {flightstate[25]}")
        
        hud.draw(image)
        return image