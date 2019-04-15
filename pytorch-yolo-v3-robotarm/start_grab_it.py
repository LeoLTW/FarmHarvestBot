from __future__ import division
import time
import torch 
import torch.nn as nn
from torch.autograd import Variable
import numpy as np
import cv2 
from util import *
from darknet import Darknet
from preprocess import prep_image, inp_to_image
import pandas as pd
import random 
import argparse
import pickle as pkl
import serial
from time import sleep
ser = serial.Serial("COM5", 9600, timeout=2)
def SerialWrite(command):
    ser.write(command)

def get_test_input(input_dim, CUDA):
    img = cv2.imread("imgs/messi.jpg")
    img = cv2.resize(img, (input_dim, input_dim)) 
    img_ =  img[:,:,::-1].transpose((2,0,1))
    img_ = img_[np.newaxis,:,:,:]/255.0
    img_ = torch.from_numpy(img_).float()
    img_ = Variable(img_)
    
    if CUDA:
        img_ = img_.cuda()
    
    return img_

def prep_image(img, inp_dim):
    """
    Prepare image for inputting to the neural network. 
    
    Returns a Variable 
    """

    orig_im = img
    dim = orig_im.shape[1], orig_im.shape[0]
    img = cv2.resize(orig_im, (inp_dim, inp_dim))
    img_ = img[:,:,::-1].transpose((2,0,1)).copy()
    img_ = torch.from_numpy(img_).float().div(255.0).unsqueeze(0)
    return img_, orig_im, dim

def write(x, img):
    c1 = tuple(x[1:3].int())
    c2 = tuple(x[3:5].int())
    cls = int(x[-1])
    label = "{0}".format(classes[cls])
    color = random.choice(colors)
    cv2.rectangle(img, c1, c2,color, 1)
    t_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_PLAIN, 1 , 1)[0]
    c2 = c1[0] + t_size[0] + 3, c1[1] + t_size[1] + 4
    cv2.rectangle(img, c1, c2,color, -1)
    cv2.putText(img, label, (c1[0], c1[1] + t_size[1] + 4), cv2.FONT_HERSHEY_PLAIN, 1, [225,255,255], 1);
    return img

def arg_parse():
    """
    Parse arguements to the detect module
    
    """
    
    
    parser = argparse.ArgumentParser(description='YOLO v3 Cam Demo')
    parser.add_argument("--confidence", dest = "confidence", help = "Object Confidence to filter predictions", default = 0.9)
    parser.add_argument("--nms_thresh", dest = "nms_thresh", help = "NMS Threshhold", default = 0.4)
    parser.add_argument("--reso", dest = 'reso', help = 
                        "Input resolution of the network. Increase to increase accuracy. Decrease to increase speed",
                        default = "672", type = str)
    return parser.parse_args()



if __name__ == '__main__':
    cfgfile = "cfg/yolov3_tiny.cfg"
    weightsfile = "yolov3_tiny_last.weights"
    num_classes = 5

    args = arg_parse()
    confidence = float(args.confidence)
    nms_thesh = float(args.nms_thresh)
    start = 0
    CUDA = torch.cuda.is_available()
    

    
    
    num_classes = 5
    bbox_attrs = 5 + num_classes
    
    model = Darknet(cfgfile)
    model.load_weights(weightsfile)
    
    model.net_info["height"] = args.reso
    inp_dim = int(model.net_info["height"])
    
    assert inp_dim % 32 == 0 
    assert inp_dim > 32

    if CUDA:
        model.cuda()
            
    model.eval()
    
    videofile = 'video.avi'
    
    cap = cv2.VideoCapture(0)
    
    assert cap.isOpened(), 'Cannot capture source'
    
    frames = 0
    start = time.time()    
    while cap.isOpened():
        
        ret, frame = cap.read()
        if ret:
            
            img, orig_im, dim = prep_image(frame, inp_dim)
            
            im_dim = torch.FloatTensor(dim).repeat(1,2)
            
            
            if CUDA:
                im_dim = im_dim.cuda()
                img = img.cuda()
            
            
            output = model(Variable(img), CUDA)
            output = write_results(output, confidence, num_classes, nms = True, nms_conf = nms_thesh)

            if type(output) == int:
                frames += 1
                print("FPS of the video is {:5.2f}".format( frames / (time.time() - start)))
                cv2.imshow("frame", orig_im)
                key = cv2.waitKey(1)
                if key & 0xFF == ord('q'):
                    break
                continue
            

        
            output[:,1:5] = torch.clamp(output[:,1:5], 0.0, float(inp_dim))/inp_dim
            
            im_dim = im_dim.repeat(output.size(0), 1)
            output[:,[1,3]] *= frame.shape[1]
            output[:,[2,4]] *= frame.shape[0]

            
            classes = load_classes('data/my_class.names')
            colors = pkl.load(open("pallete", "rb"))
            
            list(map(lambda x: write(x, orig_im), output))
            
            
            cv2.imshow("frame", orig_im)
            key = cv2.waitKey(1)
            if key & 0xFF == ord('q'):
                break
            frames += 1
            print("FPS of the video is {:5.2f}".format( frames / (time.time() - start)))
            #接下來是跟手臂的code
            coord_oringinal=[]#接輸出的list
            if type(output) != int:
                coord_oringinal.append(output[0][1])
                coord_oringinal.append(output[0][4])
                print(coord_oringinal)
        else:
            break

        if coord_oringinal != []:
            y_o=coord_oringinal[0]#偵測完的yolo y
            z_o=coord_oringinal[1]#偵測完的yolo z
            y_base=260#基準點的yolo y
            z_base=514#基準點的 yolo z
            y=(y_o-y_base)//1.215#換算成座標要加減的y
            if y>0:
                y=y+70#修正值
            y=int(y)
            z=-(z_o-z_base)//1.75#算成座標要加減的的z
            if z<100:
                z=z-166
            z=int(z)
            
            
            x1=200#固定x 的第一個座標
            x2=300#固定x 的第二個座標 要夾了
            bucket_coord_o = 'o:250,300,200'#桶子的座標 夾子開
            bucket_coord_c='c:250,300,200'#桶子的座標 夾子不開
            bucket_coord_dodge='c:150,300,100'#躲開板子
            coord_base='c:150,0,100'#基準點座標
            coord1='o:'+str(x1)+','+str(0+y)+','+str(100+z)
            coord2='o:'+str(x2)+','+str(0+y)+','+str(100+z)
            coord3='s:'+str(x2)+','+str(0+y)+','+str(100+z)
            coord4='c:'+str(x1)+','+str(0+y)+','+str(100+z)
            print(coord1)
            # 流程
            move=[coord_base,coord1,coord2,coord3,coord4,coord_base,bucket_coord_c,bucket_coord_o,bucket_coord_dodge,coord_base]
            for moving in move:
                Arduino_cmd = moving
                cmd = Arduino_cmd.encode("utf-8")
                SerialWrite(cmd)
                rv = ser.readline()
                print (rv) # Read the newest output from the Arduino
                print(rv.decode("utf-8"))
                sleep(2)  # Delay for one tenth of a second
                ser.flushInput()
