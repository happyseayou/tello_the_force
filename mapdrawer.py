import matplotlib as matlab
from mpl_toolkits.mplot3d import Axes3D
import numpy as np 
import matplotlib.pyplot as plt
from tkinter import *
import tkinter.filedialog
import os
import pandas as pd 

root = tkinter.Tk()    
root.withdraw()       
path=tkinter.filedialog.askopenfile(title=u'选择航点数据')

read=pd.read_csv(path)
print(read)
data=read.values.tolist()
data=np.array(data)

#np.around(data,decimals=4)
#data = np.random.rand(10000,4)
x=data[:, 1]
y=data[:, 2]
z=data[:, 3]

matlab.rcParams['legend.fontsize']=10
fig=plt.figure()
ax=fig.gca(projection='3d')
ax.set_xlabel('x')  
ax.set_ylabel('y') 
ax.set_zlabel('z')
ax.plot(x, y, z,'g-',label='Air flight')

ax.legend()

plt.show()