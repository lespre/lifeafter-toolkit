# -*- coding: utf-8 -*-
"""render_neox_mesh.py — NeoX .mesh (ver4) 软件渲染器 v2
功能: 逐子网格贴图(tex_map)· 发光层(emi_map)· 2x超采样 · 金属光照 · 泛光
用法(库): P,uv,idx,meta=parse_mesh(mesh); render(P,uv,idx,'out.png',tex=...,tex_map={1:...},emi=...,sub_offsets=meta['sub_offsets'],roll_deg=50,ss=2,bloom=0.5)
格式文档: WEAPON_MESH_v4_FORMAT.md
"""
import struct, sys, math
import numpy as np
from PIL import Image

def parse_mesh(path):
    d = open(path,'rb').read()
    assert d[:4] == b'\x34\x80\xc8\xbb', 'magic mismatch'
    ver = struct.unpack_from('<H', d, 4)[0]
    off = 14; subs=[]
    for _ in range(3):
        vc, fc = struct.unpack_from('<II', d, off); off += 10
        subs.append((vc, fc))
    off += 2
    tv, tf = struct.unpack_from('<II', d, off); off += 8
    bbox = struct.unpack_from('<6f', d, off); off += 24
    bmin=np.array(bbox[:3],np.float32); bmax=np.array(bbox[3:],np.float32)
    pos_raw=np.frombuffer(d,dtype='<u2',count=tv*3,offset=off).reshape(-1,3)
    off2=off+tv*6; off3=off2+tv*6+2
    idx=np.frombuffer(d,dtype='<u2',count=tf*3,offset=off3).reshape(-1,3)
    off4=off3+tf*6
    uv=np.frombuffer(d,dtype='<f2',count=tv*2,offset=off4).reshape(-1,2).astype(np.float32)
    f=(pos_raw.astype(np.float32)+0.5)/65536.0
    P=bmin+f*(bmax-bmin)
    meta=dict(ver=ver,subs=subs,tv=tv,tf=tf,bbox=(bmin,bmax),sub_offsets=[])
    o=0
    for vc,fc in subs: meta['sub_offsets'].append((o,o+vc)); o+=vc
    return P,uv,idx,meta

def smooth_normals(P, faces):
    N=np.zeros_like(P)
    v0,v1,v2=P[faces[:,0]],P[faces[:,1]],P[faces[:,2]]
    fn=np.cross(v1-v0,v2-v0)
    for k in range(3): np.add.at(N,faces[:,k],fn)
    ln=np.linalg.norm(N,axis=1,keepdims=True); ln[ln==0]=1
    return N/ln

def smooth_normals_welded(P, faces, tol=0.005):
    # NeoX 网格顶点按 UV 缝分裂 -> 按位置焊接后再平滑，消除三角面明暗分块
    q=np.round(P/tol).astype(np.int64)
    key=q[:,0]*100000000000000+q[:,1]*10000000+q[:,2]
    uq,inv=np.unique(key,return_inverse=True)
    N=np.zeros((len(uq),3),np.float64)
    v0,v1,v2=P[faces[:,0]],P[faces[:,1]],P[faces[:,2]]
    fn=np.cross(v1-v0,v2-v0)
    for k in range(3): np.add.at(N,inv[faces[:,k]],fn)
    ln=np.linalg.norm(N,axis=1,keepdims=True); ln[ln==0]=1
    N=N/ln
    return N[inv].astype(np.float32)

def as_tex(src):
    if src is None: return None
    if isinstance(src, np.ndarray): return src
    im=Image.open(src).convert('RGBA')
    return np.asarray(im).astype(np.float32)/255.0

def render(P, uv, faces, out_png, tex=None, emi=None, tex_map=None, emi_map=None, glow=0.9,
           sub_colors=None, sub_offsets=None, size=(1200,1560), roll_deg=55.0,
           eye=(1.0,0.0,0.0), zoom=1.0, ss=2, bg_top=(38,44,58), bg_bot=(20,22,28),
           light=(-0.72,-0.30,0.62), ambient=0.34, diffuse=0.74,
           spec_pow=26.0, spec_str=0.45, spec2_pow=7.0, spec2_str=0.16,
           rimk=0.8, rimcol=(0.30,0.24,0.14), bloom=0.0, bloom_radius=14, emi_th=0.45, emi_k=2.2, tint_map=None, edgek=0.0, edgecol=(0.72,0.78,0.90), edge_pow=5.0, nl_pow=1.0, base_gamma=1.0, knee=1.0, knee_k=2.0, envk=0.0, env_light=(0.55,0.35,0.55), nrm=None, nrm_map=None, nrm_str=1.0, nrm_flip_g=False, edgeface_mask=None, edgeface_rgb=(0.82,0.85,0.90), edgeface_blend=0.5, uv_flip_u=False, uv_flip_v=False, face_overrides=None, weld_smooth=False, normal_override=None, nrm_ch=(0,1),
 edge_sheen_k=0.0, edge_sheen_mu=0.52, edge_sheen_sigma=0.30):
    W0,H0=size; W,H=W0*ss,H0*ss
    c=(P.min(0)+P.max(0))/2.0; p=P-c
    e=np.array(eye,np.float32); e/=np.linalg.norm(e)
    up0=np.array([0,0,1.0],np.float32)
    if abs(np.dot(up0,e))>0.9: up0=np.array([0,1.0,0],np.float32)
    r0=np.cross(up0,e); r0/=np.linalg.norm(r0)
    u0=np.cross(e,r0); u0/=np.linalg.norm(u0)
    sx=p@r0; sy=p@u0; dep=p@e
    a=math.radians(roll_deg)
    Rr=np.array([[math.cos(a),-math.sin(a)],[math.sin(a),math.cos(a)]],np.float32)
    s=Rr@np.stack([sx,sy]); sxx,syy=s[0],s[1]
    spanx=sxx.max()-sxx.min(); spany=syy.max()-syy.min()
    Mg=60*ss
    sc=min((W-2*Mg)/max(spanx,1e-6),(H-2*Mg)/max(spany,1e-6))*zoom
    cx=(sxx.max()+sxx.min())/2; cy=(syy.max()+syy.min())/2
    vx=(sxx-cx)*sc+W/2; vy=H/2-(syy-cy)*sc
    vd=dep.copy()
    Nsm=normal_override if normal_override is not None else (smooth_normals_welded(P,faces) if weld_smooth else smooth_normals(P,faces))
    L=np.array(light,np.float32); L/=np.linalg.norm(L)
    vdir=-e; Hv=(L+vdir); Hv/=np.linalg.norm(Hv)
    tarr=as_tex(tex); earr=as_tex(emi); narr=as_tex(nrm)
    nmap={int(k):as_tex(v) for k,v in (nrm_map or {}).items()}
    tmap={int(k):as_tex(v) for k,v in (tex_map or {}).items()}
    emap={int(k):as_tex(v) for k,v in (emi_map or {}).items()}
    sub_of=None
    if sub_offsets is not None:
        sub_of=np.zeros(len(P),np.int32)
        for k,(a0,a1) in enumerate(sub_offsets): sub_of[a0:a1]=k
    bg=np.zeros((H,W,3),np.float32)
    for i in range(H):
        t=i/(H-1); bg[i,:]=(np.array(bg_top)*(1-t)+np.array(bg_bot)*t)/255.0
    col=bg.copy(); zb=np.full((H,W),-1e9,np.float32)
    order=np.argsort(vd[faces].mean(1))
    for t in order:
        fa,fb,fc=faces[t]
        x0,y0=vx[fa],vy[fa]; x1,y1=vx[fb],vy[fb]; x2,y2=vx[fc],vy[fc]
        minx=max(int(min(x0,x1,x2)),0); maxx=min(int(max(x0,x1,x2))+1,W)
        miny=max(int(min(y0,y1,y2)),0); maxy=min(int(max(y0,y1,y2))+1,H)
        if maxx<=minx or maxy<=miny: continue
        gx,gy=np.meshgrid(np.arange(minx,maxx)+0.5,np.arange(miny,maxy)+0.5)
        d0=(x1-x0)*(gy-y0)-(y1-y0)*(gx-x0)
        d1=(x2-x1)*(gy-y1)-(y2-y1)*(gx-x1)
        d2=(x0-x2)*(gy-y2)-(y0-y2)*(gx-x2)
        m=((d0>=0)&(d1>=0)&(d2>=0))|((d0<=0)&(d1<=0)&(d2<=0))
        if not m.any(): continue
        area=d0+d1+d2
        w0=d1/area; w1=d2/area; w2=d0/area
        dd=w0*vd[fa]+w1*vd[fb]+w2*vd[fc]
        sub=zb[miny:maxy,minx:maxx]; upd=m&(dd>sub)
        if not upd.any(): continue
        si=int(sub_of[fa]) if sub_of is not None else 0
        cur=tmap.get(si, tarr)
        if cur is None and sub_colors is not None:
            shade=np.broadcast_to(np.array(sub_colors[si],np.float32)/255.0,(maxy-miny,maxx-minx,3)).copy()
        else:
            uu=w0*uv[fa,0]+w1*uv[fb,0]+w2*uv[fc,0]
            vv=w0*uv[fa,1]+w1*uv[fb,1]+w2*uv[fc,1]
            txv=uu; tyv=vv
            if uv_flip_u: txv=1.0-uu
            if uv_flip_v: tyv=1.0-vv
            tx=np.clip((txv*1023).astype(int),0,1023); ty=np.clip((tyv*1023).astype(int),0,1023)
            base=cur[ty,tx][...,:3] if cur is not None else np.ones((maxy-miny,maxx-minx,3),np.float32)
            if base_gamma!=1.0: base=base**base_gamma
            if (edgeface_mask is not None) and (t<len(edgeface_mask)) and edgeface_mask[t]:
                base=base*(1.0-edgeface_blend)+np.array(edgeface_rgb,np.float32)[None,None,:]*edgeface_blend
            if face_overrides:
                for (fm,fm_rgb,fm_bl) in face_overrides:
                    if t<len(fm) and fm[t]:
                        base=base*(1.0-fm_bl)+np.array(fm_rgb,np.float32)[None,None,:]*fm_bl
            nn=(w0[...,None]*Nsm[fa]+w1[...,None]*Nsm[fb]+w2[...,None]*Nsm[fc])
            nn/=np.maximum(np.linalg.norm(nn,axis=2,keepdims=True),1e-6)
            nn_geo=nn
            nsrc=nmap.get(si, narr)
            if nsrc is not None:
                ch=nsrc[ty,tx]
                nmv=(np.stack([ch[...,int(nrm_ch[0])],ch[...,int(nrm_ch[1])]],axis=-1)*2.0-1.0)*nrm_str
                if nrm_flip_g: nmv=nmv*np.array([1.0,-1.0],np.float32)
                nz=np.sqrt(np.clip(1.0-nmv[...,0]**2-nmv[...,1]**2,0,1))
                dP1=P[fb]-P[fa]; dP2=P[fc]-P[fa]
                du1=uv[fb]-uv[fa]; du2=uv[fc]-uv[fa]
                det=du1[0]*du2[1]-du2[0]*du1[1]
                if abs(det)<1e-12: Tf=np.array([1.0,0,0]); Bf=np.array([0,1.0,0])
                else:
                    r=1.0/det
                    Tf=(dP1*du2[1]-dP2*du1[1])*r; Bf=(dP2*du1[0]-dP1*du2[0])*r
                Nf=(Nsm[fa]+Nsm[fb]+Nsm[fc])/3.0
                Tf=Tf-Nf*np.dot(Tf,Nf); 
                nT=np.linalg.norm(Tf); Tf=Tf/(nT if nT>1e-9 else 1.0)
                sgn=np.sign(np.dot(np.cross(Nf,Tf),Bf)) or 1.0
                Bf=np.cross(Nf,Tf)*sgn*-1.0 if False else np.cross(Nf,Tf)*sgn
                nw=Tf[None,None,:]*nmv[...,0:1]+Bf[None,None,:]*nmv[...,1:2]+nn*nz[...,None]
                nn=nw/np.maximum(np.linalg.norm(nw,axis=2,keepdims=True),1e-6)
            nl=np.abs(np.sum(nn*L,axis=2))**nl_pow
            ndh=np.maximum(np.sum(nn*Hv,axis=2),0)
            spec=(ndh**spec_pow)*spec_str+(ndh**spec2_pow)*spec2_str
            ndv=np.abs(np.sum(nn*vdir,axis=2))
            rim=(1.0-ndv)**3
            shade=base*(ambient+diffuse*nl[...,None])+spec[...,None]+rim[...,None]*np.array(rimcol,np.float32)*rimk
            if edgek>0:
                edge=((1.0-ndv)**edge_pow)[...,None]*np.array(edgecol,np.float32)*edgek
                shade=shade+edge
            if edge_sheen_k>0:
                ndv_g=np.abs(np.sum(nn_geo*vdir,axis=2))
                sheen=np.exp(-(((ndv_g-edge_sheen_mu)/max(edge_sheen_sigma,1e-6))**2))[...,None]*np.array(edgecol,np.float32)*edge_sheen_k
                shade=shade+sheen
            if envk>0:
                envL=np.array(env_light,np.float32); envL/=np.linalg.norm(envL)
                shade=shade+base*np.maximum(np.sum(nn*envL,axis=2),0)[...,None]*envk
            esrc=emap.get(si,earr)
            if esrc is not None:
                em=esrc[ty,tx]; lum=em[...,:3].mean(axis=2)
                gl=np.clip((lum-emi_th)*emi_k,0,1.2)
                shade=shade+em[...,:3]*gl[...,None]*glow
        if tint_map and si in tint_map:
            shade=shade*np.array(tint_map[si],np.float32)
        if knee<1.0:
            ex=np.maximum(shade-knee,0)
            shade=np.where(shade>knee, knee+ex/(1+ex*knee_k), shade)
        colw=col[miny:maxy,minx:maxx]; colw[upd]=shade[upd]; sub[upd]=dd[upd]
    img=np.clip(col,0,1)
    if bloom>0:
        from PIL import ImageFilter
        b=np.clip((img.mean(axis=2)-0.70)*3.3,0,1)
        bimg=Image.fromarray((np.clip(img*b[...,None],0,1)*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(bloom_radius*ss))
        bb=np.asarray(bimg).astype(np.float32)/255.0
        img=np.clip(img+bb*bloom,0,1)
    oimg=Image.fromarray((img*255).astype(np.uint8))
    if ss>1: oimg=oimg.resize((W0,H0),Image.LANCZOS)
    oimg.save(out_png); return out_png
