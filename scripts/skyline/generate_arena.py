"""Original Skyline Rush blockout, MAPZ 56 / game protocol 282.
The layout and encoder are original. Format reference: engine/worldio.cpp.
Run from repository root. No third-party Python packages required.
"""
from pathlib import Path
import struct, gzip, json
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'data/skyline'
OUT.mkdir(parents=True,exist_ok=True)
S=1024
# Each box is x,y,z,width,depth,height,texture. All geometry is on an 8-unit grid.
boxes=[]
def box(x,y,z,w,d,h,t=2): boxes.append((x,y,z,w,d,h,t))
# Low street plane, six connected rooftops and wide crossings.
box(0,0,0,1024,1024,16,1)
for x,y in [(256,256),(448,256),(640,256),(256,544),(448,544),(640,544)]:
 box(x,y,16,128,160,240,2)
 box(x,y,248,128,160,8,3)
for y in (304,592):
 box(384,y,240,64,32,16,4); box(576,y,240,64,32,16,4)
for x in (304,496,688): box(x,416,240,32,128,16,4)
# Cover and two-sided wall-running lanes. Leave spawn pads and routes unobstructed.
for x in (272,464,656):
 for y in (272,640): box(x,y,256,32,32,24,5)
for y in (352,568):
 box(456,y,256,8,32,48,2); box(560,y,256,8,32,48,2)
# Distinctive distant skyline, deliberately outside the combat loop.
for x,y,w,d,h in [(80,80,80,80,352),(160,800,80,80,304),(824,152,96,96,400),(816,792,112,64,328),(464,80,64,64,424)]:
 box(x,y,16,w,d,h,2)
 box(x+16,y+16,16+h,32,32,32,5)
# Octree serialisation: recurse only where a box boundary intersects a node.
def node(x,y,z,n):
 hits=[b for b in boxes if x<b[0]+b[3] and x+n>b[0] and y<b[1]+b[4] and y+n>b[1] and z<b[2]+b[5] and z+n>b[2]]
 if not hits: return struct.pack('<B6H',1,*([0]*6))
 last=hits[-1]
 full=all((a>=b and a+n<=b+s) for a,b,s in zip((x,y,z),last[:3],last[3:6]))
 if full or n==8: return struct.pack('<B6H',2,*([last[6]]*6))
 half=n//2
 return b'\0'+b''.join(node(x+(i&1)*half,y+((i>>1)&1)*half,z+((i>>2)&1)*half,half) for i in range(8))
def svar(k,v):
 k=k.encode();v=v.encode();return struct.pack('<i',len(k))+k+b'\0'+struct.pack('<ii',2,len(v))+v+b'\0'
spawns=[(320,336,264,0),(512,336,264,0),(704,336,264,0),(320,624,264,180),(512,624,264,180),(704,624,264,180)]
entities=[]
for x,y,z,yaw in spawns:
 attrs=[0,yaw,0,0,0,0,0]
 entities.append(struct.pack('<3fB3x',x,y,z,3)+struct.pack('<i7ii',7,*attrs,0))
variables=[svar('maptitle','Skyline Rush / Braamfontein Heights'),svar('mapauthor','Jake Harvey / Skyline Rush'),svar('mapdesc','Original rooftop blockout. Six rooftops, three crossings, one fast loop. Playtest build.')]
raw=struct.pack('<4s9i4s',b'MAPZ',56,44,S,len(entities),0,0,6,282,1,b'fps\0')
raw+=struct.pack('<i',len(variables))+b''.join(variables)+struct.pack('<H',0)+b''.join(entities)
raw+=struct.pack('<i',-6) # six unchanged texture slots
raw+=b''.join(node((i&1)*512,((i>>1)&1)*512,((i>>2)&1)*512,512) for i in range(8))
(OUT/'heights.mpz').write_bytes(gzip.compress(raw,mtime=0))
# Conservative bot routes stay on rooftops and crossings. No links across a gap.
points=[]
for y in (320,608):
 for x in range(288,737,16): points.append((x,y,257))
for x in (320,512,704):
 for y in range(336,593,16): points.append((x,y,257))
points=list(dict.fromkeys(points)); ids={p:i+1 for i,p in enumerate(points)}
wp=b'RWPT'+struct.pack('<iH',1,len(points))
for x,y,z in points:
 links=[ids[p] for p in [(x-16,y,z),(x+16,y,z),(x,y-16,z),(x,y+16,z)] if p in ids]
 wp+=struct.pack('<3fiB',x,y,z,1,len(links))+struct.pack('<'+'H'*len(links),*links)
(OUT/'heights.wpt').write_bytes(gzip.compress(wp,mtime=0))
(OUT/'layout.json').write_text(json.dumps({'worldsize':S,'boxes':boxes,'spawns':spawns,'waypoints':points},indent=2)+'\n')
print(f'Wrote arena: {len(boxes)} boxes, {len(spawns)} spawns, {len(points)} bot waypoints')
