from pupremote import PUPRemoteSensor
import color

def rgb(_):
    r, g, b = color.get_rgb()
    r = max(0, min(255, int(r)))
    g = max(0, min(255, int(g)))
    b = max(0, min(255, int(b)))
    return r, g, b

p = PUPRemoteSensor(power=True, max_packet_size=16)
p.add_command("rgb", from_hub_fmt="b", to_hub_fmt="3B")  # ★3文字ならOK

while True:
    p.process()
