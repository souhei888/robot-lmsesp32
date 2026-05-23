from pybricks.parameters import Port
from pybricks.tools import wait
from pybricks.iodevices import PUPDevice
from pupremote_hub import PUPRemoteHub

PORT = Port.F

# デバイスが見えるまで待つ
for i in range(40):  # 20秒
    try:
        print("PUPDevice OK:", PUPDevice(PORT).info())
        break
    except OSError:
        print("waiting device...", i)
        wait(500)
else:
    raise OSError("Still ENODEV: device not detected")

hub = PUPRemoteHub(PORT, max_packet_size=16)
hub.add_command("ping", from_hub_fmt="b", to_hub_fmt="b")

while True:
    # まずは小さい値で
    print("ret=", hub.call("ping", 7))
    wait(500)
