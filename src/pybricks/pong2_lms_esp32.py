from pybricks.parameters import Port
from pybricks.tools import wait
from pupremote_hub import PUPRemoteHub

hub = PUPRemoteHub(Port.F, max_packet_size=16)
hub.add_command("ping", from_hub_fmt="b", to_hub_fmt="4s")

while True:
    print(hub.call("ping", 1))  # b'pong' が返る
    wait(500)
