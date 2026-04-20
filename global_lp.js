
// ── GLOBAL LONG PRESS ───────────────────
var _lpTimer=null,_lpFired=false;
var _lpD=[
  {a:'data-sid', f:function(el){if(window.supp_lpAction)window.supp_lpAction(el);}},
  {a:'data-pid', f:function(el){if(window.haut_lpAction)window.haut_lpAction(el);}},
  {a:'data-gid', f:function(el){if(window.get_lpAction)window.get_lpAction(el);}},
  {a:'data-iid', f:function(el){if(window.ern_lpAction)window.ern_lpAction(el);}},
  {a:'data-eid', f:function(el){if(window.akt_lpAction)window.akt_lpAction(el);if(window.regen_lpAction)window.regen_lpAction(el);}},
  {a:'data-kid', f:function(el){if(window.fam_lpAction)window.fam_lpAction(el);}},
  {a:'data-medid',f:function(el){if(window.med_lpAction)window.med_lpAction(el);}},
  {a:'data-entryid',f:function(el){if(window.med_lpEntryAction)window.med_lpEntryAction(el);}},
  {a:'data-entry',f:function(el){if(window.ern_lpEntryAction)window.ern_lpEntryAction(el);}},
];
document.addEventListener('pointerdown',function(e){
  _lpFired=false;
  for(var i=0;i<_lpD.length;i++){
    var t=e.target.closest('['+_lpD[i].a+']');
    if(t){var fn=_lpD[i].f,el=t;_lpTimer=setTimeout(function(){_lpFired=true;fn(el);},500);return;}
  }
});
document.addEventListener('pointerup',function(){clearTimeout(_lpTimer);});
document.addEventListener('pointercancel',function(){clearTimeout(_lpTimer);});
document.addEventListener('click',function(e){
  if(_lpFired){
    _lpFired=false;
    e.stopImmediatePropagation();
    e.preventDefault();
    // Reset after short delay to allow next interaction
    setTimeout(function(){_lpFired=false;},100);
  }
},true);
