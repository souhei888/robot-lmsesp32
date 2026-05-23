from pybricks.parameters import Port
from pybricks.tools import wait
from pupremote_hub import PUPRemoteHub

hub = PUPRemoteHub(Port.F, max_packet_size=16)
hub.add_command("rgb", from_hub_fmt="b", to_hub_fmt="3B")

while True:
    r, g, b = hub.call("rgb", 0)
    print(r, g, b)
    wait(100)
