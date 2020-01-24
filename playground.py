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


pygame.init()
screen = pygame.display.set_mode((640, 480), 0, 32)

video=cv2.VideoCapture(0)
flag=0
changetime=time.time()

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
        cv2.circle(frame, (320, 240), 10, (0, 0, 255), -1)
    elif key_list[pygame.K_DOWN]:
        cv2.circle(frame, (320, 240), 10, (0, 255, 0), -1)
    elif key_list[pygame.K_LEFT]:
        cv2.circle(frame, (320, 240), 10, (255, 0, 0), -1)
    elif key_list[pygame.K_RIGHT]:
        cv2.circle(frame, (320, 240), 10, (255, 255, 255), -1)
    pygame.display.update()
    cv2.imshow("raw",frame) 
    k = cv2.waitKey(1) & 0xff
    if k == 27 : break

video.release()
cv2.destroyAllWindows()