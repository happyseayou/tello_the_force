import time


class Com:
    def __init__(self):
        pass

    def get_comd(self,userc):
        comd=[0,0,0,0,0]#每轮循环都回中 
        #拷贝命令，命令来自ui.py的class Usercomd
        comd[0]=userc[3]
        comd[1]=userc[2]
        comd[2]=userc[1]
        comd[3]=userc[0]

        comd[4]=userc[5] 
        return comd
        #comd[0] comd[1] comd[2]  comd[3]  comd[4]
        #旋转     左右    前后      上下     特殊命令