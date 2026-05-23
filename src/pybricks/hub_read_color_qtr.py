from pybricks.parameters import Port
from pybricks.tools import wait
from pupremote_hub import PUPRemoteHub

hub = PUPRemoteHub(Port.F, max_packet_size=16)

hub.add_command("rgb1", from_hub_fmt="b", to_hub_fmt="3B")
hub.add_command("rgb2", from_hub_fmt="b", to_hub_fmt="3B")
hub.add_command("qtr1", from_hub_fmt="b", to_hub_fmt="H")
hub.add_command("qtr2", from_hub_fmt="b", to_hub_fmt="H")

while True:
    r1, g1, b1 = hub.call("rgb1", 0)
    r2, g2, b2 = hub.call("rgb2", 0)
    v1 = hub.call("qtr1", 0)
    v2 = hub.call("qtr2", 0)

    print("C1:", r1, g1, b1, " C2:", r2, g2, b2, " Q1:", v1, " Q2:", v2)
    wait(100)  # 1msは速すぎるので100ms推奨
