from time import sleep
import serial


ser = serial.Serial("COM5", 9600, timeout=2)
def SerialWrite(command):
    ser.write(command)

#ex=['c:150,0,100',
#'o:150,-225,200',
#'o:250,-225,200',
#'s:250,-225,200',
#'c:150,-225,200',
#'c:200,0,100',
#'c:250,175,200',
#'o:250,175,200',
#'c:200,0,100']
while 1:
#for i in ex:
    Arduino_cmd =input("座標:")
    cmd = Arduino_cmd.encode("utf-8")
    SerialWrite(cmd)
    rv = ser.readline()
    # print (rv) # Read the newest output from the Arduino
    print (rv.decode("utf-8"))
    sleep(2.5)  # Delay for one tenth of a second
    ser.flushInput()
