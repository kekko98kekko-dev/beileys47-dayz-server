#!/usr/bin/env python3
from v45_safe_loot_ttl import patch,LIFETIME,parse
def main():
 sample=b'''<types>
 <type name="BakedBeansCan"><nominal>20</nominal><lifetime>28800</lifetime><category name="food"/></type>
 <type name="M4A1"><nominal>5</nominal><lifetime>18000</lifetime><category name="weapons"/></type>
 <type name="WoodenCrate"><nominal>0</nominal><lifetime>3888000</lifetime><category name="tools"/></type>
 <type name="Barrel_Green"><nominal>40</nominal><lifetime>3888000</lifetime><category name="tools"/></type>
 <type name="MetalPlate"><nominal>20</nominal><lifetime>28800</lifetime><category name="tools"/></type>
 <type name="WoodenPlank"><nominal>30</nominal><lifetime>28800</lifetime><category name="tools"/></type>
 <type name="CarBattery"><nominal>40</nominal><lifetime>28800</lifetime><category name="tools"/></type>
 <type name="AliceBag_Green"><nominal>3</nominal><lifetime>28800</lifetime><category name="containers"/></type>
 <type name="Flag_Chernarus"><nominal>1</nominal><lifetime>28800</lifetime><category name="tools"/></type>
 <type name="TerritoryFlagKit"><nominal>0</nominal><lifetime>28800</lifetime><category name="tools"/></type>
 <type name="Food_Old"><nominal>4</nominal><lifetime>720000</lifetime><category name="food"/></type>
 </types>'''
 new,change=patch(sample)
 assert [x["name"] for x in change]==["BakedBeansCan","M4A1"]
 d=parse(new)
 assert d.find("type[@name='BakedBeansCan']").findtext("lifetime")=="14400"
 assert d.find("type[@name='WoodenCrate']").findtext("lifetime")=="3888000"
 assert d.find("type[@name='AliceBag_Green']").findtext("lifetime")=="28800"
 assert d.find("type[@name='Food_Old']").findtext("lifetime")=="720000"
 assert patch(new)[1]==[]
 print("PASS V45: cap ordinary abandoned loot to four hours, protect persistent/vehicle/base, idempotent")
if __name__=="__main__":main()
