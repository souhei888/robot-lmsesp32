from pybricks.hubs import PrimeHub
from pybricks.parameters import Port
from pybricks.pupdevices import Motor
from pybricks.tools import wait, StopWatch
from pupremote_hub import PUPRemoteHub

prime = PrimeHub()
remote = PUPRemoteHub(Port.F, max_packet_size=16)

mL = Motor(Port.C)
mR = Motor(Port.D)

remote.add_command("rgb1", from_hub_fmt="b", to_hub_fmt="3B")
remote.add_command("rgb2", from_hub_fmt="b", to_hub_fmt="3B")
remote.add_command("qtr1", from_hub_fmt="b", to_hub_fmt="H")
remote.add_command("qtr2", from_hub_fmt="b", to_hub_fmt="H")

def as_int(x):
    if x is None:
        return None
    if isinstance(x, (tuple, list)):
        if len(x) == 0:
            return None
        x = x[0]
    if isinstance(x, (bytes, bytearray)):
        return None
    try:
        return int(x)
    except:
        return None

def read_qtr():
    try:
        l = remote.call("qtr1", 0)
        r = remote.call("qtr2", 0)
    except:
        prime.speaker.beep(200, 50)
        return None, None

    l2 = as_int(l)
    r2 = as_int(r)
    if l2 is None or r2 is None:
        prime.speaker.beep(200, 20)
        return None, None

    return l2, r2


def read_qtr_avg(n=3):
    sL = 0
    sR = 0
    ok = 0
    for _ in range(n):
        l, r = read_qtr()
        if l is None or r is None:
            wait(2)
            continue
        sL += l
        sR += r
        ok += 1
        wait(2)
    if ok == 0:
        return None, None
    return sL // ok, sR // ok

def clamp(x, lo, hi):
    return lo if x < lo else hi if x > hi else x
# ---- helpers ----
def norm(x, mn, mx):
    if x is None or mx <= mn + 5:
        return None
    x = clamp(x, mn, mx)
    return int((x - mn) * 1000 / (mx - mn))

# ---- manual calibration (10s) ----
prime.speaker.beep(800, 200)
wait(300)

minL, minR = 4095, 4095
maxL, maxR = 0, 0
sw = StopWatch()

sw.reset()
cal_ms = 10000  # 10秒：白と黒を交互に踏ませる
while sw.time() < cal_ms:
    l, r = read_qtr_avg(3)
    if l is None or r is None:
        continue
    if l < minL: minL = l
    if r < minR: minR = r
    if l > maxL: maxL = l
    if r > maxR: maxR = r
    wait(10)

# キャリブ結果を音で知らせる（OK=高音、NG=低音）
rangeL = maxL - minL
rangeR = maxR - minR
if rangeL >= 200 and rangeR >= 200:
    prime.speaker.beep(1200, 200)
else:
    prime.speaker.beep(200, 400)  # rangeが小さい

# ---- control ----
base = 35
Kp = 0.08
Kd = 0.03
last_error = 0
last_dir = 1

while True:
    rawL, rawR = read_qtr_avg(3)
    if rawL is None or rawR is None:
        prime.speaker.beep(200, 50)
        wait(20)
        continue

    nL = norm(rawL, minL, maxL)
    nR = norm(rawR, minR, maxR)
    if nL is None or nR is None:
        # キャリブが死んでる時は安全に停止
        mL.dc(0); mR.dc(0)
        prime.speaker.beep(200, 100)
        wait(100)
        continue

    # 見失い：両方かなり白寄り（上側）
    if nL > 900 and nR > 900:
        forward = 25
        turn = 12 * last_dir
        left  = int(clamp(forward - turn, 0, 100))
        right = int(clamp(forward + turn, 0, 100))
        mL.dc(left); mR.dc(right)
        wait(10)
        continue

    error = nL - nR
    deriv = error - last_error
    last_error = error

    if error > 80:
        last_dir = -1
    elif error < -80:
        last_dir = 1

    corr = Kp * error + Kd * deriv
    corr = clamp(corr, -20, 20)

    left  = int(clamp(base - corr, 0, 100))
    right = int(clamp(base + corr, 0, 100))

    mL.dc(left); mR.dc(right)
    wait(10)
