import os
import cv2
import gc
import time
from multiprocessing import Process, Manager
 
 
# 向共享缓冲栈中写入数据:
def write(stack, cam, top: int) -> None:
    print('Process to write: %s' % os.getpid())
    cap = cv2.VideoCapture(cam)
    while True:
        _, img = cap.read()
        if _:
            stack.append(img)
            # 每到一定容量清空一次缓冲栈
            # 利用gc库，手动清理内存垃圾，防止内存溢出
            if len(stack) >= top:
                del stack[:]
                gc.collect()
 
 
# 在缓冲栈中读取数据:
def read(stack) -> None: #提醒返回值是一个None
    print('Process to read: %s' % os.getpid())
    index = 0
    fourcc = cv2.VideoWriter_fourcc(*'avc1')   #MPEG-4.2q
    
 
 
    out = cv2.VideoWriter('video_out.mp4',fourcc , 25, (640, 480))
 
    start_time = time.time()
    x = 1  # displays the frame rate every 1 second
    counter = 0
 
    print("开始逐帧读取")
    while True:
        # print("正在读取第%d帧：" %index)s
        if len(stack) >= 10:
            frame = stack.pop()
 
            # 逐帧保存为图片
            # resize_frame = cv2.resize(frame, (720, 480), interpolation=cv2.INTER_AREA)
            # cv2.imwrite("frame" + "%03d.jpg" % index,resize_frame )
            index = index+1
 
            #直接保存视频
            out.write(frame)
            cv2.imshow("img", frame)
 
            #计算fps
            counter += 1
            if (time.time() - start_time) > x:
 
                print("FPS: ", counter / (time.time() - start_time))
                counter = 0
                start_time = time.time()
 
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
        else:
            continue
    out.release()
    cv2.destroyAllWindows()
 
if __name__ == '__main__':
    # 父进程创建缓冲栈，并传给各个子进程：
    q = Manager().list()
    pw = Process(target=write, args=(q, 0, 100)) #海康威视视频流地址
    pr = Process(target=read, args=(q,))
    pw.start()
    pr.start()
 
    pr.join()
 
    pw.terminate()
