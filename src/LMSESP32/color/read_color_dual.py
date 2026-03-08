from machine import Pin, SoftI2C
from pupremote import PUPRemoteSensor
import time

# -------------------------
# TCS34725 ドライバ（この中に内蔵：ファイル分割しない版）
# -------------------------
TCS_ADDR = 0x29
CMD = 0x80

ENABLE  = 0x00
ATIME   = 0x01
CONTROL = 0x0F
ID      = 0x12
CDATAL  = 0x14

PON = 0x01
AEN = 0x02

class TCS34725:
    def __init__(self, i2c, addr=TCS_ADDR):
        self.i2c = i2c
        self.addr = addr

    def _w(self, reg, val):
        self.i2c.writeto_mem(self.addr, CMD | reg, bytes([val]))

    def _r(self, reg, n=1):
        return self.i2c.readfrom_mem(self.addr, CMD | reg, n)

    def _u16(self, reg):
        b = self._r(reg, 2)
        return b[0] | (b[1] << 8)

    def begin(self, name="S"):
        try:
            scan = [hex(a) for a in self.i2c.scan()]
            print(f"[{name}] scan:", scan)
        except Exception as e:
            print(f"[{name}] scan failed:", e)
            return False

        try:
            sensor_id = self._r(ID, 1)[0]
            print(f"[{name}] TCS ID:", hex(sensor_id))
        except Exception as e:
            print(f"[{name}] ID read failed:", e)
            return False

        # 安定設定（あなたが使っていた値）
        try:
            self._w(ATIME, 0xC0)      # ~154ms
            self._w(CONTROL, 0x02)    # 16x
            self._w(ENABLE, PON)
            time.sleep_ms(3)
            self._w(ENABLE, PON | AEN)
            time.sleep_ms(200)
        except Exception as e:
            print(f"[{name}] init write failed:", e)
            return False

        return True

    def read_raw(self):
        c  = self._u16(CDATAL + 0)
        r  = self._u16(CDATAL + 2)
        g  = self._u16(CDATAL + 4)
        b  = self._u16(CDATAL + 6)
        return r, g, b, c

    def get_rgb8(self):
        r, g, b, c = self.read_raw()
        if not c:
            return (0, 0, 0)
        r8 = int(r * 255 / c)
        g8 = int(g * 255 / c)
        b8 = int(b * 255 / c)
        r8 = max(0, min(255, r8))
        g8 = max(0, min(255, g8))
        b8 = max(0, min(255, b8))
        return (r8, g8, b8)

# -------------------------
# I2C 2系統（確定版）
# -------------------------
i2c1 = SoftI2C(sda=Pin(21), scl=Pin(22), freq=100000)  # Sensor1
i2c2 = SoftI2C(sda=Pin(33), scl=Pin(32), freq=100000)  # Sensor2（←33/32が正解）

s1 = TCS34725(i2c1)
s2 = TCS34725(i2c2)

print("init s1:", s1.begin("S1"))
print("init s2:", s2.begin("S2"))

# -------------------------
# pupremote
# -------------------------
def get_rgb1(_):
    try:
        return s1.get_rgb8()
    except Exception:
        return (0, 0, 0)

def get_rgb2(_):
    try:
        return s2.get_rgb8()
    except Exception:
        return (0, 0, 0)

p = PUPRemoteSensor(power=True, max_packet_size=16)
p.add_command("get_rgb1", from_hub_fmt="b", to_hub_fmt="3B")
p.add_command("get_rgb2", from_hub_fmt="b", to_hub_fmt="3B")

while True:
    p.process()
    time.sleep_ms(2)
