# tello_the_force
使用“原力”控制tello
  
# 感谢
这个东东是基于 https://github.com/geaxgx/tello-openpose 开发的，重新设计了调用逻辑，使用了他的class FPS和class HUB（目前的进度），拆分出更多模块，后续可以更方便的开发出新模块（只需要修改com.py）
  
# 需要的库
参考tellostate.yaml      //conda 环境配置  
基于python3  
opencv-python  
pyAV    用于解码（后续考虑使用带gpu加速的）安装有坑需要ffmpeg，然后用conda安装  
tellopy  （这里使用geaxge修改过的版本，增加了throw_and_fly功能）  
numpy  
simple_pid  
argparse  
pygame  
openpose 用于检测关键点  
matplotlib  
pandas  
  
  
# 思路  
main.py  
    main里是一个循环，从tello回传的视频数据里解码出一帧画面，然后在循环里处理和显示，分别调用每一个模块的一个方法，实现一个功能  
tello.py  
    与tello无人机通讯的模块，处理指令和视频数据，更改这个模块可以控制其他种类的无人机  
pose.py  
    用来检测人体姿态的，调用openpose，获得关键点的坐标  
ui.py  
    显示模块  
com.py  
    获取姿态关键点坐标后进行判断决策，得到控制飞机的指令  
mapcom.py  
    航点飞行模块，获取飞机回传的位置信息，从文件读取航点规划文件，得到控制飞机的指令  
maplaner.py  
    用于规划航线，tello飞机只有xy和高度坐标，控制带gps模块的飞机时需要修改  
mapdrawer.py  
    将每一次航点飞行的轨迹画出来


  
# 现在的状态  
v3.20  
1.姿态跟踪  
这个是从geaxgx学来的，重新调整了代码结构（虽然性能没提升多少）  
    左右挥手控制前进后退以及roll方向  
    两只手组合动作切换飞行模式：普通跟踪，锁定距离，平行跟随  
    左右手靠近右左耳朵可以触发降落或手掌降落
上图：  
![pose](https://github.com/happyseayou/tello_the_force/tree/master/media/github/pose.png)   
  
2.键盘控制
键盘控制级别虽高，需要将鼠标焦点放在“没卵用窗口”上  
WSADQE控制前后左右等四个通道，shift ctrl控制上下  
12346789小键盘控制翻滚  
上下键控制起飞和降落，地图模式下是刷新起飞点和退出，（小问题，容易误触让飞机直接降落）  
f11 f12全屏和退出全屏  
m进入和退出map模式，b暂停map模式，t进入和退出pose模式  
上图：  
![inf](https://github.com/happyseayou/tello_the_force/tree/master/media/github/inf.png)  
  
3.map航点飞行  
基于飞机回传的mvo数据，精度还行，自动返航误差在30cm内  
上图：  
![map](https://github.com/happyseayou/tello_the_force/tree/master/media/github/map.png)  
  
可以将飞行后的轨迹画出来
上图：
![mapdrawer](https://github.com/happyseayou/tello_the_force/tree/master/media/github/mapdrawer.png)  
数据的存储格式：  
上图：  
![csv](https://github.com/happyseayou/tello_the_force/tree/master/media/github/csv.png)  
![pos](https://github.com/happyseayou/tello_the_force/tree/master/media/github/pos.png)  
  
  

# 存在问题  
1.性能问题：  
    pose模式下帧率低，只有9-10fps，显卡gtx970m 3g  
    map模式下，cpu占用达到60%，cpu i7 6700hq  
2.误触问题：  
    在map模式下，按键盘下键强制退出map模式时容易误触发降落  
3.人体姿态检测：  
    在人多的情况下，容易跟踪错人，目前没有找到解决方案  
4.pid问题：  
    pid的调节一直是个谜，每次调整都达不到要的效果  
  
  
  
  
# 关于openpose的安装：参照官网
https://github.com/CMU-Perceptual-Computing-Lab/openpose  
需要自行编译对应的cuda版本，或者其他版本，没有gpu不能做到实时，因为帧率只有1fps甚至更低
