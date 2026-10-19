// SherpaWare service worker (version 03eff8978f)
var CACHE='sherpaware-03eff8978f';
var CORE=['./','index.html','manifest.webmanifest','icon-192.png','icon-512.png','icon-180.png'];
self.addEventListener('install',function(e){e.waitUntil(caches.open(CACHE).then(function(c){return c.addAll(CORE)}).then(function(){return self.skipWaiting()}))});
self.addEventListener('activate',function(e){e.waitUntil(caches.keys().then(function(ks){return Promise.all(ks.filter(function(k){return k!==CACHE&&k.indexOf('sherpaware-')===0}).map(function(k){return caches.delete(k)}))}).then(function(){return self.clients.claim()}))});
self.addEventListener('fetch',function(e){
  var r=e.request;if(r.method!=='GET')return;
  var u=new URL(r.url);
  // Weather and other live data always go to the network, never from cache.
  if(u.hostname.indexOf('aviationweather.gov')>=0)return;
  if(r.mode==='navigate'){e.respondWith(caches.match('index.html').then(function(m){return m||fetch(r)}));return}
  e.respondWith(caches.match(r).then(function(m){
    if(m)return m;
    return fetch(r).then(function(res){
      if(res&&(res.ok||res.type==='opaque')&&(u.origin===location.origin||u.hostname.indexOf('fonts.g')===0)){var cp=res.clone();caches.open(CACHE).then(function(c){c.put(r,cp)})}
      return res}).catch(function(){return m})}))});
