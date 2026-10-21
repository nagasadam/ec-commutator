import json,time
from playwright.sync_api import sync_playwright
f=0
def chk(c,m):
    global f
    print(('PASS ' if c else 'FAIL ')+m)
    if not c:f+=1
USERS={'a@x.com':{'pw':'secret1','ver':False},'b@x.com':{'pw':'secret2','ver':True},'z@x.com':{'pw':'secret3','ver':True}}
ALLOW={'a@x.com','b@x.com'}
DOCS={}
def u_sign(email,pw,create):
    if create:
        if email in USERS:return {'err':'auth/email-already-in-use'}
        if len(pw)<6:return {'err':'auth/weak-password'}
        USERS[email]={'pw':pw,'ver':False};return {'email':email,'ver':False}
    u=USERS.get(email)
    if not u or u['pw']!=pw:return {'err':'auth/invalid-credential'}
    return {'email':email,'ver':u['ver']}
def u_state(email):return {'email':email,'ver':USERS[email]['ver']}
def f_list(email):
    if email not in ALLOW or not USERS[email]['ver']:return {'err':'permission-denied'}
    return {'docs':[[k,json.loads(v)] for k,v in DOCS.items()]}
def f_set(email,id,data):
    if email not in ALLOW or not USERS[email]['ver']:return {'err':'permission-denied'}
    DOCS[id]=json.dumps(data);return {}
def f_del(email,id):
    if email not in ALLOW or not USERS[email]['ver']:return {'err':'permission-denied'}
    DOCS.pop(id,None);return {}
MOCK="""
window.__fbSdk=(()=>{let user=null,cbs=[];const E=o=>{const e=new Error(o.err);e.code=o.err;return e};
 const mk=r=>({email:r.email,emailVerified:r.ver,async reload(){const s=await window.u_state(this.email);this.emailVerified=s.ver},async getIdToken(){}});
 const auth={get currentUser(){return user}};
 const fire=()=>cbs.forEach(c=>c(user));
 const em=()=>user&&user.email;
 return {initializeApp:()=>({}),getAuth:()=>auth,getFirestore:()=>({}),
  onAuthStateChanged:(a,cb)=>{cbs.push(cb);setTimeout(async()=>{const m=localStorage.getItem('__mu');if(m&&!user){const r=await window.u_state(m);user=mk(r)}cb(user)},0)},
  signInWithEmailAndPassword:async(a,e,p)=>{const r=await window.u_sign(e,p,false);if(r.err)throw E(r);user=mk(r);localStorage.setItem('__mu',r.email);fire()},
  createUserWithEmailAndPassword:async(a,e,p)=>{const r=await window.u_sign(e,p,true);if(r.err)throw E(r);user=mk(r);setTimeout(fire,0);return {user}},
  sendEmailVerification:async()=>{window.__sent=(window.__sent||0)+1},sendPasswordResetEmail:async()=>{},
  signOut:async()=>{user=null;localStorage.removeItem('__mu');fire()},
  collection:(fs,n)=>({n}),doc:(fs,c,id)=>({c,id}),
  onSnapshot:(ref,opts,ok,bad)=>{let last='';const tick=async()=>{const r=await window.f_list(em());if(r.err){if(bad&&last!=='E'){last='E';const e=new Error(r.err);e.code=r.err;bad(e)}return}
     const js=JSON.stringify(r.docs);if(js!==last){last=js;ok({docs:r.docs.map(([id,d])=>({id,data:()=>d})),metadata:{fromCache:false}})}};tick();setInterval(tick,150)},
  getDocs:async()=>{const r=await window.f_list(em());if(r.err)throw E(r);return {docs:r.docs.map(([id,d])=>({id,data:()=>d})),metadata:{fromCache:false}}},
  setDoc:async(ref,d)=>{const r=await window.f_set(em(),ref.c+'/'+ref.id,d);if(r.err)throw E(r)},
  deleteDoc:async(ref)=>{const r=await window.f_del(em(),ref.c+'/'+ref.id);if(r.err)throw E(r)},
  runTransaction:async(fs,fn)=>fn({get:async()=>({exists:()=>false,data:()=>null}),set:()=>{}})}})();
"""
def newpage(br):
    ctx=br.new_context(viewport={'width':1200,'height':800})
    for n,fn in (('u_sign',u_sign),('u_state',u_state),('f_list',f_list),('f_set',f_set),('f_del',f_del)):ctx.expose_function(n,fn)
    ctx.add_init_script(MOCK)
    pg=ctx.new_page();pg.errs=[];pg.on('pageerror',lambda e:pg.errs.append(str(e)));return ctx,pg
URL='file:///mnt/user-data/outputs/commutator-mfg-firebase.html'
with sync_playwright() as p:
    br=p.chromium.launch()
    ctx,pg=newpage(br);pg.goto(URL);pg.wait_for_selector('#m');ev=pg.evaluate
    pg.wait_for_selector('#login',state='visible',timeout=5000)
    chk('Sign in' in pg.inner_text('#lgc'),'login screen shows when signed out')
    pg.fill('#lge','a@x.com');pg.fill('#lgp','wrong');pg.click("#lgc button:text-is('Sign in')");pg.wait_for_timeout(300)
    chk('Wrong email or password' in pg.inner_text('#lger'),'wrong password refused')
    pg.fill('#lgp','secret1');pg.click("#lgc button:text-is('Sign in')");pg.wait_for_timeout(400)
    chk('Verify your email' in pg.inner_text('#lgc'),'unverified account is asked to verify')
    pg.click("#lgc button:text-is('I have verified')");pg.wait_for_timeout(300)
    chk('Not verified yet' in pg.inner_text('#lger'),'still unverified: told so')
    USERS['a@x.com']['ver']=True
    pg.click("#lgc button:text-is('I have verified')");pg.wait_for_timeout(1500)
    chk(not pg.is_visible('#login'),'verified: login closes')
    chk(ev("SH.db!==null")==True and 'Shared' in pg.inner_text('#sync'),'connected: status says Shared')
    # seeding: this device's books published
    pg.wait_for_timeout(1500);n0=len(DOCS);chk(n0>5,'books published to the store (%d docs)'%n0)
    # enter data
    ev("(()=>{const b=B();b.cust.push({id:'c1',name:'Acme Pvt Ltd',type:'company',gstin:'',phone:'',addr:'',open:0});save();R()})()");pg.wait_for_timeout(1500)
    chk(any('c1' in k for k in DOCS),'a new customer reaches the store')
    # second person on another device
    ctx2,pg2=newpage(br);pg2.goto(URL);pg2.wait_for_selector('#login',state='visible',timeout=5000)
    pg2.fill('#lge','b@x.com');pg2.fill('#lgp','secret2');pg2.click("#lgc button:text-is('Sign in')");pg2.wait_for_timeout(2500)
    chk(not pg2.is_visible('#login'),'second person signs in')
    chk(pg2.evaluate("B().cust.some(c=>c.id=='c1')"),'second device receives the first one\'s customer')
    pg2.evaluate("(()=>{const b=B();b.cust.push({id:'c2',name:'Beta Ltd',type:'company',gstin:'',phone:'',addr:'',open:0});save()})()");pg2.wait_for_timeout(2500)
    chk(ev("B().cust.some(c=>c.id=='c2')"),'first device receives the second one\'s customer')
    # delete propagates
    pg2.evaluate("(()=>{const b=B();b.cust=b.cust.filter(c=>c.id!='c2');save()})()");pg2.wait_for_timeout(2500)
    chk(not any('c2' in k for k in DOCS) and not ev("B().cust.some(c=>c.id=='c2')"),'a deletion propagates')
    # refresh keeps data
    pg.reload();pg.wait_for_selector('#m');pg.wait_for_timeout(2500)
    chk(ev("B().cust.some(c=>c.id=='c1')") ,'refresh keeps the data')
    # sign out clears local copy
    pg.click('#fbout');pg.wait_for_timeout(800)
    chk(ev("localStorage.getItem('booksmith10')")is None or 'c1' not in ev("localStorage.getItem('booksmith10')||''"),'sign out clears the local copy')
    pg.wait_for_selector('#login',state='visible',timeout=5000)
    chk(not ev("(window.B&&B().cust||[]).some(c=>c.id=='c1')"),'after sign-out the page is empty until sign-in')
    # not on the list
    ctx3,pg3=newpage(br);pg3.goto(URL);pg3.wait_for_selector('#login',state='visible',timeout=5000)
    pg3.fill('#lge','z@x.com');pg3.fill('#lgp','secret3');pg3.click("#lgc button:text-is('Sign in')");pg3.wait_for_timeout(2500)
    chk('No access' in pg3.inner_text('#lgc'),'account not on the access list sees No access')
    # create account
    ctx4,pg4=newpage(br);pg4.goto(URL);pg4.wait_for_selector('#login',state='visible',timeout=5000)
    pg4.fill('#lge','new@x.com');pg4.fill('#lgp','abc');pg4.click("#lgc button:text-is('Create account')");pg4.wait_for_timeout(400)
    chk('at least 6' in pg4.inner_text('#lger'),'short password refused')
    pg4.fill('#lgp','abcdef');pg4.click("#lgc button:text-is('Create account')");pg4.wait_for_timeout(600)
    chk('Verify your email' in pg4.inner_text('#lgc') and pg4.evaluate("window.__sent")==1,'new account: verification email sent')
    # local only
    ctx5,pg5=newpage(br);pg5.goto(URL);pg5.wait_for_selector('#login',state='visible',timeout=5000);pg5.click("#lgc button:text-is('Use on this device only')")
    chk(not pg5.is_visible('#login') and 'device only' in pg5.inner_text('#sync'),'use on this device only works')
    for q in (pg,pg2,pg3,pg4,pg5):
        if q.errs:print('ERRS',q.errs)
    chk(not any(q.errs for q in (pg,pg2,pg3,pg4,pg5)),'no js errors');print('failed',f)
