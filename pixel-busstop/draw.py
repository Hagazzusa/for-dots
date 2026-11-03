from PIL import Image, ImageDraw
from pathlib import Path
P={'night':'#111d2b','sky':'#203448','haze':'#2a4659','building':'#172a39','roof':'#10222d','edge':'#385364','glass':'#284455','wet':'#1a303e','road':'#132733','line':'#567180','rain':'#658291','dim':'#825d46','amber':'#d69a59','light':'#f3cb82','glow':'#ae784e','white':'#f9e5af'}
out=Path(__file__).parent
im=Image.new('RGB',(192,108),P['sky']); d=ImageDraw.Draw(im)
def rect(box,c): d.rectangle(box,fill=P[c])
def line(points,c,w=1): d.line(points,fill=P[c],width=w)
# Broad stepped silhouettes; deliberately flat, no gradients.
rect((0,26,40,70),'building'); rect((3,20,31,27),'building'); rect((34,37,65,70),'building')
rect((121,28,155,72),'building'); rect((129,20,150,30),'building'); rect((157,34,191,72),'building')
for x,y in [(8,33),(20,43),(36,48),(133,37),(145,45),(165,42),(178,53)]:
 rect((x,y,x+4,y+6),'haze'); rect((x+1,y+1,x+2,y+3),'dim')
# Wet pavement and road
rect((0,72,191,86),'wet'); rect((0,87,191,107),'road'); line([(0,86),(191,86)],'edge')
# Distant bus approaching at right: compact distinct silhouette, twin lamps.
rect((139,56,173,72),'roof'); rect((142,53,170,57),'roof'); rect((143,57,169,65),'haze')
rect((145,58,154,63),'glass'); rect((158,58,167,63),'glass'); rect((141,66,171,71),'building')
rect((144,67,147,69),'light'); rect((165,67,168,69),'light'); rect((146,72,150,73),'night'); rect((163,72,167,73),'night')
# The shelter: a large warm window framed in dark steel.
rect((26,34,101,74),'roof'); rect((30,38,96,70),'edge'); rect((33,40,93,69),'glass')
rect((36,42,61,68),'glow'); rect((38,44,59,67),'amber'); rect((40,46,57,65),'light')
# Lamp and small interior suggestion, no people.
rect((46,41,52,42),'white'); rect((42,62,57,65),'amber'); rect((45,60,56,61),'dim')
# Frame, sill, and deep eave
rect((23,30,103,34),'roof'); rect((27,28,99,29),'edge'); rect((25,35,28,78),'roof'); rect((97,35,100,78),'roof')
rect((64,38,66,70),'roof'); rect((31,70,96,72),'roof'); rect((31,73,34,79),'edge'); rect((92,73,95,79),'edge')
# Bench under shelter, silhouette separate from frame.
rect((68,61,89,63),'edge'); rect((70,64,87,65),'roof'); rect((71,66,72,70),'roof'); rect((85,66,86,70),'roof')
# Stop pole and deliberately abstract unlettered sign.
rect((111,37,113,80),'edge'); rect((105,33,119,43),'roof'); rect((107,35,117,41),'haze'); rect((110,37,114,39),'light')
# Ground reflections: restrained bands and broken lines.
for box,c in [((37,78,62,78),'dim'),((43,80,57,80),'amber'),((40,83,60,83),'glow'),((47,88,56,88),'dim'),((39,92,53,92),'glow'),((45,97,61,97),'dim'),((143,77,149,77),'amber'),((164,77,170,77),'amber'),((145,82,153,82),'dim'),((160,84,168,84),'dim'),((17,89,30,89),'haze'),((111,93,129,93),'haze'),((3,101,21,101),'edge'),((77,102,91,102),'haze'),((156,99,178,99),'edge')]: rect(box,c)
# Diagonal rain marks, manually placed to avoid obscuring focal shapes.
for x,y in [(5,4),(17,14),(31,6),(45,18),(60,8),(73,16),(87,4),(104,13),(118,4),(132,13),(150,5),(166,16),(181,4),(8,50),(18,59),(106,51),(123,26),(180,29),(185,65),(122,63),(4,78),(126,79),(181,81),(72,83),(11,95),(99,98),(183,96)]: line([(x,y),(x-1,y+3)],'rain')
# A couple of splashes make the still scene feel inhabited by weather.
for x,y in [(17,84),(82,85),(125,86),(183,88)]: rect((x,y,x+2,y),'edge'); rect((x+1,y-1,x+1,y-1),'edge')
im.save(out/'busstop.png'); im.resize((1152,648),Image.Resampling.NEAREST).save(out/'busstop_6x.png')
# Mechanical checks: exact palette and reversible nearest-neighbour enlargement.
assert im.size==(192,108)
assert set(im.getdata()) <= {tuple(bytes.fromhex(v[1:])) for v in P.values()}
big=Image.open(out/'busstop_6x.png').convert('RGB'); assert big.size==(1152,648)
assert big.resize(im.size,Image.Resampling.NEAREST).tobytes()==im.tobytes()
for y in range(108):
 for x in range(192):
  assert len(set(big.crop((x*6,y*6,x*6+6,y*6+6)).getdata()))==1
print('verified: 192x108, palette-only, every 6x6 block uniform, exact roundtrip')
