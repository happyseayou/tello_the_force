#main函数，主循环代码放这里




def main():
    usercomd=Usercomd()#用户命令，从键盘键入进行飞行
    tello=Tello()
    pose=Pose()
    com=Com()
    ui=UID()
    

    frame_skip=300
    for frame in tello.container.decode(video=0):#一定要用这个循环来获取才不会产生delay
        if 0 < frame_skip:
            frame_skip = frame_skip - 1
            continue
        start_time = time.time()
        image = cv2.cvtColor(numpy.array(frame.to_image()), cv2.COLOR_RGB2BGR)
        imageraw=image
        image = cv2.resize(image,(640,480))#这个太大会爆显存
        userc=usercomd.usec()#来自用户输入的命令
        #userc[0                1 2 3 4   5         ]
            #是否使用openpose    四个通道  模式
        if userc[0]==1:#判断
            kp=pose.get_kp(image)
        else:#不使用
            kp=[[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0]]
        comd=com.get_comd(kp,userc)#接受两个数组进行判断
        tello.send_comd(comd)
        flightdata=tello.send_data()#飞行数据
        com.read_tello_data(flightdata)#飞控获取数据用于判断指令
        flightstate=com.get_state()#命令状态
        if userc[0]==1:#使用
            ui.show(image,kp,flightstate)#显示并负责播放声音
        else:#不用
            ui.show(imageraw,0,flightstate)
        


        if frame.time_base < 1.0/60:
            time_base = 1.0/60
        else:
            time_base = frame.time_base
        cv2.waitKey(1)
        frame_skip = int((time.time() - start_time)/time_base)

        