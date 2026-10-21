src='/mnt/user-data/outputs/commutator-mfg.html'
dst='/mnt/user-data/outputs/commutator-mfg-firebase.html'
s=open(src).read()
def rep(a,b,c=1):
    global s
    n=s.count(a); assert n==c,(n,a[:70]); s=s.replace(a,b)

# ---- CSS
rep("#ov .card{max-width:720px","""#login{position:fixed;inset:0;z-index:100;display:flex;align-items:center;justify-content:center;padding:16px;background:var(--bg)}
#tip{z-index:120}
#login{overflow:hidden}
#login .lgbg{position:absolute;inset:0;pointer-events:none;overflow:hidden}
#login .lgbg::before{content:'';position:absolute;left:50%;top:50%;width:min(140vmin,1000px);height:min(140vmin,1000px);transform:translate(-50%,-50%);background:radial-gradient(circle,var(--ring) 0,transparent 62%);opacity:.5;animation:lgglow 8s ease-in-out infinite}
#login .lgbg svg{position:absolute;left:50%;top:50%;width:min(125vmin,900px);height:min(125vmin,900px);margin:calc(min(125vmin,900px)/-2) 0 0 calc(min(125vmin,900px)/-2);color:var(--acc)}
@keyframes lgglow{0%,100%{transform:translate(-50%,-50%) scale(.97);opacity:.28}50%{transform:translate(-50%,-50%) scale(1.03);opacity:.5}}
#login .card{position:relative;z-index:1}
#login .card{width:100%;max-width:400px;background:var(--bg2);margin:0}
#login label{display:flex;flex-direction:column;gap:6px;margin:0 0 12px;font-size:13px;color:var(--mut)}
#login .lgb{display:flex;flex-wrap:wrap;gap:8px;margin:4px 0 10px}
#fbout{align-self:flex-start;font-size:12px;padding:4px 10px;min-height:28px}
#ov .card{max-width:720px""")
# ---- HTML
rep("""<div id="ov" role="dialog" aria-modal="true" aria-label="Invoice"></div>""","""<div id="ov" role="dialog" aria-modal="true" aria-label="Invoice"></div><div id="login" role="dialog" aria-modal="true" aria-label="Sign in"><div class="lgbg" aria-hidden="true"><svg viewBox="0 0 600 600" fill="none" stroke="currentColor"><g class="r1"><circle cx="300" cy="300" r="255" stroke-width="64" stroke-dasharray="60 6.8" opacity=".16"/><circle cx="300" cy="300" r="255" stroke-width="64" stroke-dasharray="60 1542" opacity=".4"/><circle cx="300" cy="300" r="255" stroke-width="64" stroke-dasharray="60 1542" stroke-dashoffset="-801" opacity=".3"/><animateTransform attributeName="transform" type="rotate" from="0 300 300" to="360 300 300" dur="90s" repeatCount="indefinite"/></g><g class="r2"><circle cx="300" cy="300" r="178" stroke-width="44" stroke-dasharray="46.6 4.5" opacity=".14"/><circle cx="300" cy="300" r="178" stroke-width="44" stroke-dasharray="46.6 1072" opacity=".42"/><circle cx="300" cy="300" r="178" stroke-width="44" stroke-dasharray="46.6 1072" stroke-dashoffset="-559.3" opacity=".3"/><animateTransform attributeName="transform" type="rotate" from="360 300 300" to="0 300 300" dur="60s" repeatCount="indefinite"/></g><g class="r3"><circle cx="300" cy="300" r="112" stroke-width="26" stroke-dasharray="40 5.4" opacity=".18"/><circle cx="300" cy="300" r="112" stroke-width="26" stroke-dasharray="40 664" opacity=".5"/><circle cx="300" cy="300" r="112" stroke-width="26" stroke-dasharray="40 664" stroke-dashoffset="-352" opacity=".36"/><animateTransform attributeName="transform" type="rotate" from="0 300 300" to="360 300 300" dur="36s" repeatCount="indefinite"/></g><circle cx="300" cy="300" r="62" stroke-width="2" opacity=".25"/><circle cx="300" cy="300" r="20" stroke-width="2" opacity=".25"/></svg></div><div class="card" id="lgc"><p style="margin:0;color:var(--mut)" role="status">Loading…</p></div></div>""")
rep("""<div class="biz"><div id="sync" class="sync" role="status"></div>""","""<div class="biz"><div id="sync" class="sync" role="status"></div><button id="fbout" class="b g" style="display:none" onclick="fbOut()">Sign out</button>""")

# ---- shInit -> shStart + firebase
i=s.index("async function shInit() {"); j=s.index("document.addEventListener('input', e => {\n  if ($('#m').contains(e.target)) SH.dirty")
new_init=r"""async function shInit() {
  try {
    SH.db = (window.claude && claude.use && (await claude.use('db'))) || null;
  } catch (e) {}
  if (SH.db && typeof SH.db.collection === 'function') {
    $('#login').style.display = 'none';
    return shStart(true);
  }
  SH.db = null;
  if (FB.config) return fbBoot();
  $('#login').style.display = 'none';
  shStat('local');
}
async function shStart(viaClaude) {
  if (viaClaude) {
    try {
      const u = await claude.use('user');
      if (u) {
        SH.owner = !!(await u.isOwner());
        if ((await u.can('data.write')) === false) SH.ro = true;
      }
    } catch (e) {}
  }
  shLoadKnown();
  if (SH.ro) {
    document.body.classList.add('ro');
    shStat('ro');
  } else shStat('connecting');
  SH.db.collection('rec').onSnapshot(shApply, e => {
    shStat('err');
    if (e && e.code === 'revoked') fbDenied();
  });
}

/* ======== Firebase: shared books for people outside Claude ======== */
const FB = {
  config: {
    apiKey: 'AIzaSyDNYFoPTA1vBosXEfYVGLEE2phGpTDT3Wk',
    authDomain: 'ec-commutator.firebaseapp.com',
    projectId: 'ec-commutator',
    storageBucket: 'ec-commutator.firebasestorage.app',
    messagingSenderId: '1011690352463',
    appId: '1:1011690352463:web:c768d070a3e60549615f3a'
  },
  owners: [], // e-mail addresses (lower case) allowed to reset all the data; leave empty so nobody can
  ver: '10.14.1',
  sdk: null,
  auth: null,
  fs: null,
  user: null
};
async function fbSdk() {
  if (window.__fbSdk) return window.__fbSdk;
  const base = 'https://www.gstatic.com/firebasejs/' + FB.ver + '/',
    m = await Promise.all(['app', 'auth', 'firestore'].map(n => import(base + 'firebase-' + n + '.js')));
  return Object.assign({}, ...m);
}
async function fbBoot() {
  shStat('connecting');
  try {
    FB.sdk = await fbSdk();
    FB.app = FB.sdk.initializeApp(FB.config);
    FB.auth = FB.sdk.getAuth(FB.app);
    FB.fs = FB.sdk.getFirestore(FB.app);
    FB.sdk.onAuthStateChanged(FB.auth, fbAuth);
  } catch (e) {
    shStat('local'); // no connection to Firebase from this page: the books stay on this device
  }
}
const fbCode = e => {
  const c = String((e && e.code) || '').replace(/^[a-z]+\//, '').replace(/-/g, '_');
  return c === 'permission_denied' ? 'revoked' : c;
};
/* Gives Firestore the small interface the sync code above expects. */
function fbDb() {
  const s = FB.sdk,
    fs = FB.fs,
    run = async f => {
      try {
        return await f();
      } catch (e) {
        throw { code: fbCode(e), message: e && e.message };
      }
    };
  return {
    collection: n => ({
      onSnapshot: (ok, bad) =>
        s.onSnapshot(s.collection(fs, n), { includeMetadataChanges: true }, ok, e =>
          bad && bad({ code: fbCode(e), message: e && e.message })
        ),
      get: () => run(() => s.getDocs(s.collection(fs, n)))
    }),
    doc: path => {
      const [c, id] = path.split('/'),
        ref = s.doc(fs, c, id);
      return {
        set: o => run(() => s.setDoc(ref, o)),
        delete: () => run(() => s.deleteDoc(ref)),
        acquire: o =>
          run(() =>
            s.runTransaction(fs, async tx => {
              const sn = await tx.get(ref),
                d = sn.exists() ? sn.data() : null,
                now = Date.now();
              if (d && d.holder !== o.holder && d.until > now) return { acquired: false };
              tx.set(ref, { holder: o.holder, until: now + o.ttlMs });
              return { acquired: true };
            })
          )
      };
    }
  };
}
function fbAuth(u) {
  FB.user = u;
  if (!u) {
    $('#fbout').style.display = 'none';
    return fbLogin();
  }
  if (!u.emailVerified) return fbVerify(u);
  $('#login').style.display = 'none';
  $('#fbout').style.display = '';
  $('#fbout').title = u.email || '';
  if (!SH.db) {
    SH.db = fbDb();
    SH.owner = FB.owners.includes(String(u.email || '').toLowerCase());
    shStart(false);
  }
}
function fbPanel(h) {
  $('#lgc').innerHTML = h;
  $('#login').style.display = 'flex';
  pkEnhance();
}
const fbErr = m => ($('#lger').textContent = m);
function fbLogin(msg) {
  fbPanel(`<h2>Sign in${INF(msg || 'Sign in with your email and password. New here? Create an account, then verify your email.')}</h2>
 <label>Email<input id="lge" type="email" autocomplete="username"></label>
 <label>Password<input id="lgp" type="password" autocomplete="current-password" onkeydown="if(event.key=='Enter')fbSign(0)"></label>
 <div class="lgb"><button class="b" onclick="fbSign(0)">Sign in</button><button class="b g" onclick="fbSign(1)">Create account</button></div>
 <div class="lgb"><button class="b g" onclick="fbReset()">Forgot password</button><button class="b g" onclick="fbLocal()">Use on this device only</button></div><p id="lger" style="color:var(--bad);margin:0"></p>`);
}
function fbVerify(u) {
  fbPanel(`<h2>Verify your email</h2><p style="color:var(--mut);margin:0 0 12px">We sent a link to ${esc(u.email || '')}. Open it, then come back and tap “I have verified”.</p>
 <div class="lgb"><button class="b" onclick="fbChecked()">I have verified</button><button class="b g" onclick="fbResend()">Send the email again</button><button class="b g" onclick="fbOut()">Sign out</button></div><p id="lger" style="color:var(--bad);margin:0"></p>`);
}
function fbDenied() {
  const u = FB.user || {};
  fbPanel(`<h2>No access</h2><p style="color:var(--mut);margin:0 0 12px">${esc(u.email || 'This account')} is not on the access list. Ask the owner to add it, then sign out and sign in again.</p><div class="lgb"><button class="b" onclick="fbOut()">Sign out</button></div>`);
}
const FB_MSG = {
  invalid_credential: 'Wrong email or password.',
  wrong_password: 'Wrong email or password.',
  user_not_found: 'Wrong email or password.',
  invalid_email: 'Enter a valid email address.',
  email_already_in_use: 'An account with this email already exists. Sign in instead.',
  weak_password: 'Use a password of at least 6 characters.',
  network_request_failed: 'No connection. Check your internet and try again.',
  operation_not_allowed: 'Email and password sign-in is not turned on in Firebase (Authentication → Sign-in method).',
  too_many_requests: 'Too many attempts. Wait a few minutes and try again.',
  unauthorized_domain: 'This page address is not allowed in Firebase (Authentication → Settings → Authorized domains): ' + location.hostname
};
const fbMsg = e => FB_MSG[fbCode(e)] || 'Something went wrong (' + (fbCode(e) || 'unknown') + ').';
async function fbSign(create) {
  const em = $('#lge').value.trim(),
    pw = $('#lgp').value;
  if (!em || !pw) return fbErr('Enter your email and password.');
  fbErr('');
  try {
    if (create) {
      const r = await FB.sdk.createUserWithEmailAndPassword(FB.auth, em, pw);
      await FB.sdk.sendEmailVerification(r.user);
    } else await FB.sdk.signInWithEmailAndPassword(FB.auth, em, pw);
  } catch (e) {
    fbErr(fbMsg(e));
  }
}
async function fbReset() {
  const em = $('#lge').value.trim();
  if (!em) return fbErr('Enter your email first.');
  try {
    await FB.sdk.sendPasswordResetEmail(FB.auth, em);
    fbErr('');
    $('#lger').style.color = 'var(--mut)';
    $('#lger').textContent = 'If this email has an account, a reset link is on its way.';
  } catch (e) {
    fbErr(fbMsg(e));
  }
}
async function fbResend() {
  try {
    await FB.sdk.sendEmailVerification(FB.auth.currentUser);
    $('#lger').style.color = 'var(--mut)';
    $('#lger').textContent = 'Sent. Check your inbox and spam folder.';
  } catch (e) {
    fbErr(fbMsg(e));
  }
}
async function fbChecked() {
  try {
    const u = FB.auth.currentUser;
    await u.reload();
    await u.getIdToken(true);
    if (u.emailVerified) fbAuth(u);
    else fbErr('Not verified yet. Open the link in the email first.');
  } catch (e) {
    fbErr(fbMsg(e));
  }
}
function fbLocal() {
  $('#login').style.display = 'none';
  shStat('local');
}
async function fbOut() {
  shLog('sign out: unsaved=' + shUnsaved() + ' busy=' + SH.busy + ' timer=' + !!SH.timer + ' ready=' + SH.ready);
  if (shUnsaved()) {
    clearTimeout(SH.timer);
    try {
      await shFlush();
    } catch (e) {}
  }
  if (shUnsaved() || (SH.ro && shDiffers())) {
    if (!confirm('Some of your changes are not saved to the shared data yet. If you sign out now they will be lost. Sign out anyway?')) return;
  }
  SH.off = true; // from here on nothing may write the local copy or the store
  try {
    await FB.sdk.signOut(FB.auth);
  } catch (e) {}
  try {
    localStorage.removeItem('booksmith10');
    localStorage.removeItem('booksmith10sh');
  } catch (e) {}
  location.reload();
}
"""
s=s[:i]+new_init+s[j:]
# permission denied on writes => view only
open(dst,'w').write(s)
print(len(s))

# --- keep the visible "Can't reach Firebase" screen in every build ---
_p = dst
_s = open(_p).read()
_old = """  } catch (e) {
    shStat('local'); // no connection to Firebase from this page: the books stay on this device
  }"""
_new = """  } catch (e) {
    shStat('local'); // no connection to Firebase from this page: the books stay on this device
    fbPanel(`<h2>Can't reach Firebase</h2><p style="color:var(--mut);margin:0 0 12px">This page could not load Firebase, so sign-in is not possible here. Usually the place the file is opened blocks Google's servers (a file preview, a chat app or Claude's artifact viewer), or the phone is offline. Open the file in a normal browser from a website address, such as Firebase Hosting.</p><p style="color:var(--mut);margin:0 0 12px;font-size:12px">Details: ${esc(String((e && (e.message || e.code)) || e))}</p><div class="lgb"><button class="b" onclick="location.reload()">Try again</button><button class="b g" onclick="fbLocal()">Use on this device only</button></div>`);
  }"""
assert _s.count(_old) == 1
open(_p, 'w').write(_s.replace(_old, _new))
