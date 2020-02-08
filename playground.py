import cv2
import numpy as np
import time
import pygame



def get_brightness(frame):
    frame= cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    per_image=[]
    per_image.append(np.mean(frame[0]))
    brightness=np.mean(per_image)
    return brightness


class player():
    def __init__(self):
        self.sound_mode_0 = pygame.mixer.Sound("playsounds\\普通锁定.wav")
        self.sound_mode_1 = pygame.mixer.Sound("playsounds\\跟随模式.wav")
        self.sound_mode_2 = pygame.mixer.Sound("playsounds\\平行跟随.wav")
        self.sound_mode_3 = pygame.mixer.Sound("playsounds\\目标丢失.wav")
        self.sound_mode_4 = pygame.mixer.Sound("playsounds\\降落.wav")
        self.sound_mode_5 = pygame.mixer.Sound("playsounds\\即将降落.wav")
        self.sound_mode_6 = pygame.mixer.Sound("playsounds\\抛出即可飞行.wav")
        self.sound_mode_7 = pygame.mixer.Sound("playsounds\\起飞.wav")

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
        elif mode == 7:
            self.sound_mode_7.play()
            
        


pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((640, 480), 0, 32)
video=cv2.VideoCapture(0)
flag=0
changetime=time.time()
player=player()
while True:
    ok,frame=video.read()
    brightness=get_brightness(frame)
    if brightness<60:
        if flag!=1:
            if time.time()-changetime>2:
                changetime=time.time()
                flag=1
                print('fly')
        elif  flag==1:
            if time.time()-changetime>2:
                changetime=time.time()
                print('land')
                flag=0      
    key_list = pygame.key.get_pressed()
    if key_list[pygame.K_UP]:
        player.sound(0)
    elif key_list[pygame.K_DOWN]:
        cv2.circle(frame, (320, 240), 40, (0, 255, 0), -1)
    elif key_list[pygame.K_LEFT]:
        cv2.circle(frame, (320, 240), 80, (255, 0, 0), -1)
    elif key_list[pygame.K_RIGHT]:
        cv2.circle(frame, (320, 240), 10, (255, 255, 255), -1)
    pygame.display.update()
    cv2.imshow("raw",frame) 
    k = cv2.waitKey(1) & 0xff
    if k == 27 : break

video.release()
cv2.destroyAllWindows()



"""
    if isdisplay==1:
        screen = pygame.display.set_mode((640, 480), pygame.DOUBLEBUF)#键盘控制封不了类，只能用函数
        pygame.display.set_caption('没卵用的窗口')
        #不会动的界面
        background=pygame.image.load('media//uimain.png')
        #俯仰滚
        roll=pygame.image.load('media//roll.png')
        rollrect=roll.get_rect()
        #电池速度高度
        heightp=pygame.image.load('media//h.png')
        betp=pygame.image.load('media//battery.png')
        velhp=pygame.image.load('media//velh.png')
        velxyp=pygame.image.load('media//velxy.png')
        #转盘
        yawp=pygame.image.load('media//yawpoint.png')
        yawprect=yawp.get_rect()
        #飞行模式和灯
        ready=pygame.image.load('media//ready.png')
        pl=pygame.image.load('media//pl.png')
        flying=pygame.image.load('media//visualfly.png')
        greenlight=pygame.image.load('media//greenlight.png')
        redlight=pygame.image.load('media//redlight.png')

    else:
        screen = pygame.display.set_mode((320, 240), 0, 32)#键盘控制封不了类，只能用函数
        pygame.display.set_caption('没卵用的窗口')
        background=pygame.image.load('media//tello background1.png')
"""


"""
            if isdisplay==1:
                #背景和画面
                imsf=pygdisplaycv2(image2surface)
                screen.blit(imsf,(0,0))
                screen.blit(background,(0,0))
                #滚动俯
                newroll=pygame.transform.rotate(roll,-(180/pi)*atan(flightstate[15]/5))#使用响应曲线放大
                newrect=newroll.get_rect(center=rollrect.center)
                screen.blit(newroll,(newrect[0]+264,newrect[1]+129-(366/pi)*atan(flightstate[16]/5)))#使用响应曲线放大
                #电池高度速度
                screen.blit(heightp,(5,319-abs(flightstate[11]*11)))
                screen.blit(betp,(575-(100-flightstate[1])*4,18))
                screen.blit(velhp,(611,283+int(flightstate[18]*4)))
                screen.blit(velxyp,(611,211-int(flightstate[17]*10)))
                #盘
                newyawp=pygame.transform.rotate(yawp,-flightstate[24])
                newyawprect=newyawp.get_rect(center=yawprect.center)
                screen.blit(newyawp,(newyawprect[0]+74,newyawprect[1]+368))#使用响应曲线放大
                #飞行模式和灯
                if flightstate[0]!=0:#飞行中
                    if flightstate[25]==6:
                        screen.blit(flying,(13,10))
                    elif flightstate[25]==1:
                        screen.blit(pl,(23,11))
                    #灯
                    screen.blit(greenlight,(601,6))
                else:
                    if flightstate[25]==6:
                        screen.blit(ready,(17,8))
                    elif flightstate[25]==1:
                        screen.blit(pl,(23,11))
                    screen.blit(redlight,(601,6))

                pygame.display.update()
                #pygame.display.flip() 
            else:
                screen.blit(background,(0,0))
                pygame.display.update()
"""