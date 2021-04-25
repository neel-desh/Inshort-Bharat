const staticCacheName = 'inshortbharat-v1';
const dynamicCacheName = 'inshortbharat-dynamic-v1';
const assets = [
    "/offline/index.html",
    "/offline/detailpage.html",
    "/offline/fallback.html",
    "/static/images/error.png",
    "/static/assets/css/bootstrap.min.css",
    "https://cdn.ampproject.org/amp-story-player-v0.js",
    "https://cdn.ampproject.org/amp-story-player-v0.css" ,
    "/static/assets/css/fontawesome-all.min.css",
    "/static/assets/css/themify-icons.css" ,
    "/static/assets/css/et-line.css" ,
    "/static/assets/css/bootstrap-select.min.css" ,
    "/static/assets/css/plyr.css" ,
    "/static/assets/css/flag.css" ,
    "/static/assets/css/slick.css" , 
    "/static/assets/css/owl.carousel.min.css" ,
    "/static/assets/css/jquery.nstSlider.min.css" ,
    "/static/css/main.css",
    "https://fonts.googleapis.com/css?family=Poppins:400,500,600%7CRoboto:300i,400,500" ,
    "https://cdnjs.cloudflare.com/ajax/libs/jspdf/1.3.4/jspdf.min.js",
    "/static/assets/js/jquery.min.js",
    "/static/assets/js/popper.min.js",
    "/static/assets/js/bootstrap.min.js",
    "/static/assets/js/feather.min.js",
    "/static/assets/js/bootstrap-select.min.js",
    "/static/assets/js/jquery.nstSlider.min.js",
    "/static/assets/js/owl.carousel.min.js",
    "/static/assets/js/visible.js",
    "/static/assets/js/jquery.countTo.js",
    "/static/assets/js/chart.js",
    "/static/assets/js/plyr.js",
    "/static/assets/js/tinymce.min.js",
    "/static/assets/js/slick.min.js",
    "/static/assets/js/jquery.ajaxchimp.min.js",
    "/static/js/custom.js",
];

// cache size limit function
// const limitCacheSize = (name, size) => {
//   caches.open(name).then(cache => {
//     cache.keys().then(keys => {
//       if(keys.length > size){
//         cache.delete(keys[0]).then(limitCacheSize(name, size));
//       }
//     });
//   });
// };

// install event
self.addEventListener('install', evt => {
  //console.log('service worker installed');
  evt.waitUntil(
    caches.open(staticCacheName).then((cache) => {
      console.log('caching shell assets');
      cache.addAll(assets);
          })
  );
});

// activate event
self.addEventListener('activate', evt => {
  console.log('service worker activated');
  
  



});

// fetch events
self.addEventListener('fetch', evt => {
  if(evt.request.url.indexOf('firestore.googleapis.com') === -1){
    evt.respondWith(
      caches.match(evt.request).then(cacheRes => {
        return cacheRes || fetch(evt.request).then(fetchRes => {
          return caches.open(dynamicCacheName).then(cache => {
            cache.put(evt.request.url, fetchRes.clone());
            // check cached items size
            limitCacheSize(dynamicCacheName, 15);
            return fetchRes;
          })
        });
      }).catch(() => {
        if(evt.request.url.indexOf('.html') > -1){
          return caches.match('/offline/fallback.html');
        } 
      })
    );
  }
});

