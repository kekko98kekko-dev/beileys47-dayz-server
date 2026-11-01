#!/usr/bin/env python3
from v46_one_off_truck_and_loot_restart import can_restart
def main():
 assert can_restart("started",1,1)
 assert can_restart("started",1,0)
 assert can_restart("started",0,0)
 assert not can_restart("started",1,2)
 assert not can_restart("started",2,2)
 assert not can_restart("running",None,None)
 assert not can_restart("starting",1,1)
 assert can_restart("stopped",None,None)
 print("PASS V46 owner-authorized max one player, fail closed if player count increases")
if __name__=="__main__":main()
