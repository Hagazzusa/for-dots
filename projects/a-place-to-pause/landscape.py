"""Seeded terrain only; fixed planar road. 1 unit = 1 virtual metre."""
import math,random,bisect
SEEDS=list(range(1101,1113))
def parameters(seed):
 r=random.Random(seed)
 return {'seed':seed,'amplitudes':[r.uniform(3,7),r.uniform(2,5),r.uniform(2,4)],'phases':[r.uniform(-math.pi,math.pi) for _ in range(3)],'x_scales':[r.uniform(70,110),r.uniform(85,140)],'y_scales':[r.uniform(100,160),r.uniform(120,190),r.uniform(150,220)]}
def cx(y):return 21*math.sin((y+25)/46)+.07*y
def dx(y):return 21/46*math.cos((y+25)/46)+.07
def natural(x,y,p):
 a,b,c=p['amplitudes'];q,r,t=p['phases'];lx,mx=p['x_scales'];ly,my,ny=p['y_scales']
 return 8+.015*(y+80)+a*math.sin(x/lx+y/ly+q)+b*math.cos(x/mx-y/my+r)+c*math.sin(y/ny+t)
def width(y):return 3+4.5*math.exp(-((y-22)/9)**4)
def profile_height(y,profile,p):
 yy=profile['y'];hh=profile['height']
 if y<=yy[0]:return hh[0]+natural(cx(y),y,p)-natural(cx(yy[0]),yy[0],p)
 if y>=yy[-1]:return hh[-1]+natural(cx(y),y,p)-natural(cx(yy[-1]),yy[-1],p)
 i=bisect.bisect_right(yy,y)-1;t=(y-yy[i])/(yy[i+1]-yy[i]);return hh[i]*(1-t)+hh[i+1]*t
