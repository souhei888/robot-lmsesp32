from machine import Pin, SoftI2C, time_pulse_us
from pupremote import PUPRemoteSensor
import time

# -------------------------
# TCS34725 ドライバ（内蔵）
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
            print(f"[{name}] scan:", [hex(a) for a in self.i2c.scan()])
            sensor_id = self._r(ID, 1)[0]
            print(f"[{name}] TCS ID:", hex(sensor_id))
        except Exception as e:
            print(f"[{name}] init failed:", e)
            return False

        self._w(ATIME, 0xC0)      # ~154ms
        self._w(CONTROL, 0x02)    # 16x
        self._w(ENABLE, PON)
        time.sleep_ms(3)
        self._w(ENABLE, PON | AEN)
        time.sleep_ms(200)
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
        return (max(0, min(255, r8)),
                max(0, min(255, g8)),
                max(0, min(255, b8)))

# -------------------------
# I2C 2系統（そのまま）
# -------------------------
i2c1 = SoftI2C(sda=Pin(21), scl=Pin(22), freq=100000)  # Color1
i2c2 = SoftI2C(sda=Pin(33), scl=Pin(32), freq=100000)  # Color2

s1 = TCS34725(i2c1); s1.begin("S1")
s2 = TCS34725(i2c2); s2.begin("S2")

# -------------------------
# HC-SR04（TRIG/ECHO）
#  TRIG: GPIO13
#  ECHO: GPIO14  ※分圧して3.3Vへ
# -------------------------
TRIG_PIN = 13
ECHO_PIN = 14

trig = Pin(TRIG_PIN, Pin.OUT, value=0)
echo = Pin(ECHO_PIN, Pin.IN)

def hcsr04_mm(timeout_us=30000):
    """
    距離(mm)を返す。失敗時は 0 を返す。
    timeout_us: 反射待ちタイムアウト（30ms ≒ 約5m）
    """
    # トリガパルス 10us
    trig.off()
    time.sleep_us(2)
    trig.on()
    time.sleep_us(10)
    trig.off()

    # ECHO High の時間(μs)を取得
    dur = time_pulse_us(echo, 1, timeout_us)
    if dur < 0:
        return 0  # timeout 等

    # 距離換算：音速 343m/s → 0.343mm/us
    # 往復なので /2
    # mm = dur * 0.343 / 2 = dur * 0.1715
    mm = int(dur * 1715 // 10000)  # 0.1715 を整数演算で近似
    return mm

# -------------------------
# pupremote コマンド
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

def distance_mm(_):
    # 0〜65535に収める（to_hub_fmt="H"）
    d = hcsr04_mm()
    if d < 0:
        d = 0
    if d > 65535:
        d = 65535
    return d

p = PUPRemoteSensor(power=True, max_packet_size=16)
p.add_command("get_rgb1",    from_hub_fmt="b", to_hub_fmt="3B")
p.add_command("get_rgb2",    from_hub_fmt="b", to_hub_fmt="3B")
p.add_command("distance_mm", from_hub_fmt="b", to_hub_fmt="H")  # mm を返す

while True:
    p.process()
    time.sleep_ms(2)
