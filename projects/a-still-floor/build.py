"""주기적 물결에서 굴절한 평행광을 고정 바닥에 모으는 절차적 영상."""
from pathlib import Path
import json,math,subprocess,argparse
import numpy as np
from scipy.ndimage import gaussian_filter
from PIL import Image
P=Path(__file__).resolve().parent

def surface(x,y,time,m):
 h=np.zeros_like(x);hx=h.copy();hy=h.copy();L=m['domain_size']
 for w in m['waves']:
  kx=2*np.pi*w['nx']/L;ky=2*np.pi*w['ny']/L
  phase=kx*x+ky*y+2*np.pi*w['cycles']*time/m['loop_seconds']+w['phase']
  h+=w['amplitude']*np.cos(phase);q=-w['amplitude']*np.sin(phase);hx+=q*kx;hy+=q*ky
 return h,hx,hy

def endpoints(x,y,time,m):
 h,hx,hy=surface(x,y,time,m);inv=1/np.sqrt(1+hx*hx+hy*hy);nx=-hx*inv;ny=-hy*inv;nz=inv
 eta=m['air_index']/m['water_index'];a=eta*nz-np.sqrt(1-eta*eta*(1-nz*nz))
 tx=a*nx;ty=a*ny;tz=-eta+a*nz
 distance=(-m['bottom_depth']-h)/tz
 return x+distance*tx,y+distance*ty,tx,ty,tz

def irradiance(time,m,rays,pixels):
 L=m['domain_size'];g=(np.arange(rays)+.5)*L/rays
 counts=np.zeros((pixels,pixels),dtype=np.float64)
 # 광선을 행 묶음으로 계산하여 큰 3D 배열을 동시에 유지하지 않는다.
 for row in range(0,rays,16):
  x,y=np.meshgrid(g,g[row:row+16]);xx,yy,*_=endpoints(x,y,time,m)
  ix=np.floor(np.mod(xx,L)*pixels/L).astype(np.int32);iy=np.floor(np.mod(yy,L)*pixels/L).astype(np.int32)
  counts+=np.bincount((iy*pixels+ix).ravel(),minlength=pixels*pixels).reshape(pixels,pixels)
 raw_sum=float(counts.sum());I=gaussian_filter(counts,sigma=m['blur_sigma_pixels'],mode='wrap')/(rays*rays/(pixels*pixels))
 return I,raw_sum

def colorize(I):
 # 측정 색이 아니라 강도를 청록에서 옅은 금색으로 옮기는 작화 선택이다.
 stops=np.array([0.,.55,1.15,2.5,4.5,8.]);colors=np.array([[9,36,48],[13,60,69],[24,91,94],[74,139,128],[166,190,153],[247,230,176]],dtype=float)
 rgb=np.stack([np.interp(I,stops,colors[:,i]) for i in range(3)],axis=-1)
 return np.clip(np.rint(rgb),0,255).astype(np.uint8)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output-root',type=Path,default=P/'output');a=ap.parse_args();out=a.output_root;out.mkdir(parents=True,exist_ok=True)
 m=json.loads((P/'model.json').read_text());I,total=irradiance(0,m,m['still_rays_per_axis'],m['still_pixels_per_axis']);Image.fromarray(colorize(I)).save(out/'A-Still-Floor.png');np.savez_compressed(out/'irradiance.npz',intensity=I.astype(np.float32))
 (out/'still_data.json').write_text(json.dumps({'ray_count':int(total),'normalized_mean':float(I.mean()),'maximum':float(I.max()),'minimum':float(I.min()),'time_seconds':0},indent=2)+'\n')
if __name__=='__main__':main()
