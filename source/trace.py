import numpy as np, potrace
from PIL import Image, ImageFilter
im=Image.open('source.jpg').convert('RGB').resize((2160,2160),Image.LANCZOS).filter(ImageFilter.GaussianBlur(1.2))
a=np.asarray(im).astype(int); r,g,b=a[...,0],a[...,1],a[...,2]
H=a.shape[0]; yy,xx=np.mgrid[0:H,0:H]; cx=cy=H/2
rad=np.hypot(xx-cx,yy-cy)
inside=rad<H*0.455
from scipy import ndimage as nd
raw=b-(r+g)/2.0
bs_mark=nd.gaussian_filter(raw,(5,1.8))
bs_text=nd.gaussian_filter(raw,1.0)
textzone=(yy>1350)
bs=np.where(textzone,bs_text,bs_mark)
lum=nd.gaussian_filter((r+g+b)/3.0,1.5)
def fill_small(m,maxa):
    lab,n=nd.label(~m)
    sizes=nd.sum(np.ones_like(lab),lab,range(1,n+1))
    small=np.isin(lab,[i+1 for i,sz in enumerate(sizes) if sz<maxa])
    return m|small
blue=np.where(textzone,bs>75,bs>45)&inside
blue=fill_small(blue,300)
blue&=~((yy>1632)&(yy<1668)&(xx>1000))
blue=nd.binary_opening(blue,iterations=2)
black=(lum<140)&(nd.gaussian_filter(raw,1.0)<25)&inside&(((yy>1170)&(xx>1060))|(yy>1660))&~nd.binary_dilation(blue,iterations=4)
black=fill_small(black,40)
def trace(mask):
    bm=potrace.Bitmap(~mask)
    p=bm.trace(turdsize=80,alphamax=1.0,opticurve=True,opttolerance=0.3)
    s=[]
    for c in p:
        st=c.start_point; d=[f"M{st.x/2:.2f},{st.y/2:.2f}"]
        for seg in c.segments:
            if seg.is_corner: d.append(f"L{seg.c.x/2:.2f},{seg.c.y/2:.2f}L{seg.end_point.x/2:.2f},{seg.end_point.y/2:.2f}")
            else: d.append(f"C{seg.c1.x/2:.2f},{seg.c1.y/2:.2f} {seg.c2.x/2:.2f},{seg.c2.y/2:.2f} {seg.end_point.x/2:.2f},{seg.end_point.y/2:.2f}")
        s.append("".join(d)+"Z")
    return " ".join(s)
pb=trace(blue); pk=trace(black)
stripes="".join(f'<rect x="0" y="{y}" width="1080" height="7"/>' for y in range(40,1040,14))
svg=f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 1080" width="1080" height="1080">
<title>The Open Source Community</title>
<defs><clipPath id="c"><circle cx="540" cy="540" r="500"/></clipPath>
<radialGradient id="g" cx="0.42" cy="0.38" r="0.7"><stop offset="0" stop-color="#2a3cf0"/><stop offset="1" stop-color="#0a0f8a"/></radialGradient></defs>
<circle cx="540" cy="540" r="500" fill="#ffffff"/>
<g clip-path="url(#c)" fill="#dfe3e8">{stripes}</g>
<circle cx="540" cy="540" r="500" fill="none" stroke="#1a2bc4" stroke-width="5"/>
<path fill="url(#g)" fill-rule="evenodd" d="{pb}"/>
<rect x="183" y="822" width="722" height="7" rx="3.5" fill="#0f1590"/>
<path fill="#111111" fill-rule="evenodd" d="{pk}"/>
</svg>'''
open('opensource-community-logo.svg','w').write(svg)
print(len(svg))
