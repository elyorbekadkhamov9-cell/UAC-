/* Renders news cards from news-uac.js and news-world.js. All text goes in with textContent. */
(function(){
  "use strict";
  var MON=["yanvar","fevral","mart","aprel","may","iyun","iyul","avgust","sentabr","oktabr","noyabr","dekabr"];
  function nice(d){ var p=String(d||"").split("-"); return p.length===3?(+p[2])+"-"+MON[p[1]-1]+", "+p[0]:""; }
  var MS=["yan","fev","mar","apr","may","iyn","iyl","avg","sen","okt","noy","dek"];
  function short(d){ var p=String(d||"").split("-"); return p.length===3?(+p[2])+" "+MS[p[1]-1]:"UAC"; }
  function el(tag,cls,text){ var e=document.createElement(tag); if(cls) e.className=cls; if(text!=null) e.textContent=text; return e; }
  var KIND={video:"Video",photo:"Post",file:"Fayl","":"Post"};
  function cover(label,big,img,it){
    var c=el("span","nc-cover"); c.appendChild(el("span","nc-big",big)); c.appendChild(el("span","nc-lbl",label));
    if(img){ var im=new Image(); im.alt=""; im.loading="lazy"; im.onerror=function(){ im.remove(); c.classList.remove("nc-plain"); c.style.background=""; }; im.src=img; c.appendChild(im);
      if(it&&it.fit==="contain"){ c.classList.add("nc-plain"); if(it.bg) c.style.background=it.bg; } }
    return c;
  }
  function credit(it){ if(!it.credit) return null; var p=el("span","nc-credit"); p.appendChild(document.createTextNode("Rasm: "));
    if(it.credit.url){ var a=el("a","",it.credit.text); a.href=it.credit.url; a.target="_blank"; a.rel="noopener"; p.appendChild(a); } else p.appendChild(document.createTextNode(it.credit.text)); return p; }
  function uacCard(it){
    var a=el("a","ncard"); a.href=it.url; a.target="_blank"; a.rel="noopener";
    a.appendChild(cover(KIND[it.media]||"Post",short(it.date),it.img));
    var b=el("span","nc-body"); b.appendChild(el("span","nc-meta",nice(it.date)+" · Telegram"));
    b.appendChild(el("span","nc-title",it.title)); if(it.text) b.appendChild(el("span","nc-text",it.text));
    a.appendChild(b); return a;
  }
  function worldCard(it){
    var a=el("a","ncard"); a.href="yangiliklar.html#"+it.id;
    a.appendChild(cover(it.cat,it.cover,it.img||"",it));
    var b=el("span","nc-body"); b.appendChild(el("span","nc-meta",nice(it.date)+" · Dunyo kimyosi"));
    b.appendChild(el("span","nc-title",it.title)); b.appendChild(el("span","nc-text",it.lead));
    if(it.credit) b.appendChild(el("span","nc-credit","Rasm: "+it.credit.text));
    a.appendChild(b); return a;
  }
  function empty(box,msg){ box.appendChild(el("p","empty",msg)); }
  window.UACFeed={
    nice:nice,
    uacCards:function(box,n){ var L=(window.NEWS_UAC||[]).slice(0,n); if(!L.length) return empty(box,"Hozircha postlar yuklanmadi. Yangiliklarni Telegram kanalimizda o‘qing.");
      L.forEach(function(it){ box.appendChild(uacCard(it)); }); },
    worldCards:function(box,n){ (window.NEWS_WORLD||[]).slice(0,n).forEach(function(it){ box.appendChild(worldCard(it)); }); },
    mixed:function(box){ var u=(window.NEWS_UAC||[])[0], w=(window.NEWS_WORLD||[])[0]; if(u) box.appendChild(uacCard(u)); if(w) box.appendChild(worldCard(w)); },
    worldArticles:function(box){ var L=window.NEWS_WORLD||[]; if(!L.length) return empty(box,"Hozircha yangilik yo‘q.");
      L.forEach(function(it){
        var art=el("article","witem"); art.id=it.id; art.appendChild(cover(it.cat,it.cover,it.img||"",it));
        var d=el("div"); d.appendChild(el("span","nc-meta",nice(it.date)+" · "+it.cat)); d.appendChild(el("h3","",it.title)); d.appendChild(el("p","lead",it.lead));
        var det=el("details"), sum=el("summary","","To‘liq o‘qish"), more=el("div","more"); det.appendChild(sum);
        (it.body||[]).forEach(function(p){ more.appendChild(el("p","",p)); }); det.appendChild(more); d.appendChild(det);
        var s=el("p","src"); s.appendChild(document.createTextNode("Manba: "));
        (it.src||[]).forEach(function(x,i){ if(i) s.appendChild(document.createTextNode(", ")); var a=el("a","",x.name); a.href=x.url; a.target="_blank"; a.rel="noopener"; s.appendChild(a); });
        d.appendChild(s); var cr=credit(it); if(cr){ cr.className="src"; d.appendChild(cr); } art.appendChild(d); box.appendChild(art);
        if(location.hash==="#"+it.id) det.open=true;
      });
      if(location.hash){ var t=document.getElementById(location.hash.slice(1)); if(t) setTimeout(function(){ t.scrollIntoView({block:"start"}); },80); }
    }
  };
})();
