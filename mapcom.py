class Mapcom:
    def __init__(self):
        self.nowpos=[0,0,0]#x,y,z
        self.nextpos=[0,0,0]
        


    def do(self):
        
        

        return comd
    def get_acc(self):#获取修正量，包括距离，角度，和高度
        self.distance=sqrt((self.nowpos[0]-self.nextpos[0])**2+(self.nextpos[1]**2+self.nowpos[1]**2))
        self.dheight=self.nextpos[3]-self.nextpos[3]
        #角度这个有点麻烦，解算四元数可得
        #dangler=nextposangler-90+yaw0   
        self.dangler=self.nextposangler-90+self.yaw0


    def get_map(self):

    def save_map(self):

    def getpos(self,flightstate):
        self.nowpos=
        self.nextposangler=#下一个点的与x正方向的夹角
        self.yaw0=

    def computing(self):


