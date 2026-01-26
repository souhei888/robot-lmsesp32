from machine import Pin, SoftI2C
"""
センサーチェックコード1
認識するピンを見つけるコード
pin32と33に接続しておく
鶴田君とチェック1/25日成功済み
"""

i2c2 = SoftI2C(sda=Pin(32), scl=Pin(33), freq=100000)
print("32/33:", [hex(a) for a in i2c2.scan()])

i2c2 = SoftI2C(sda=Pin(33), scl=Pin(32), freq=100000)
print("33/32:", [hex(a) for a in i2c2.scan()])