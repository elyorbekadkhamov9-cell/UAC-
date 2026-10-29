/* UAC site — shared behaviour: sound, page transitions, cursor, tilt, count-up, marquee,
   the background particle scene and the small rotating molecules. */
(function(){
  "use strict";
  var UAC = window.UAC = window.UAC || {};
  var reduce = !!(window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches);
  UAC.reduce = reduce;

  /* ---------------- sound ---------------- */
  var Sound = UAC.Sound = {
    ctx:null, on:true, last:0,
    init:function(){
      if(!this.ctx){ try{ var AC=window.AudioContext||window.webkitAudioContext; if(AC) this.ctx=new AC(); }catch(e){} }
      if(this.ctx && this.ctx.state==="suspended"){ try{ this.ctx.resume(); }catch(e){} }
    },
    tone:function(f0,f1,dur,gain,type,delay){
      if(!this.on||!this.ctx) return;
      var c=this.ctx, t=c.currentTime+(delay||0), o=c.createOscillator(), g=c.createGain();
      o.type=type||"sine"; o.frequency.setValueAtTime(f0,t); o.frequency.exponentialRampToValueAtTime(Math.max(f1,20),t+dur);
      g.gain.setValueAtTime(0.0001,t); g.gain.exponentialRampToValueAtTime(gain,t+0.006); g.gain.exponentialRampToValueAtTime(0.0001,t+dur);
      o.connect(g); g.connect(c.destination); o.start(t); o.stop(t+dur+0.03);
    },
    noise:function(dur,gain,freq){
      if(!this.on||!this.ctx) return;
      var c=this.ctx, n=Math.floor(c.sampleRate*dur), buf=c.createBuffer(1,n,c.sampleRate), d=buf.getChannelData(0);
      for(var i=0;i<n;i++){ d[i]=(Math.random()*2-1)*Math.pow(1-i/n,2); }
      var s=c.createBufferSource(), f=c.createBiquadFilter(), g=c.createGain();
      f.type="bandpass"; f.frequency.value=freq; f.Q.value=0.8; g.gain.value=gain;
      s.buffer=buf; s.connect(f); f.connect(g); g.connect(c.destination); s.start();
    },
    /* soft, low "tap" sounds: short, warm, no high pitches */
    tap:function(freq,dur,gain){
      if(!this.on||!this.ctx) return;
      var c=this.ctx, t=c.currentTime, o=c.createOscillator(), g=c.createGain(), f=c.createBiquadFilter();
      o.type="sine"; o.frequency.setValueAtTime(freq,t); o.frequency.exponentialRampToValueAtTime(freq*0.62,t+dur);
      f.type="lowpass"; f.frequency.value=1400; f.Q.value=0.4;
      g.gain.setValueAtTime(0.0001,t); g.gain.exponentialRampToValueAtTime(gain,t+0.004); g.gain.exponentialRampToValueAtTime(0.0001,t+dur);
      o.connect(f); f.connect(g); g.connect(c.destination); o.start(t); o.stop(t+dur+0.02);
    },
    soft:function(dur,gain,freq){
      if(!this.on||!this.ctx) return;
      var c=this.ctx, n=Math.floor(c.sampleRate*dur), buf=c.createBuffer(1,n,c.sampleRate), d=buf.getChannelData(0);
      for(var i=0;i<n;i++){ d[i]=(Math.random()*2-1)*Math.pow(1-i/n,3); }
      var s=c.createBufferSource(), f=c.createBiquadFilter(), g=c.createGain();
      f.type="lowpass"; f.frequency.value=freq; g.gain.value=gain;
      s.buffer=buf; s.connect(f); f.connect(g); g.connect(c.destination); s.start();
    },
    click:function(){ this.tap(420,0.09,0.11); this.soft(0.03,0.05,1600); },
    page:function(){ this.soft(0.16,0.10,1100); this.tap(330,0.08,0.05); },
    tick:function(){ var now=performance.now(); if(now-this.last<90) return; this.last=now; this.tap(640,0.035,0.012); },
    pop:function(){ this.tap(300,0.14,0.10); this.tap(460,0.12,0.05); },
    swoosh:function(){ this.soft(0.32,0.08,700); },
    chord:function(){ var s=this; [523.25,659.25,783.99].forEach(function(f,i){ s.tone(f,f*0.999,0.55,0.07,"sine",i*0.06); }); }
  };
  document.documentElement.classList.add("js");

  function $(s,r){ return (r||document).querySelector(s); }
  function $$(s,r){ return [].slice.call((r||document).querySelectorAll(s)); }

  document.addEventListener("DOMContentLoaded", function(){
    document.addEventListener("pointerdown",function(){ Sound.init(); },{passive:true});
    document.addEventListener("click",function(e){ var t=e.target.closest&&e.target.closest("[data-sfx]"); if(!t) return; Sound.init(); var k=t.getAttribute("data-sfx"); if(Sound[k]) Sound[k](); });
    document.addEventListener("pointerover",function(e){ if(e.pointerType!=="mouse") return; var t=e.target.closest&&e.target.closest("[data-hover]"); if(!t||t.contains(e.relatedTarget)) return; Sound.tick(); });

    /* page-leave curtain for links between our own pages */
    var curtain=document.createElement("div"); curtain.className="curtain"; curtain.setAttribute("aria-hidden","true");
    curtain.innerHTML='<span>UAC</span>'; document.body.appendChild(curtain);
    document.addEventListener("click",function(e){
      var a=e.target.closest&&e.target.closest("a[href]"); if(!a) return;
      var href=a.getAttribute("href");
      if(!/^[a-z0-9-]+\.html(#.*)?$/i.test(href) || a.target==="_blank" || e.metaKey||e.ctrlKey||e.shiftKey||e.button!==0) return;
      if(reduce) return;
      e.preventDefault(); Sound.init(); Sound.swoosh();
      curtain.classList.add("go");
      setTimeout(function(){ location.href=href; }, 430);
    });
    window.addEventListener("pageshow",function(){ curtain.classList.remove("go"); });

    /* cursor + tilt */
    if(!reduce){
      var cur=document.createElement("div"); cur.className="cursor"; cur.setAttribute("aria-hidden","true"); document.body.appendChild(cur);
      var cx=-100,cy=-100,tx=-100,ty=-100;
      window.addEventListener("pointermove",function(e){ tx=e.clientX; ty=e.clientY; cur.classList.toggle("big",!!(e.target.closest&&e.target.closest("a,button,[data-tilt]"))); },{passive:true});
      (function loop(){ cx+=(tx-cx)*0.22; cy+=(ty-cy)*0.22; cur.style.transform="translate3d("+cx.toFixed(1)+"px,"+cy.toFixed(1)+"px,0)"; requestAnimationFrame(loop); })();
      UAC.tilt=function(root){
        $$("[data-tilt]",root).forEach(function(card){
          if(card._tilt) return; card._tilt=1;
          card.addEventListener("pointermove",function(e){ if(e.pointerType!=="mouse") return; var r=card.getBoundingClientRect(), px=(e.clientX-r.left)/r.width-0.5, py=(e.clientY-r.top)/r.height-0.5; card.style.transform="perspective(900px) rotateX("+(-py*8).toFixed(2)+"deg) rotateY("+(px*10).toFixed(2)+"deg) translateY(-4px)"; });
          card.addEventListener("pointerleave",function(){ card.style.transform=""; });
        });
      };
    } else { UAC.tilt=function(){}; }
    UAC.tilt(document);

    /* hand-drawn marks: measure each stroke, draw it once when it comes into view */
    $$(".draw[data-draw]").forEach(function(svg){
      $$("path",svg).forEach(function(p){ try{ var L=Math.ceil(p.getTotalLength())+2; p.style.setProperty("--len",L); p.style.strokeDasharray=L; }catch(e){} });
    });
    if("IntersectionObserver" in window && !reduce){
      var dio=new IntersectionObserver(function(es){ es.forEach(function(en){ if(en.isIntersecting){ var el=en.target; setTimeout(function(){ el.classList.add("drawn"); $$("path",el).forEach(function(p){ p.style.strokeDashoffset=0; }); }, +(el.getAttribute("data-draw")||0)); dio.unobserve(el); } }); },{threshold:0.6});
      $$(".draw[data-draw]").forEach(function(el){ dio.observe(el); });
    } else { $$(".draw[data-draw]").forEach(function(el){ el.classList.add("drawn"); $$("path",el).forEach(function(p){ p.style.strokeDashoffset=0; }); }); }

    /* count up */
    if("IntersectionObserver" in window && !reduce){
      $$("[data-count]").forEach(function(el){
        var target=+el.getAttribute("data-count"), done=false;
        var io=new IntersectionObserver(function(es){ es.forEach(function(en){ if(en.isIntersecting&&!done){ done=true; io.disconnect(); var t0=performance.now();
          (function step(now){ var p=Math.min(1,(now-t0)/1300); el.textContent=Math.round(target*(1-Math.pow(1-p,3))); if(p<1) requestAnimationFrame(step); })(t0); } }); },{threshold:0.4});
        io.observe(el);
      });
    }

    /* marquee */
    var mq=$("[data-marquee]");
    if(mq && !reduce){
      var x=0, lastY=window.scrollY, vel=0;
      (function run(){ var y=window.scrollY; vel=vel*0.85+(y-lastY)*0.15; lastY=y; var w=mq.scrollWidth/3; x-=0.6+Math.min(10,Math.abs(vel)*0.2); if(-x>w) x+=w; mq.style.transform="translate3d("+x.toFixed(1)+"px,0,0)"; requestAnimationFrame(run); })();
    }

    initScene();
    initMinis();
  });

  /* ---------------- shapes (point clouds) ---------------- */
  var NAVY=[0.11,0.23,0.36], SKY=[0.24,0.6,0.85], LIGHT=[0.5,0.73,0.89], SUN=[0.97,0.68,0.1], MID=[0.42,0.56,0.69], INK=[0.05,0.12,0.21];
  function rnd(seed){ return function(){ seed|=0; seed=seed+0x6D2B79F5|0; var t=Math.imul(seed^seed>>>15,1|seed); t=t+Math.imul(t^t>>>7,61|t)^t; return ((t^t>>>14)>>>0)/4294967296; }; }
  function sph(r){ var u=r(), v=r(), th=2*Math.PI*u, ph=Math.acos(2*v-1); return [Math.sin(ph)*Math.cos(th),Math.cos(ph),Math.sin(ph)*Math.sin(th)]; }
  function make(N,fill){ var P=new Float32Array(N*3), C=new Float32Array(N*3); for(var i=0;i<N;i++){ var o=fill(i,N); P[i*3]=o[0];P[i*3+1]=o[1];P[i*3+2]=o[2]; C[i*3]=o[3][0];C[i*3+1]=o[3][1];C[i*3+2]=o[3][2]; } return {P:P,C:C,N:N}; }
  function seg(r,p,q,rad){ var u=r(), a=r()*Math.PI*2; return [p[0]+(q[0]-p[0])*u+Math.cos(a)*rad, p[1]+(q[1]-p[1])*u+Math.sin(a)*rad, p[2]+(q[2]-p[2])*u+Math.sin(a+1.3)*rad]; }
  function neck(x,y,ang){ var nx=x*Math.cos(ang)-(y-0.62)*Math.sin(ang), ny=x*Math.sin(ang)+(y-0.62)*Math.cos(ang); return [nx,ny+0.62]; }

  var GEN = UAC.shapes = {
    flask:function(N){ var r=rnd(11); return make(N,function(i){
      var k=i/N, d, x,y,z, c=MID, cyc=-0.35, R=1.08;
      if(k<0.46){ do{ d=sph(r); }while(d[1]>0.93); x=d[0]*R; y=cyc+d[1]*R; z=d[2]*R; c=(i%5===0)?NAVY:MID; }
      else if(k<0.62){ var a=r()*Math.PI*2; x=Math.cos(a)*0.24; z=Math.sin(a)*0.24; y=0.62+r()*1.25; var p=neck(x,y,-0.45); x=p[0]; y=p[1]; c=MID; }
      else if(k<0.66){ var a2=r()*Math.PI*2; x=Math.cos(a2)*0.34; z=Math.sin(a2)*0.34; y=1.87; var p2=neck(x,y,-0.45); x=p2[0]; y=p2[1]; c=NAVY; }
      else { do{ d=sph(r); var s=Math.cbrt(r())*0.97; x=d[0]*R*s; y=cyc+d[1]*R*s; z=d[2]*R*s; }while(y>cyc-0.05+0.12*Math.sin(x*3)); c=(r()<0.06)?SUN:SKY; }
      return [x,y,z,c]; }); },
    benzene:function(N){ var r=rnd(21), Cp=[], Hp=[]; for(var a=0;a<6;a++){ var t=a*Math.PI/3+Math.PI/6; Cp.push([Math.cos(t)*1.15,Math.sin(t)*1.15,0]); Hp.push([Math.cos(t)*2.05,Math.sin(t)*2.05,0]); }
      return make(N,function(i){ var k=i/N, v, c;
        if(k<0.40){ var j=i%6, d=sph(r); v=[Cp[j][0]+d[0]*0.27,Cp[j][1]+d[1]*0.27,d[2]*0.27]; c=NAVY; }
        else if(k<0.58){ var h=i%6, e=sph(r); v=[Hp[h][0]+e[0]*0.17,Hp[h][1]+e[1]*0.17,e[2]*0.17]; c=SKY; }
        else if(k<0.78){ var b=i%6; v=seg(r,Cp[b],Cp[(b+1)%6],0.05); c=MID; }
        else if(k<0.88){ var b2=i%6; v=seg(r,Cp[b2],Hp[b2],0.04); c=MID; }
        else { var a3=r()*Math.PI*2, zz=(i%2?0.32:-0.32); v=[Math.cos(a3)*0.72,Math.sin(a3)*0.72,zz]; c=SUN; }
        var tilt=0.75; return [v[0], v[1]*Math.cos(tilt)-v[2]*Math.sin(tilt), v[1]*Math.sin(tilt)+v[2]*Math.cos(tilt), c]; }); },
    dna:function(N){ var r=rnd(31); return make(N,function(i){ var k=i/N;
      if(k<0.72){ var s=i%2, u=r()*2-1, L=3.4, ang=u*L*1.9+(s?Math.PI:0); return [u*L, Math.cos(ang)*0.62+(r()-0.5)*0.05, Math.sin(ang)*0.62+(r()-0.5)*0.05, s?SKY:NAVY]; }
      var rung=Math.floor(r()*36), u2=(rung/35)*2-1, ang2=u2*3.4*1.9, t2=r()*2-1; return [u2*3.4, Math.cos(ang2)*0.62*t2, Math.sin(ang2)*0.62*t2, t2>0?SUN:MID]; }); },
    atom:function(N){ var r=rnd(41); return make(N,function(i){ var k=i/N;
      if(k<0.18){ var d=sph(r), s=Math.cbrt(r())*0.36; return [d[0]*s,d[1]*s,d[2]*s,(i%2)?SUN:SKY]; }
      var o=i%3, a=r()*Math.PI*2, R=1.75, px=Math.cos(a)*R, py=Math.sin(a)*R*0.42, rot=o*Math.PI/3;
      var x=px*Math.cos(rot)-py*Math.sin(rot), y=px*Math.sin(rot)+py*Math.cos(rot), z=(r()-0.5)*0.04, t=0.5;
      var c=MID; if(Math.abs(a-(o*2.1+0.6))<0.1) c=NAVY;
      return [x, y*Math.cos(t)-z*Math.sin(t), y*Math.sin(t)+z*Math.cos(t), c]; }); },
    crystal:function(N){ var r=rnd(51), sites=[]; for(var a=0;a<4;a++)for(var b=0;b<4;b++)for(var c=0;c<4;c++) sites.push([a-1.5,b-1.5,c-1.5,(a+b+c)%2]);
      var bonds=[]; sites.forEach(function(p,i){ sites.forEach(function(q,j){ if(j>i && Math.abs(p[0]-q[0])+Math.abs(p[1]-q[1])+Math.abs(p[2]-q[2])===1) bonds.push([p,q]); }); });
      return make(N,function(i){ var k=i/N, s=0.62;
        if(k<0.7){ var p=sites[i%64], d=sph(r), rad=p[3]?0.2:0.12; return [(p[0]+d[0]*rad/s)*s,(p[1]+d[1]*rad/s)*s,(p[2]+d[2]*rad/s)*s, p[3]?SKY:NAVY]; }
        var b=bonds[Math.floor(r()*bonds.length)], v=seg(r,b[0],b[1],0.01); return [v[0]*s,v[1]*s,v[2]*s,MID]; }); },
    uac:function(N){ var r=rnd(61), cv=document.createElement("canvas"); cv.width=640; cv.height=240; var g=cv.getContext("2d");
      g.fillStyle="#000"; g.font="900 210px 'Arial Black', Arial, sans-serif"; g.textAlign="center"; g.textBaseline="middle"; g.fillText("UAC",320,128);
      var data=g.getImageData(0,0,640,240).data, hits=[]; for(var y=0;y<240;y+=2) for(var x=0;x<640;x+=2) if(data[(y*640+x)*4+3]>128) hits.push([x,y]);
      return make(N,function(){ var h=hits.length?hits[Math.floor(r()*hits.length)]:[320,120]; var x=(h[0]-320)/640*5.2; return [x, -(h[1]-120)/240*1.95, (r()-0.5)*0.35, x<-0.9?NAVY:(x<0.9?SKY:MID)]; }); }
  };

  /* ---------------- background scene ---------------- */
  function initScene(){
    var canvas=document.getElementById("scene"), THREE=window.THREE;
    var anchors=$$("[data-shape]");
    if(!canvas || !anchors.length) return;
    if(!THREE){ canvas.style.display="none"; return; }
    var renderer; try{ renderer=new THREE.WebGLRenderer({canvas:canvas,antialias:true,alpha:true}); }catch(e){ canvas.style.display="none"; return; }
    renderer.setPixelRatio(Math.min(window.devicePixelRatio||1,2)); renderer.setClearColor(0x000000,0);
    var scene=new THREE.Scene(), camera=new THREE.PerspectiveCamera(40,innerWidth/innerHeight,0.1,100); camera.position.set(0,0,7.2);
    var N=4600, shapes=anchors.map(function(a){ return GEN[a.getAttribute("data-shape")](N); });
    function look(a,narrow){ var v=(a.getAttribute(narrow?"data-look-n":"data-look")||"0,0,1,1").split(",").map(Number); return v; }
    var geo=new THREE.BufferGeometry(), pos=new Float32Array(shapes[0].P), col=new Float32Array(shapes[0].C);
    geo.setAttribute("position",new THREE.BufferAttribute(pos,3)); geo.setAttribute("color",new THREE.BufferAttribute(col,3));
    var sc=document.createElement("canvas"); sc.width=sc.height=64; var sg=sc.getContext("2d"), grd=sg.createRadialGradient(32,32,0,32,32,32);
    grd.addColorStop(0,"rgba(255,255,255,1)"); grd.addColorStop(0.45,"rgba(255,255,255,.85)"); grd.addColorStop(1,"rgba(255,255,255,0)"); sg.fillStyle=grd; sg.fillRect(0,0,64,64);
    var mat=new THREE.PointsMaterial({size:0.05,map:new THREE.CanvasTexture(sc),vertexColors:true,transparent:true,depthWrite:false,opacity:1,sizeAttenuation:true});
    var pts=new THREE.Points(geo,mat); scene.add(pts);
    function resize(){ renderer.setSize(innerWidth,innerHeight,false); camera.aspect=innerWidth/innerHeight; camera.updateProjectionMatrix(); }
    resize(); window.addEventListener("resize",resize);
    var mx=0,my=0; window.addEventListener("pointermove",function(e){ mx=e.clientX/innerWidth-0.5; my=e.clientY/innerHeight-0.5; },{passive:true});
    function ease(t){ return t<0.5?4*t*t*t:1-Math.pow(-2*t+2,3)/2; }
    function stage(){ var mid=innerHeight/2, ds=anchors.map(function(a){ var r=a.getBoundingClientRect(); return r.top+Math.min(r.height,innerHeight)/2-mid; });
      if(ds[0]>=0||ds.length===1) return {a:0,b:0,t:0};
      for(var i=0;i<ds.length-1;i++){ if(ds[i]<=0&&ds[i+1]>0) return {a:i,b:i+1,t:ease(Math.min(1,Math.max(0,-ds[i]/(ds[i+1]-ds[i]))))}; }
      return {a:ds.length-1,b:ds.length-1,t:0}; }
    var t0=performance.now(), rot=0;
    (function frame(now){
      requestAnimationFrame(frame); if(document.hidden) return;
      var time=(now-t0)/1000, st=stage(), A=shapes[st.a], B=shapes[st.b], t=st.t, narrow=innerWidth<820;
      var la=look(anchors[st.a],narrow), lb=look(anchors[st.b],narrow), L=[0,1,2,3].map(function(k){ return la[k]+(lb[k]-la[k])*t; });
      var wob=reduce?0:0.012;
      for(var i=0,n3=N*3;i<n3;i+=3){ var j=i/3;
        pos[i]=A.P[i]+(B.P[i]-A.P[i])*t+Math.sin(time*1.4+j*0.37)*wob;
        pos[i+1]=A.P[i+1]+(B.P[i+1]-A.P[i+1])*t+Math.cos(time*1.1+j*0.53)*wob;
        pos[i+2]=A.P[i+2]+(B.P[i+2]-A.P[i+2])*t;
        col[i]=A.C[i]+(B.C[i]-A.C[i])*t; col[i+1]=A.C[i+1]+(B.C[i+1]-A.C[i+1])*t; col[i+2]=A.C[i+2]+(B.C[i+2]-A.C[i+2])*t; }
      geo.attributes.position.needsUpdate=true; geo.attributes.color.needsUpdate=true;
      rot+=reduce?0:0.0028; pts.rotation.y=rot+mx*0.5; pts.rotation.x=my*0.25;
      pts.position.set(L[0],L[1],0); pts.scale.setScalar(L[2]); mat.opacity=L[3];
      renderer.render(scene,camera);
    })(t0);
  }

  /* ---------------- small rotating molecules (2D canvas, no WebGL) ---------------- */
  function initMinis(){
    $$("canvas[data-mini]").forEach(function(cv){
      var shape=GEN[cv.getAttribute("data-mini")](900), ctx=cv.getContext("2d"), host=cv.closest("[data-mini-host]")||cv;
      var speed=1, target=1, ang=Math.random()*6, visible=true, dpr=Math.min(window.devicePixelRatio||1,2);
      host.addEventListener("pointerenter",function(){ target=4; }); host.addEventListener("pointerleave",function(){ target=1; });
      host.addEventListener("focusin",function(){ target=4; }); host.addEventListener("focusout",function(){ target=1; });
      if("IntersectionObserver" in window){ new IntersectionObserver(function(es){ visible=es[0].isIntersecting; }).observe(cv); }
      var scale=+(cv.getAttribute("data-scale")||1);
      function draw(){
        var w=cv.clientWidth, h=cv.clientHeight; if(!w||!h) return;
        if(cv.width!==Math.round(w*dpr)){ cv.width=Math.round(w*dpr); cv.height=Math.round(h*dpr); }
        ctx.setTransform(dpr,0,0,dpr,0,0); ctx.clearRect(0,0,w,h);
        var ca=Math.cos(ang), sa=Math.sin(ang), cb=Math.cos(0.35), sb=Math.sin(0.35), f=Math.min(w,h)*0.24*scale, P=shape.P, C=shape.C;
        for(var i=0;i<shape.N;i++){ var x=P[i*3], y=P[i*3+1], z=P[i*3+2];
          var x1=x*ca+z*sa, z1=-x*sa+z*ca, y1=y*cb-z1*sb, z2=y*sb+z1*cb, p=4.5/(4.5+z2);
          ctx.fillStyle="rgb("+Math.round(C[i*3]*255)+","+Math.round(C[i*3+1]*255)+","+Math.round(C[i*3+2]*255)+")";
          ctx.globalAlpha=0.45+0.5*p*p/1.6; var s=1.6*p;
          ctx.fillRect(w/2+x1*f*p-s/2, h/2-y1*f*p-s/2, s, s); }
        ctx.globalAlpha=1;
      }
      (function loop(){ requestAnimationFrame(loop); if(!visible||document.hidden) return; speed+=(target-speed)*0.06; if(!reduce) ang+=0.006*speed; draw(); })();
      draw();
    });
  }
})();
