from pybricks.hubs import PrimeHub
from pybricks.parameters import Port
from pybricks.pupdevices import Motor
from pybricks.tools import wait, StopWatch
from pupremote_hub import PUPRemoteHub

hub = PrimeHub()

mL = Motor(Port.C)
mR = Motor(Port.D)

remote = PUPRemoteHub(Port.F, max_packet_size=16)

remote.add_command("rgb1", from_hub_fmt="b", to_hub_fmt="3B")
remote.add_command("rgb2", from_hub_fmt="b", to_hub_fmt="3B")
remote.add_command("qtr1", from_hub_fmt="b", to_hub_fmt="H")
remote.add_command("qtr2", from_hub_fmt="b", to_hub_fmt="H")

def read_qtr():
    l = remote.call("qtr1", 0)
    r = remote.call("qtr2", 0)
    return l, r

def clamp(x, lo, hi):
    return lo if x < lo else hi if x > hi else x

def normalize(v, vmin, vmax):
    if vmax <= vmin + 10:
        return 0.5
    x = (v - vmin) / (vmax - vmin)
    return clamp(x, 0.0, 1.0)

# -------------------------
# Calibration: min/max
# -------------------------
hub.speaker.beep(1000, 100)
wait(200)

sw = StopWatch()
cal_ms = 6000

minL, minR = 4095, 4095
maxL, maxR = 0, 0

print("CALIBRATION:", cal_ms, "ms")
sw.reset()
while sw.time() < cal_ms:
    l, r = read_qtr()
    if l < minL: minL = l
    if r < minR: minR = r
    if l > maxL: maxL = l
    if r > maxR: maxR = r
    wait(10)

rangeL = maxL - minL
rangeR = maxR - minR
print("minL,maxL =", minL, maxL, " minR,maxR =", minR, maxR)
print("rangeL, rangeR =", rangeL, rangeR)

if rangeL < 300 or rangeR < 300:
    print("Calibration failed")
    hub.speaker.beep(200, 800)
    while True:
        wait(100)

hub.speaker.beep(1500, 100)
wait(200)

# -------------------------
# Main loop（とりあえず値を見るだけ）
# -------------------------
while True:
    rawL, rawR = read_qtr()
    nL = normalize(rawL, minL, maxL)
    nR = normalize(rawR, minR, maxR)
    print(rawL, rawR, " -> ", round(nL,2), round(nR,2))
    wait(200)
