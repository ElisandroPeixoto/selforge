from sel_relays.sel700 import SEL700


relay = SEL700('10.82.125.104')

map = relay.read_dnpmap()

print(map)
