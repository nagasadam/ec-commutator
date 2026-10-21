"""Builds test/index.html: the live Firebase build pointed at the TEST Firebase project,
username+password sign-in (no email verification), own storage keys, sample data seed.
usage: python3 tools/build_test_fb.py tools/test_firebase_config.json"""
import json,sys,re
cfg=json.load(open(sys.argv[1]))
s=open('index.html').read()
def rep(a,b,c=1):
    global s
    assert s.count(a)==c,(s.count(a),a[:60]);s=s.replace(a,b)
# 1 test project config
i=s.index('config: {');j=s.index('},',i)+2
s=s[:i]+'config: '+json.dumps(cfg,indent=4)+','+s[j:]
# 2 own storage keys so the real site's data on the same origin is never touched
s=s.replace('booksmith10','ectest10')
# 3 no email verification
rep("if (!u.emailVerified) return fbVerify(u);","")
rep("      await FB.sdk.sendEmailVerification(r.user);\n","")
# 4 username sign-in: tester1 -> tester1@ec-test.app
rep("const em = $('#lge').value.trim(),\n    pw = $('#lgp').value;","let em = $('#lge').value.trim();\n  const pw = $('#lgp').value;\n  if (em && em.indexOf('@') < 0) em = em.toLowerCase() + '@ec-test.app';")
rep('<label>Email<input id="lge" type="email" autocomplete="username"></label>','<label>Username<input id="lge" type="text" autocomplete="username" autocapitalize="none"></label>')
rep("Sign in with your email and password. New here? Create an account, then verify your email.","Test copy: sign in with the username and password you were given.")
# 5 sample data seed + banner
seed=open('tools/test_seed.json').read().strip()
inj="""<script>
/* TEST COPY: separate Firebase project and storage keys; first sign-in loads the sample data */
(function(){var K='ectest10',SEED=%s;
try{if(!localStorage.getItem(K))localStorage.setItem(K,JSON.stringify(SEED))}catch(e){}
document.addEventListener('DOMContentLoaded',function(){var d=document.createElement('div');
d.style.cssText='position:fixed;left:50%%;bottom:10px;transform:translateX(-50%%);z-index:200;background:#f0a063;color:#1b1209;font:600 12px system-ui,sans-serif;padding:6px 12px;border-radius:99px;box-shadow:0 4px 18px rgba(0,0,0,.4);pointer-events:none';
d.textContent='TEST COPY \\u00b7 not the real books';document.body.appendChild(d)})})();
</script>"""%json.dumps(json.loads(seed))
s=s.replace('<script>',inj+'\n<script>',1)
import os;os.makedirs('test',exist_ok=True);open('test/index.html','w').write(s);print(len(s))
