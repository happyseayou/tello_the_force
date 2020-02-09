#根据opese的数据和tello的图像把画面显示出来添加紧急停机按钮
import cv2
import time
import numpy
import pygame
from math import atan2, degrees, sqrt,pi,atan
import csv


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


class Pydisplay():
    def __init__(self):
        self.isdisplay=1
        pygame.init()
        pygame.mixer.init()
        self.player=player()
        self.preflightstate2=-1

        if self.isdisplay==1:
            self.screen = pygame.display.set_mode((640, 480), pygame.DOUBLEBUF)#键盘控制封不了类，只能用函数
            #self.screen = pygame.display.set_mode((640, 480), 0)#键盘控制封不了类，只能用函数
            pygame.display.set_caption('没卵用的窗口')
            #不会动的界面
            self.background=pygame.image.load('media//uimain.png')
            #俯仰滚
            self.roll=pygame.image.load('media//roll.png')
            self.rollrect=self.roll.get_rect()
            #电池速度高度
            self.heightp=pygame.image.load('media//h.png')
            self.betp=pygame.image.load('media//battery.png')
            self.velhp=pygame.image.load('media//velh.png')
            self.velxyp=pygame.image.load('media//velxy.png')
            #转盘
            self.yawp=pygame.image.load('media//yawpoint.png')
            self.yawprect=self.yawp.get_rect()
            #飞行模式和灯
            self.ready=pygame.image.load('media//ready.png')
            self.pl=pygame.image.load('media//pl.png')
            self.flying=pygame.image.load('media//visualfly.png')
            self.greenlight=pygame.image.load('media//greenlight.png')
            self.redlight=pygame.image.load('media//redlight.png')

        else:
            self.screen = pygame.display.set_mode((320, 240), 0, 32)#键盘控制封不了类，只能用函数
            self.pygame.display.set_caption('没卵用的窗口')
            self.background=pygame.image.load('media//tello background1.png')

    def pygdisplaycv2(self,imsurface):
        #将cv2 frame做一个pygame surface
        imsurface=cv2.resize(imsurface,(640,480))
        imsurface=numpy.rot90(imsurface,k=-1)
        imsf=pygame.surfarray.make_surface(imsurface)
        imsf = pygame.transform.flip(imsf, False, True)
        return imsf

    def display(self,image2surface,flightstate):
        if self.isdisplay==1:
            #背景和画面
            imsf=self.pygdisplaycv2(image2surface)
            self.screen.blit(imsf,(0,0))
            self.screen.blit(self.background,(0,0))
            #滚动俯
            newroll=pygame.transform.rotate(self.roll,-(180/pi)*atan(flightstate[15]/5))#使用响应曲线放大
            newrect=newroll.get_rect(center=self.rollrect.center)
            self.screen.blit(newroll,(newrect[0]+264,newrect[1]+129-(366/pi)*atan(flightstate[16]/5)))#使用响应曲线放大
            #电池高度速度
            self.screen.blit(self.heightp,(5,319-abs(flightstate[11]*11)))
            self.screen.blit(self.betp,(575-(100-flightstate[1])*4,18))
            self.screen.blit(self.velhp,(611,283+int(flightstate[18]*4)))
            self.screen.blit(self.velxyp,(611,211-int(flightstate[17]*10)))
            #盘
            newyawp=pygame.transform.rotate(self.yawp,-flightstate[24])
            newyawprect=newyawp.get_rect(center=self.yawprect.center)
            self.screen.blit(newyawp,(newyawprect[0]+74,newyawprect[1]+368))#使用响应曲线放大
            #飞行模式和灯
            if flightstate[0]!=0:#飞行中
                if flightstate[25]==6:
                    self.screen.blit(self.flying,(13,10))
                elif flightstate[25]==1:
                    self.screen.blit(self.pl,(23,11))
                #灯
                self.screen.blit(self.greenlight,(601,6))
            else:
                if flightstate[25]==6:
                    self.screen.blit(self.ready,(17,8))
                elif flightstate[25]==1:
                    self.screen.blit(self.pl,(23,11))
                self.screen.blit(self.redlight,(601,6))

            if flightstate[2]!=self.preflightstate2:#判断当前模式是否与先前的不一样
                self.player.sound(flightstate[2])#只有不一样才可以播放声音，不然一直叫个不停
                self.preflightstate2=flightstate[2]

            pygame.display.update()
            #pygame.display.flip() 
        else:
            self.screen.blit(self.background,(0,0))
            pygame.display.update()


class Keyuser():
    def __init__(self):
        self.ispose=0
        self.isposetime=time.time()
        self.us=[0,0,0,0,0,0]

    def usec(self,key_list):#定义键盘跟踪，暂时没有封转到类
        speed=50
        for i in [0,1,2,3,5]:
            self.us[i]=0
        if key_list[pygame.K_w]:#W 前进
            self.us[1]=speed
        if key_list[pygame.K_s]:#s后退
            self.us[1]=-speed
        if key_list[pygame.K_q]:#q
            self.us[2]=-speed
        if key_list[pygame.K_e]:#e
            self.us[2]=speed
        if key_list[pygame.K_a]:#a
            self.us[3]=-speed
        if key_list[pygame.K_d]:#d
            self.us[3]=speed
        if key_list[pygame.K_LSHIFT]:#shitf
            self.us[0]=speed
        if key_list[pygame.K_LCTRL]:#ctrl
            self.us[0]=-speed
        #ispose
        if key_list[pygame.K_t]:
            if self.ispose !=1:
                if time.time()-self.isposetime>2:
                    self.ispose=1
                    self.us[4]=self.ispose
                    self.isposetime=time.time() 
                    
            else:
                if  time.time()-self.isposetime>2:
                    self.ispose=0
                    self.us[4]=self.ispose
                    self.isposetime=time.time()
        #全屏切换
        if key_list[pygame.K_F11]:
            pygame.display.set_mode((640, 480), pygame.DOUBLEBUF)
        if key_list[pygame.K_F12]:
            pygame.display.set_mode((640, 480), pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)
        #特殊指令执行时通道指令无效且归零
        if key_list[pygame.K_0]:#0
            self.us[5]=2
            self.us[0]=self.us[1]=self.us[2]=self.us[3]=0
            
        if key_list[pygame.K_9]:#退出
            self.us[5]=3
            self.us[0]=self.us[1]=self.us[2]=self.us[3]=0
            
        
        elif key_list[pygame.K_UP]:#up
            #四通道值刷为0
            self.us[5]=1
            self.us[0]=self.us[1]=self.us[2]=self.us[3]=0
            
        elif key_list[pygame.K_DOWN]: #down
            #四通道值刷为0
            self.us[5]=4
            self.us[0]=self.us[1]=self.us[2]=self.us[3]=0

        elif key_list[pygame.K_SPACE]:#space紧急停机
            pass
            #四个通道刷为0
            #[0  1  2  3   4         5]
            #四个通道   ispose    模式
            #油 pitch roll yaw ispose   模式 0   1   2     3         4             
        #shift w     e    a    t          无  起飞 抛飞  降落  手掌降落  
        #ctrl  s    q    d    t              up down   0         0   
        
        #八向翻滚：5  6 7 8  9 10  11 12 
        #对应键位  8  2 4 6  7  9  1  3
        elif key_list[pygame.K_KP8]:
            self.us[5]=5
            self.us[0]=self.us[1]=self.us[2]=self.us[3]=0
        elif key_list[pygame.K_KP2]:
            self.us[5]=6
            self.us[0]=self.us[1]=self.us[2]=self.us[3]=0
        elif key_list[pygame.K_KP4]:
            self.us[5]=7
            self.us[0]=self.us[1]=self.us[2]=self.us[3]=0
        elif key_list[pygame.K_KP6]:
            self.us[5]=8
            self.us[0]=self.us[1]=self.us[2]=self.us[3]=0
        elif key_list[pygame.K_KP7]:
            self.us[5]=9
            self.us[0]=self.us[1]=self.us[2]=self.us[3]=0
        elif key_list[pygame.K_KP9]:
            self.us[5]=10
            self.us[0]=self.us[1]=self.us[2]=self.us[3]=0
        elif key_list[pygame.K_KP1]:
            self.us[5]=11
            self.us[0]=self.us[1]=self.us[2]=self.us[3]=0
        elif key_list[pygame.K_KP3]:
            self.us[5]=12
            self.us[0]=self.us[1]=self.us[2]=self.us[3]=0
        return self.us


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
        
        #PID记录
        self.pidt=0
        if self.pidt:
            self.pidfile=open('pid.csv','w',encoding='utf-8',newline='')
            self.pidfilewrite=csv.writer(self.pidfile)
            self.pidfilewrite.writerow(["mode","lock","dis","x","y"])

    def show(self,image,kp,flightstate):
        if kp==0:#两种显示模式
            image=self.hubw(image,flightstate)
            #frame2=image
            self.fps.update()
            #cv2.imshow('tello',image)
        else:
            self.drawer(image,kp,flightstate)
            #frame2=image
            image=cv2.resize(image,(960,720))
            image=self.hubw(image,flightstate)
            self.fps.update()
            #PID调节文件
            if self.pidt:
                self.pidfilewrite.writerow([flightstate[2],flightstate[8],flightstate[9],flightstate[13],flightstate[14]])
        cv2.imshow('tello',image)
        
        return image
        #self.write(self.stack,frame2)
        


    def drawer(self,image,kp,flightstate):
        #画点
        #for i in [0,1,2,3,4,5,6,7,8,17,18]:
            #if kp[i][0] and kp[i][1]:
                #cv2.circle(image, (kp[i][0], kp[i][1]), 3, (0, 0, 255), -1)
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