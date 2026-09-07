from pathlib import Path
import xml.etree.ElementTree as ET

root=Path(__file__).parent
expected={
 '/VIN':{'J1.1','C1.1','C2.1','U1.1'},
 '/SW':{'U1.2','D1.1','L1.1'},
 '/+5V':{'L1.2','C3.1','J2.1','U1.4'},
 'GND':{'J1.2','C1.2','C2.2','U1.3','U1.5','D1.2','C3.2','J2.2'},
}
actual={n.attrib['name']:{v.attrib['ref']+'.'+v.attrib['pin'] for v in n.findall('node')} for n in ET.parse(root/'reports/netlist.xml').findall('./nets/net')}
assert actual==expected, f'Net mismatch: expected {expected}, got {actual}'
result='PASS: all 19 component pins match the guide topology across exactly four nets.\n'
result+='\n'.join(n+': '+', '.join(sorted(v)) for n,v in actual.items())+'\n'
(root/'reports/connectivity.txt').write_text(result)
print(result)
