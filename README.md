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
open pose 用于检测关键点  

# 思路
tello从tello获取图像信息传给pose得到人的姿态关键点，然后这些关键点数据经过com的控制逻辑产生命令通过tello发送给飞机实现各种操作，图像和飞行数据和操控数据通过ui显示处理  
com.py  
一个飞行模式的组成：  
1.特定的pose激活  
2.对应的锁定策略  
3.丢失模式等级高  
4.起飞模式等级最高  
5.降落完成之后重置所有参数  
6.接受和发送state数据和遥测信号  
7.最后发送一帧所对应的指令comd[]  
mapcom.py  
  
  

  

# 现在的状态
目前完成了第一个版本，实现了用键盘控制和身体姿态控制的目标，pygame的一个窗口还没设计，在细节的判断上需要优化，pid与容错
![效果](https://github.com/happyseayou/tello_the_force/blob/master/performcetest/nopose.jpg)
![打开pose](https://github.com/happyseayou/tello_the_force/blob/master/performcetest/pose.jpg)
![调用没有pose](https://github.com/happyseayou/tello_the_force/blob/master/performcetest/resultmain.png)
![调用pose](https://github.com/happyseayou/tello_the_force/blob/master/performcetest/resultmainpose.png)
![cpu内存](https://github.com/happyseayou/tello_the_force/blob/master/performcetest/cpuram.jpg)
![显存](https://github.com/happyseayou/tello_the_force/blob/master/performcetest/gpu.jpg)

# 存在问题
pose调用摄像头进行检测的时候fps有20fps左右（i7 6700hq + gtx970m 3g+16gb ram+512gb nvme ssd）
是调用了tello的摄像头检测的fps只有6fps这给pid正常运行造成很大麻烦，阶跃曲线很迷，目前只能通过限制舵量来防止震荡，目前测试的结论是fps跟显存频率和显卡频率有巨大的关系，嗯，不管主循环的操作有多复杂，而且tellopy获取视频的时候有丢帧策略设置太小可以提高帧率但是会造成延迟，后续看看能不能换上更快的解码器来提高解码速度降低丢帧，com的决策可能逻辑存在漏洞，目前还没开发完，搞得有点掉发，因为要理清好多层的if-elif--。。。。。，还要有应对错误的机制（在class pose.check_pose）没有把键盘控制封装成类


# 关于openpose的安装：参照官网
https://github.com/CMU-Perceptual-Computing-Lab/openpose  
需要自行编译对应的cuda版本，或者其他版本，没有gpu不能做到实时，因为帧率只有1fps甚至更低
