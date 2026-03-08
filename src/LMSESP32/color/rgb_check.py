from pupremote import PUPRemoteSensor
from servo import Servo
from machine import Pin, SoftI2C
import time
import utime

#--- 1. サーボ設定 ---
sv = Servo(21, min_pulse=518, max_pulse=2510, min_angle=0, max_angle=360)
sv2 = Servo(22, min_pulse=518, max_pulse=2510, min_angle=0, max_angle=360)

#コマンド名と一致させる
def servo(v):
    sv.angle(v)

def sv2(v): # servo2からsv2に変更(3文字)
    sv2.angle(v)

#--- 2. カラーセンサー設定 ---
i2c = SoftI2C(sda=Pin(27), scl=Pin(26), freq=100000)
try:
    i2c.writeto_mem(0x29, 0x80, bytes([0x03]))
    time.sleepms(500)
except:
    print("Sensor not found")

def rgb():
    try:
        data = i2c.readfrom_mem(0x29, 0x94, 8) 
        c = data[0] | (data[1] << 8)
        r = data[2] | (data[3] << 8)
        g = data[4] | (data[5] << 8)
        b = data[6] | (data[7] << 8)
        if c == 0: return 0, 0, 0
        return int(r255/c), int(g255/c), int(b*255/c)
    except:
        return 0, 0, 0

#--- 3. PUPRemote 通信設定 ---
p = PUPRemoteSensor(power=True)

#すべて5文字以内に設定
p.add_command('servo', '', 'h') 
p.add_command('sv2', '', 'h')   # 名前を短くしました
p.add_command('rgb', 'b', '3B') 

#--- 4. メインループ ---
while True:
    p.process()
    utime.sleep_ms(5)
