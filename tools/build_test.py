import json,re
src=open('/mnt/user-data/outputs/commutator-mfg.html').read()
state=open('test_seed.json').read().strip()
inject="""<script>
/* TEST COPY: seeds sample data into this browser only; nothing is sent anywhere */
(function(){
  var K='booksmith10',SEED=%s,u=(new URLSearchParams(location.search).get('u')||'').replace(/[^0-9]/g,'').slice(0,1);
  window.TEST_RESET=function(){try{localStorage.setItem(K,JSON.stringify(SEED))}catch(e){}location.reload()};
  try{if(!localStorage.getItem(K))localStorage.setItem(K,JSON.stringify(SEED))}catch(e){}
  document.addEventListener('DOMContentLoaded',function(){
    var d=document.createElement('div');
    d.style.cssText='position:fixed;left:50%%;bottom:10px;transform:translateX(-50%%);z-index:200;background:#f0a063;color:#1b1209;font:600 12px system-ui,sans-serif;padding:7px 12px;border-radius:99px;box-shadow:0 4px 18px rgba(0,0,0,.4);display:flex;gap:10px;align-items:center;max-width:94vw';
    d.innerHTML='<span>TEST COPY'+(u?' · Tester '+u:'')+' · data stays in this browser</span><button style="all:unset;cursor:pointer;text-decoration:underline" onclick="if(confirm(\\'Reset all test data to the starting sample?\\'))TEST_RESET()">Reset sample data</button>';
    document.body.appendChild(d);
  });
})();
</script>"""%json.dumps(json.loads(state))
out=src.replace('<script>',inject+'\n<script>',1)
out=out.replace('<title>','<title>[TEST] ',1) if '<title>' in out else out
open('/mnt/user-data/outputs/commutator-test.html','w').write(out)
print(len(out))
