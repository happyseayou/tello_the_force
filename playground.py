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