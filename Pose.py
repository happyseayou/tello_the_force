#op class，调用openpose用于分析每一帧图像，获得图像身体节点坐标

import sys
import cv2
import os
from sys import platform
import argparse
#from tello import *
from UI import FPS
from math import atan2, degrees, sqrt,pi



#导入openpos库
dir_path = os.path.dirname(os.path.realpath(__file__))
try:
    if platform == "win32":
        #对于windows系统导入dll库
        sys.path.append(dir_path+'./../python/openpose/Release');    #路径根据文件所在位置
        os.environ['path'] = os.environ['path'] + ';' +dir_path + './../x64/Release;'+ dir_path +'./../bin;'
        #上面路径需要根据openpose文件夹的位置来决定
        import pyopenpose as op
    else:
        #不是windows系统则使用python文件夹里的pyd
        sys.path.append('../python');
        from openpose import pyopenpose as op
except ImportError as e:
     print('Error: OpenPose library could not be found. Did you enable `BUILD_PYTHON` in CMake and have this Python script in the right folder?')
     raise e

def angle(A,B,C):
    if A[0] is None or B[0] is None or C[0] is None:
        return None
    dg=degrees(atan2(C[1]-B[1],C[0]-B[0]) - atan2(A[1]-B[1],A[0]-B[0]))%360
    if dg>=180 and dg<360:
        dg=360-dg
    return dg
        


class Pose:


    def __init__(self):
        parser = argparse.ArgumentParser()
        #parser.add_argument("--image_path", default="./media/COCO_val2014_000000000192.jpg", help="Process an image. Read all standard formats (jpg, png, bmp, etc.).")
        args = parser.parse_known_args()

        params=dict()
        params["model_folder"]='./../models/'#具体情况
        params["number_people_max"] = 1
        params["model_pose"] = "BODY_25"

        # Add others in path?
        for i in range(0, len(args[1])):
            curr_item = args[1][i]
            if i != len(args[1])-1: next_item = args[1][i+1]
            else: next_item = "1"
            if "--" in curr_item and "--" in next_item:
                key = curr_item.replace('-','')
                if key not in params:  params[key] = "1"
            elif "--" in curr_item and "--" not in next_item:
                key = curr_item.replace('-','')
                if key not in params: params[key] = next_item


        #初始化openpose
        self.opWrapper = op.WrapperPython()
        self.opWrapper.configure(params)
        self.opWrapper.start()
        self.datum = op.Datum()

    def get_kp(self,frame):#返回坐标点的方法返回的是二维数组
        self.datum.cvInputData=frame
        self.opWrapper.emplaceAndPop([self.datum])
        #out = self.datum.cvOutputData
        
        kps = self.datum.poseKeypoints[0]
        listid=[0,1,2,3,4,5,6,7,8,10,17,18]#body_25模型关键点
            #
        #添加一组获取图片亮度listid[10]
        #brightness=self.framebightness(frame)
        xy=[[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0]]
        for i in listid:
            x,y,conf = kps[i]
            if x!=0 or y!=0:   #允许一个为0，不允许都为0
                xy[i][0]=int(x)
                xy[i][1]=int(y)
            else:
                xy[i][0]=None       
                xy[i][1]=None 
            if i==10:
                xy[i][0]=xy[i][1]=brightness
        return xy   #xy[i][k]i代表第几个点k代表第几个坐标
    
    #def framebightness(self.frame):#获取图片亮度


        
        




#读取摄像头测试
if __name__=='__main__':

    video=cv2.VideoCapture(0)
    
    fps=FPS()
    my_pose=Pose()
    while True:
        ok,frame=video.read()
        if not ok:
            break
        fps.update()
        #frame=cv2.imread("./123.jpg") 
        frame2=frame
        #cv2.imshow("raw",frame)   
        show=my_pose.get_kp(frame)
        #print(show[7])
        
        angle234=angle((show[2][0],show[2][1]),(show[3][0],show[3][1]),(show[4][0],show[4][1]))
        angle567=angle((show[7][0],show[7][1]),(show[6][0],show[6][1]),(show[5][0],show[5][1]))
        #if angle567:
        print(str(angle234)+' '+str(angle567))
        #else:
          #  print('ooooops')
        if show[2][0]:#值判断一个就好
            cv2.circle(frame2, (show[2][0], show[2][1]), 3, (0, 0, 255), -1)
        if show[3][0]:
            cv2.circle(frame2, (show[3][0], show[3][1]), 3, (0, 0, 255), -1)
        if show[4][0]:
            cv2.circle(frame2, (show[4][0], show[4][1]), 3, (0, 0, 255), -1)
        if show[5][0]:#值判断一个就好
            cv2.circle(frame2, (show[5][0], show[5][1]), 3, (0, 0, 255), -1)
        if show[6][0]:
            cv2.circle(frame2, (show[6][0], show[6][1]), 3, (0, 0, 255), -1)
        if show[7][0]:
            cv2.circle(frame2, (show[7][0], show[7][1]), 3, (0, 0, 255), -1)
        
        #cv2.putText(frame2, 'love you', (show[0]-70,show[1]), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)
        fps.display(frame2)
        frame3=cv2.resize(frame2,(960,720))
        cv2.imshow("raw",frame3) 
        #cv2.imshow("1",show[2])
        #print(show[0][0],show[0][1])
        #print('ok')
        k = cv2.waitKey(1) & 0xff
        if k == 27 : break
    video.release()
    cv2.destroyAllWindows()
