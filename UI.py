#根据opese的数据和tello的图像把画面显示出来添加紧急停机按钮
import cv2
import time

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


class UID():

    def __init__(self):
        self.fps=FPS()

    def show(self,image,kp,flightstate,flightdata):
        self.drawer(image,kp)
        image=self.hubw(image,flightdata,flightdata)
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
    
    def hubw(self,image,flightdata,flightstate):
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

        #flightdata[] 0=battary 1=flymode 3=timer
        #flightstate[]  还没定义因为com模块还没写
        #后面完善add()
        hud.add(datetime.datetime.now().strftime('%H:%M:%S'))
        hud.add(f"FPS {self.fps.get():.2f}")
        hud.add(f"BAT {flightdata[0]}")

        hud.draw(image)
        return image