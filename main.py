#main函数，主循环代码放这里




def main():
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
        image = cv2.resize(image,(640,480))#这个太大会爆显存
       
        kp=pose.get_kp(image)
        comd=com.get_comd(kp)
        tello.send_comd(comd)
        flightstate=com.get_track_p()#命令状态
        flightdata=tello.send_data()#飞行数据
        ui.show(image,kp,flightstate,flightdata)
        cv2.imshow('Original', image)


        if frame.time_base < 1.0/60:
            time_base = 1.0/60
        else:
            time_base = frame.time_base
        frame_skip = int((time.time() - start_time)/time_base)

        