from pupremote import PUPRemoteSensor

def ping(_):
    return b"pong"   # 4 bytes

p = PUPRemoteSensor(power=True, max_packet_size=16)
p.add_command("ping", from_hub_fmt="b", to_hub_fmt="4s")

while True:
    p.process()
