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


if __name__=='__main__':
    video=cv2.VideoCapture(0)
    
    fps=FPS()
    
    while True:
        ok,frame=video.read()
        if not ok:
            break
        fps.update()
        #frame=cv2.imread("./123.jpg") 
    
        #cv2.imshow("raw",frame)   
        
        fps.display(frame)
        
        cv2.imshow("raw",frame) 
        #cv2.imshow("1",show[2])
        #print(show[0][0],show[0][1])
        #print('ok')
        k = cv2.waitKey(1) & 0xff
        if k == 27 : break
    video.release()
    cv2.destroyAllWindows()