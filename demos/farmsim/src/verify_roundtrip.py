from pathlib import Path
import json
root=Path(__file__).resolve().parent
env={'__file__':str(root/'verify.py')}
exec((root/'verify.py').read_text(),env)
exec('''
def cross():
 place(503 if get('area')==0 else 9,152)
 frame(1 if get('area')==0 else 2);assert get('loading');finish_transition()
def plant(wet):
 return_plot();tool(0);tap(128);tool(2);tap(128)
 if wet:tool(1);tap(128)
frame();plant(True);assert state(3)==3
cross();plant(False);assert state(3)==2
cross();assert state(3)==3;sleep_home();assert state(3)==4
cross();assert state(3)==2
return_plot();tool(1);tap(128);cross();sleep_home()
assert state(3)==4,'unwatered sprout must wait'
cross();assert state(3)==4
return_plot();tool(1);tap(128);cross()
return_plot();tool(1);tap(128);sleep_home();assert state(3)==5
cross();assert state(3)==5
return_plot();tap(128);assert get('harvest')==1
cross();return_plot();tap(128);assert get('harvest')==2
place(232,152,1);frame();tap(128);finish_transition();assert get('room')==2
place(120,104,1);frame();put('moneylo',10);put('moneyhi',0);tap(128);assert get('dialogue')==3
seed_before=get('seeds');tap(128);assert get('moneylo')==8 and get('seeds')==seed_before+1
tap(64);leave_room();assert get('moneylo')==8
assert maxnmi<2273 and maxmain+maxnmi<29780
report={'result':'PASS','frames':frames,'max_nmi_cycles_including_dma':maxnmi,'max_main_cycles':maxmain,'checks':['edge exits both directions','watered versus dry crops across inactive fields','rewatering sprouts','harvest in both fields','shop purchase and exit'],'limitations':'6502 model with simplified PPU; Mesen visual and actual save-state testing remain open'}
(P/'roundtrip_validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
''',env)
