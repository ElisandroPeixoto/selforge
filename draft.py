from sel_relays.sel700 import SEL700


relay = SEL700('10.82.125.105', level2=True)

relay.test_db_off()
relay.test_db_overview()
