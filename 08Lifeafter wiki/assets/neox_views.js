
// ===== NeoX 中间量视图材质（source_strict / stage_debug 严格分开）=====
function neoxBuildViewMaterial(pr, g, view, THREE, base, texCache, hasExtra){
  const FULL=['Tex0','t_basecolor','NormalMap','DetailMap','t_caustic_tex','t_refraction_tex','t_custom_ibl','t_reflection_tex'];
  const NEED={ 'T_linear':['t_basecolor'], 'T_sRGB':['t_basecolor'], 'm':['Tex0'],
               'C_base':['t_basecolor','Tex0'], 'forward_family':['t_basecolor','Tex0'], 'source_strict':FULL.slice() };
  const need=NEED[view]||[];
  const missing=need.filter(k=>!g[k]||!g[k].file);
  const strict=(view==='source_strict');
  const u={
    uView:{value:{'T_linear':0,'T_sRGB':1,'m':2,'C_base':3,'forward_family':4,'source_strict':5}[view]||0},
    uCol:{value:texCache(g.t_basecolor?g.t_basecolor.file:null, view==='T_sRGB')},
    uMask:{value:texCache(g.Tex0?g.Tex0.file:null, false)},
    uDet:{value:texCache(g.DetailMap?g.DetailMap.file:null, false)},
    uHasDet:{value:(g.DetailMap&&g.DetailMap.file)?1:0},
    uBaseColor:{value:[0.1098,0.3961,0.502,1.0]},
    uCrystalColor:{value:[0.0,0.2118,0.8,1.0]},
    uDiagA1:{value:0.0}, uMissing:{value:(strict&&missing.length)?1:0}
  };
  const m=new THREE.ShaderMaterial({uniforms:u,
    vertexShader:`varying vec2 vUv; void main(){ vUv=uv; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);}`,
    fragmentShader:`
      uniform sampler2D uCol,uMask,uDet; uniform int uView; uniform float uHasDet,uDiagA1,uMissing;
      uniform vec4 uBaseColor,uCrystalColor; varying vec2 vUv;
      void main(){
        if(uMissing>0.5){ gl_FragColor=vec4(1.0,0.0,1.0,1.0); return; }
        vec4 T=texture2D(uCol,vUv); float m_=texture2D(uMask,vUv).r;
        if(uView==0||uView==1){ gl_FragColor=vec4(T.rgb,1.0); return; }
        if(uView==2){ gl_FragColor=vec4(vec3(m_),1.0); return; }
        // C_base / forward_family / source_strict：仅已确认的颜色混合
        float d=(uHasDet>0.5)?(texture2D(uDet,vUv).a*m_):(uDiagA1>0.5?1.0:m_);
        vec3 A=mix(T.rgb,T.rgb*uCrystalColor.rgb,m_);
        vec3 B=mix(uBaseColor.rgb,T.rgb*uCrystalColor.rgb,d);
        vec3 C=mix(A,B,m_);
        gl_FragColor=vec4(C,1.0);
      }`});
  m.userData.neoxView={view:view, program_family:(pr.shader_kind==='weapon'?'weapon':'forward_basecolor_3f_d982'),
    primitive:pr.prim, need:need, missing:missing, strict:strict,
    textures:Object.fromEntries(Object.entries(g).map(([k,v])=>[k,{file:v.file,sha:v.sha,cs:v.cs}])),
    uniforms:{uBaseColor:u.uBaseColor.value,uCrystalColor:u.uCrystalColor.value,uHasDet:u.uHasDet.value,uDiagA1:u.uDiagA1.value}};
  return m;
}
