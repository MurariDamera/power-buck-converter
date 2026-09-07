from pathlib import Path
import re, uuid, json, math, csv
import pcbnew as p

ROOT=Path(__file__).parent
LIB=Path(r'C:\Program Files\KiCad\10.0\share\kicad')
NAME='Buck_Converter'
def uid(s): return str(uuid.uuid5(uuid.NAMESPACE_URL,'buck-converter/'+s))
def q(s): return json.dumps(str(s))
def block(s,start):
    depth=0; quoted=False; esc=False
    for i in range(start,len(s)):
        c=s[i]
        if quoted:
            if esc: esc=False
            elif c=='\\': esc=True
            elif c=='"': quoted=False
        elif c=='"': quoted=True
        elif c=='(': depth+=1
        elif c==')':
            depth-=1
            if depth==0: return s[start:i+1]
def children(s,key):
    pat='('+key+' '; out=[]; pos=0
    while (pos:=s.find(pat,pos))>=0:
        b=block(s,pos);out.append(b);pos+=len(b)
    return out
def symbol(lib,name):
    s=(LIB/'symbols'/f'{lib}.kicad_sym').read_text(encoding='utf-8')
    b=block(s,s.index('(symbol '+q(name)+'\n'))
    ext=re.search(r'\(extends "([^"]+)"\)',b)
    if ext:
        base=symbol(lib,ext[1])
        for prop in children(b,'property'):
            key=re.match(r'\(property "([^"]+)"',prop)[1]
            old=next((v for v in children(base,'property') if v.startswith('(property '+q(key)+' ')),None)
            if old: base=base.replace(old,prop)
        b=base.replace(ext[1],name)
    return b

TO='Package_TO_SOT_THT:TO-220-5_P3.4x3.7mm_StaggerOdd_Lead3.8mm_Vertical'
TERM='TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal'
parts=[
 ('U1','Regulator_Switching:LM2596T-5','LM2596T-5',TO,105.41,76.2,0,{'1':'VIN','2':'SW','3':'GND','4':'+5V','5':'GND'}),
 ('J1','Connector_Generic:Conn_01x02','12V INPUT',TERM,40.64,73.66,180,{'1':'VIN','2':'GND'}),
 ('C1','Device:C_Polarized','680uF / 35V','Capacitor_THT:CP_Radial_D10.0mm_P5.00mm',60.96,88.9,0,{'1':'VIN','2':'GND'}),
 ('C2','Device:C','100nF / 50V','Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm',78.74,88.9,0,{'1':'VIN','2':'GND'}),
 ('D1','Device:D_Schottky','1N5822','Diode_THT:D_DO-201AD_P15.24mm_Horizontal',132.08,88.9,270,{'1':'SW','2':'GND'}),
 ('L1','Device:L','33uH / Isat >= 3.5A','Inductor_THT:L_Radial_D12.5mm_P7.00mm_Fastron_09HCP',149.86,78.74,90,{'1':'SW','2':'+5V'}),
 ('C3','Device:C_Polarized','220uF / 25V','Capacitor_THT:CP_Radial_D8.0mm_P3.50mm',170.18,88.9,0,{'1':'+5V','2':'GND'}),
 ('J2','Connector_Generic:Conn_01x02','5V OUTPUT',TERM,193.04,78.74,0,{'1':'+5V','2':'GND'}),
]
for i in range(4):
    parts.append((f'H{i+1}','Mechanical:MountingHole','M3 mounting hole','MountingHole:MountingHole_3.2mm_M3',43.18+i*20.32,165.1,0,{}))
symdefs={}
for _,libid,*_ in parts:
    lib,name=libid.split(':');symdefs[libid]=symbol(lib,name).replace('(symbol '+q(name),'(symbol '+q(libid),1)
for name in ['PWR_FLAG','GND']:
    symdefs['power:'+name]=symbol('power',name).replace('(symbol '+q(name),'(symbol '+q('power:'+name),1)
s=[f'(kicad_sch (version 20250114) (generator "eeschema") (uuid {q(uid("sheet"))}) (paper "A4")',
 '(title_block (title "12 V to 5 V Buck Converter") (date "2026-09-05") (rev "1.0") (comment 1 "Based on Buck Converter - KiCad Design Guide") (comment 2 "LM2596 fixed 5 V | 150 kHz | Prototype"))',
 '(lib_symbols '+'\n'.join(symdefs.values())+')']
pinpos={}
def place(ref,libid,value,fp,x,y,ang,nets):
    s.append(f'(symbol (lib_id {q(libid)}) (at {x} {y} {ang}) (unit 1) (in_bom {"no" if ref.startswith(("#","H")) else "yes"}) (on_board yes) (dnp no) (uuid {q(uid(ref))})')
    for key,val,px,py,hide in [('Reference',ref,x,y-8,ref.startswith('#')),('Value',value,x,y-5.5,ref.startswith('#')),('Footprint',fp,x,y,True)]:
        if ref=='D1' and key in ['Reference','Value']:px=x+8;py=y+(-1.27 if key=='Reference' else 1.27)
        if ref=='U1' and key in ['Reference','Value']:py-=2
        s.append(f'(property {q(key)} {q(val)} (at {px} {py} {90 if ang in [90,270] else 0}) (effects (font (size 1.27 1.27)) {"(hide yes)" if hide else ""}))')
    b=symdefs[libid];a=math.radians(ang)
    for pb in children(b,'pin'):
        num=re.search(r'\(number "([^"]+)"',pb)[1]
        at=re.search(r'\(at ([-\d.]+) ([-\d.]+)',pb)
        px,py=map(float,at.groups())
        pinpos[ref,num]=(round(x+px*math.cos(a)-py*math.sin(a),4),round(y-px*math.sin(a)-py*math.cos(a),4))
        s.append(f'(pin {q(num)} (uuid {q(uid(ref+"/"+num))}))')
    s.append(f'(instances (project {q(NAME)} (path {q("/"+uid("sheet"))} (reference {q(ref)}) (unit 1)))))')
for part in parts: place(*part)
wi=0
def wire(*pts):
    global wi
    for a,b in zip(pts,pts[1:]):
        if a==b: continue
        wi+=1;s.append(f'(wire (pts (xy {a[0]} {a[1]}) (xy {b[0]} {b[1]})) (stroke (width 0) (type default)) (uuid {q(uid("wire"+str(wi)))}))')
def label(name,pt):
    s.append(f'(label {q(name)} (at {pt[0]} {pt[1]} 0) (effects (font (size 1.27 1.27)) (justify left bottom)) (uuid {q(uid(name+str(pt)))}))')
def junction(pt):
    s.append(f'(junction (at {pt[0]} {pt[1]}) (diameter 0) (color 0 0 0 0) (uuid {q(uid("j"+str(pt)))}))')
# Input rail and capacitor bank.
wire(pinpos['J1','1'],(60.96,73.66),(78.74,73.66),pinpos['U1','1']);label('VIN',(60.96,73.66))
for ref in ['C1','C2']:
    px=pinpos[ref,'1'][0];wire((px,73.66),pinpos[ref,'1']);junction((px,73.66))
# Output switch, catch diode and LC filter.
wire(pinpos['U1','2'],(132.08,78.74),pinpos['L1','1']);label('SW',(124.46,78.74))
wire((132.08,78.74),pinpos['D1','1']);junction((132.08,78.74))
wire(pinpos['L1','2'],(170.18,78.74),pinpos['J2','1']);label('+5V',(175.26,78.74))
wire((170.18,78.74),pinpos['C3','1']);junction((170.18,78.74))
wire(pinpos['U1','4'],(121.92,73.66),(121.92,60.96),(170.18,60.96),(170.18,78.74))
# Common ground rail, with explicit junctions.
gxs=[45.72,60.96,78.74,88.9,105.41,132.08,170.18,185.42]
wire(*[(x,106.68) for x in gxs]);label('GND',(60.96,106.68))
wire(pinpos['J1','2'],(48.26,71.12),(48.26,99.06),(45.72,99.06),(45.72,106.68))
for ref in ['C1','C2','D1','C3']:
    pt=pinpos[ref,'2'];wire(pt,(pt[0],106.68));junction((pt[0],106.68))
wire(pinpos['U1','5'],(88.9,78.74),(88.9,106.68));junction((88.9,106.68))
wire(pinpos['U1','3'],(105.41,106.68));junction((105.41,106.68))
wire(pinpos['J2','2'],(185.42,81.28),(185.42,106.68))
place('#FLG01','power:PWR_FLAG','PWR_FLAG','',60.96,73.66,0,{})
place('#FLG02','power:PWR_FLAG','PWR_FLAG','',105.41,106.68,0,{})
place('#PWR01','power:GND','GND','',105.41,106.68,0,{})
for i,(txt,x,y,size) in enumerate([
 ('12 V NOMINAL INPUT',37,53,1.8),('FIXED 5 V / 150 kHz',96,45,2),('FILTERED 5 V OUTPUT',159,53,1.8),
 ('C1 = Cin; C2 = optional Cin2; C3 = Cout in the source guide.',38,124,1.27),
 ('Prototype for 12 V input. The 35 V input capacitor does NOT support a 40 V input rating.',38,129,1.27),
 ('3 A is a design target: qualify diode, inductor saturation, capacitor ESR/ripple and U1 heatsink.',38,134,1.27),
 ('D1: cathode (band) to SW. U1 pin 5 to GND enables operation. FB senses after L1.',38,139,1.27),
 ('Footprint dimensions must match purchased parts. No adjustable-output divider is fitted.',38,144,1.27)]):
    s.append(f'(text {q(txt)} (at {x} {y} 0) (effects (font (size {size} {size})) (justify left)) (uuid {q(uid("note"+str(i)))}))')
s.append('(embedded_fonts no))')
(ROOT/(NAME+'.kicad_sch')).write_text('\n'.join(s),encoding='utf-8')
(ROOT/'sym-lib-table').write_text('(sym_lib_table (version 7)\n'+''.join(f'(lib (name {q(n)}) (type "KiCad") (uri "${{KICAD10_SYMBOL_DIR}}/{n}.kicad_sym") (options "") (descr ""))\n' for n in ['Regulator_Switching','Device','Connector_Generic','power','Mechanical'])+')')
(ROOT/'fp-lib-table').write_text('(fp_lib_table (version 7)\n'+''.join(f'(lib (name {q(n)}) (type "KiCad") (uri "${{KICAD10_FOOTPRINT_DIR}}/{n}.pretty") (options "") (descr ""))\n' for n in sorted({part[3].split(':')[0] for part in parts}))+')')
project={'meta':{'filename':NAME+'.kicad_pro','version':1},'board':{'design_settings':{'rules':{'min_clearance':0.25,'min_track_width':0.25,'min_through_hole_diameter':0.3,'min_copper_edge_clearance':0.5},'defaults':{'board_outline_line_width':0.05}}},'net_settings':{'classes':[{'name':'Default','clearance':0.25,'track_width':0.4,'via_diameter':0.8,'via_drill':0.4},{'name':'Power','clearance':0.25,'track_width':1.25,'via_diameter':1.2,'via_drill':0.6}],'netclass_patterns':[{'netclass':'Power','pattern':n} for n in ['VIN','SW','+5V','GND']]}}
(ROOT/(NAME+'.kicad_pro')).write_text(json.dumps(project,indent=2))
project['net_settings']['version']=4
for rule in project['net_settings']['netclass_patterns']:
    if rule['pattern']!='GND':rule['pattern']='/'+rule['pattern']
project['board']['design_settings']['rules']['min_clearance']=0.25
project['board']['design_settings']['rules']['min_copper_edge_clearance']=0.5
(ROOT/(NAME+'.kicad_pro')).write_text(json.dumps(project,indent=2))

# Two-layer, plated-through-hole board. All signal routing on the top layer;
# Kelvin feedback returns on the bottom from the output capacitor pad.
b=p.BOARD(); b.SetCopperLayerCount(2)
def xy(x,y):return p.VECTOR2I(p.FromMM(x),p.FromMM(y))
nets={}
for n in ['GND','VIN','SW','+5V']:
    ni=p.NETINFO_ITEM(b,n if n=='GND' else '/'+n);b.Add(ni);nets[n]=ni
fps={}
locations={'U1':(72,48,0),'C1':(57,54,90),'C2':(66,46,90),'D1':(80,55,180),'L1':(87,59,0),'C3':(98,70,180),'J1':(53,69,90),'J2':(110,64,270),'H1':(51,42,0),'H2':(114,42,0),'H3':(51,78,0),'H4':(114,78,0)}
for ref,libid,val,foot,*other in parts:
    lib,fn=foot.split(':');f=p.FootprintLoad(str(LIB/'footprints'/(lib+'.pretty')),fn)
    f.SetReference(ref);f.SetValue(val);f.SetFPID(p.LIB_ID(lib,fn))
    x,y,a=locations[ref];f.SetPosition(xy(x,y));f.SetOrientationDegrees(a)
    f.SetPath(p.KIID_PATH('/'+uid('sheet')+'/'+uid(ref)))
    f.SetSheetname('');f.SetSheetfile(NAME+'.kicad_sch')
    f.Value().SetVisible(False)
    f.Reference().SetTextSize(xy(1,1));f.Reference().SetTextThickness(p.FromMM(0.15))
    b.Add(f);fps[ref]=f
    for pad in f.Pads():
        if pad.GetNumber() in other[-1]:pad.SetNet(nets[other[-1][pad.GetNumber()]])
    if ref.startswith('H'):f.Reference().SetVisible(False)
for ref,pos in {'U1':(75.4,38.5),'J1':(61,65),'J2':(102.5,62),'C1':(57,57.5),'C2':(66,39),'D1':(72.4,58.5),'C3':(96,75.5),'L1':(90.5,51)}.items():
    fps[ref].Reference().SetPosition(xy(*pos));fps[ref].Reference().SetTextAngle(p.EDA_ANGLE(0,p.DEGREES_T))
def pad(ref,n):
    v=next(v for v in fps[ref].Pads() if v.GetNumber()==str(n)).GetPosition()
    return (p.ToMM(v.x),p.ToMM(v.y))
print('PAD LOCATIONS',json.dumps({r:{v.GetNumber():pad(r,v.GetNumber()) for v in f.Pads()} for r,f in fps.items()}))
def route(net,pts,width=1.25,layer=p.F_Cu):
    for a,c in zip(pts,pts[1:]):
        if a==c:continue
        t=p.PCB_TRACK(b);t.SetStart(xy(*a));t.SetEnd(xy(*c));t.SetWidth(p.FromMM(width));t.SetLayer(layer);t.SetNet(nets[net]);b.Add(t)
# routing populated after inspecting exact pad geometry
route('VIN',[pad('J1',1),(56,66),(56,57),pad('C1',1),(62,51),(69,51),pad('U1',1)])
route('VIN',[pad('C2',1),(69,46),(69,51)])
route('SW',[pad('U1',2),(73.7,51)],.9)
route('SW',[(73.7,51),(77.7,55),pad('D1',1),(83,55),pad('L1',1)])
route('+5V',[pad('L1',2),(97,62),pad('C3',1)],1.5)
route('+5V',[pad('C3',1),(101,67),(107,67),pad('J2',1)],1.5)
route('+5V',[pad('U1',4),(77.1,44),(97,44),(102,49),(102,67),pad('C3',1)],0.35,p.B_Cu)
route('GND',[pad('U1',3),pad('U1',5)],1.25)
route('GND',[pad('U1',3),(75.4,51.2),(68.5,51.2),pad('D1',2)],1.25,p.B_Cu)
route('GND',[pad('C1',2),(61,49),(64.76,52.76),pad('D1',2)],1.25,p.B_Cu)
route('GND',[pad('C2',2),(59,41),pad('C1',2)],1.25,p.B_Cu)
for a,c in [((47,37),(118,37)),((118,37),(118,82)),((118,82),(47,82)),((47,82),(47,37))]:
    shape=p.PCB_SHAPE();shape.SetShape(p.SHAPE_T_SEGMENT);shape.SetStart(xy(*a));shape.SetEnd(xy(*c));shape.SetLayer(p.Edge_Cuts);shape.SetWidth(p.FromMM(.05));b.Add(shape)
for layer in [p.F_Cu,p.B_Cu]:
    z=p.ZONE(b);z.SetLayer(layer);z.SetNet(nets['GND']);z.SetLocalClearance(p.FromMM(.3));z.SetThermalReliefGap(p.FromMM(.3));z.SetThermalReliefSpokeWidth(p.FromMM(.6));z.SetPadConnection(p.ZONE_CONNECTION_THERMAL);z.SetMinThickness(p.FromMM(.25))
    poly=z.Outline();poly.NewOutline()
    for pt in [(47.6,37.6),(117.4,37.6),(117.4,81.4),(47.6,81.4)]:poly.Append(int(p.FromMM(pt[0])),int(p.FromMM(pt[1])))
    b.Add(z)
def text(txt,x,y,size=1):
    t=p.PCB_TEXT(b);t.SetText(txt);t.SetPosition(xy(x,y));t.SetTextSize(xy(size,size));t.SetTextThickness(p.FromMM(.15));t.SetLayer(p.F_SilkS);b.Add(t)
text('LM2596  12V > 5V',91,77,1.4);text('REV 1.0  /  2026-09',91,79.5,.9)
text('12V IN',54,59,1);text('5V OUT',110,59,1);text('+',53,71,1);text('-',53,62,1);text('+',110,62,1);text('-',110,72,1)
text('HEATSINK',88,39,.9)
p.SaveBoard(str(ROOT/(NAME+'.kicad_pcb')),b)
with (ROOT/'BOM.csv').open('w',newline='') as f:
    w=csv.writer(f);w.writerow(['Reference','Value','Footprint']);w.writerows((r,v,fp) for r,_,v,fp,*_ in parts)
print('Created',ROOT)
