from machine import Pin, SoftI2C
import time

i2c = SoftI2C(sda=Pin(4), scl=Pin(5), freq=100000)

ADDR = 0x29
CMD  = 0x80

ENABLE  = 0x00
ATIME   = 0x01
CONTROL = 0x0F
ID      = 0x12
CDATAL  = 0x14

PON = 0x01
AEN = 0x02

def w(reg, val):
    i2c.writeto_mem(ADDR, CMD | reg, bytes([val]))

def r(reg, n=1):
    return i2c.readfrom_mem(ADDR, CMD | reg, n)

def u16(reg):
    b = r(reg, 2)
    return b[0] | (b[1] << 8)

def init():
    print("scan:", [hex(a) for a in i2c.scan()])
    print("TCS ID:", hex(r(ID, 1)[0]))

    # 今の安定設定
    w(ATIME, 0xC0)      # ~154ms
    w(CONTROL, 0x02)    # 16x

    w(ENABLE, PON)
    time.sleep_ms(3)
    w(ENABLE, PON | AEN)
    time.sleep_ms(200)

def read_raw():
    c  = u16(CDATAL + 0)
    rr = u16(CDATAL + 2)
    g  = u16(CDATAL + 4)
    b  = u16(CDATAL + 6)
    return rr, g, b, c

# ---- 判定パラメータ（まずは仮） ----
C_MIN = 200
K_RG  = 1.25
K_BG  = 1.25

init()

while True:
    rr, g, b, c = read_raw()
    rn = rr / c if c else 0
    gn = g  / c if c else 0
    bn = b  / c if c else 0

    is_green = (c > C_MIN) and (gn > rn * K_RG) and (gn > bn * K_BG)
    label = "GREEN?" if is_green else "WHITE/OTHER"

    print(label,
          "| RAW", rr, g, b, c,
          "| NORM", round(rn,3), round(gn,3), round(bn,3),
          "| g/r", round(gn/rn, 2) if rn else 0,
          "| g/b", round(gn/bn, 2) if bn else 0)
    time.sleep_ms(200)
