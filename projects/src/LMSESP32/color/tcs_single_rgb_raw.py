from machine import Pin, SoftI2C
import time

i2c = SoftI2C(sda=Pin(4), scl=Pin(5), freq=100000)

ADDR = 0x29
CMD  = 0x80

# registers
ENABLE  = 0x00
ATIME   = 0x01
CONTROL = 0x0F
ID      = 0x12
CDATAL  = 0x14  # Clear, Red, Green, Blue (8 bytes)

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
    chip_id = r(ID, 1)[0]
    print("TCS ID:", hex(chip_id))

    # integration time ~50ms
    w(ATIME, 0xEB)
    # gain 4x
    w(CONTROL, 0x01)

    # power on -> enable ADC
    w(ENABLE, PON)
    time.sleep_ms(3)
    w(ENABLE, PON | AEN)
    time.sleep_ms(60)

def read_raw():
    c  = u16(CDATAL + 0)
    rr = u16(CDATAL + 2)
    g  = u16(CDATAL + 4)
    b  = u16(CDATAL + 6)
    return rr, g, b, c

init()

while True:
    rr, g, b, c = read_raw()
    rn = rr / c if c else 0
    gn = g  / c if c else 0
    bn = b  / c if c else 0
    print("RAW R,G,B,C =", rr, g, b, c, "| NORM", round(rn,3), round(gn,3), round(bn,3))
    time.sleep_ms(200)
