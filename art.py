#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════╗
║  N E U R O // W A T C H   ·   Neural System HUD  v4.0    ║
║  Code Olympics 2026 · vars≤3chars · ≤650 lines · Python  ║
║  100% LIVE real-time system data via psutil               ║
╚═══════════════════════════════════════════════════════════╝
"""
import os,sys,time,math,random,shutil,platform,datetime,io
import psutil

_WN=sys.platform=="win32"
if _WN:
    import msvcrt
    def _ea():
        try:
            import ctypes; k=ctypes.windll.kernel32
            k.SetConsoleMode(k.GetStdHandle(-11),7)
            k.SetConsoleMode(k.GetStdHandle(-10),7)
        except: pass
    _ea()
else:
    import select,tty,termios

# ── one-shot priming so first cpu_percent call is valid ──────────
psutil.cpu_percent(interval=None)
psutil.cpu_percent(percpu=True,interval=None)

# ── net/disk delta state ─────────────────────────────────────────
_pn=psutil.net_io_counters()    # prev net snapshot
_pd=psutil.disk_io_counters()   # prev disk snapshot
_pt=time.time()                 # prev tick timestamp
_tx=0.0; _rx=0.0                # net KB/s
_dr=0.0; _dw=0.0                # disk KB/s

# ── LIVE sensors ─────────────────────────────────────────────────
def _cv(): return psutil.cpu_percent(interval=None)
def _mv(): return psutil.virtual_memory().percent
def _dv():
    try: return psutil.disk_usage('/').percent
    except:
        try: return psutil.disk_usage('C:\\').percent
        except: return 0.0
def _tv():
    try:
        t=psutil.sensors_temperatures()
        for k in("coretemp","cpu_thermal","k10temp","acpitz","cpu-thermal"):
            if k in t and t[k]: return t[k][0].current
    except: pass
    return None          # None = not available on this hw
def _bv():
    if not hasattr(psutil,"battery"): return None
    try: b=psutil.battery(); return (b.percent,b.power_plugged) if b else None
    except: return None
def _pc(): return len(psutil.pids())
def _up():
    bt=psutil.boot_time()
    up=int(time.time()-bt)
    hh,r=divmod(up,3600); mm,ss=divmod(r,60)
    return f"{hh}h{mm:02d}m{ss:02d}s"
def _vm():
    vm=psutil.virtual_memory()
    ca=getattr(vm,"cached",0); bf=getattr(vm,"buffers",0)
    return vm.total,vm.used,vm.available,ca,bf
def _sw():
    s=psutil.swap_memory(); return s.percent,s.used,s.total
def _fi():
    try: f=psutil.cpu_freq(); return f.current if f else 0.0
    except: return 0.0

def _nd():
    """Return (tx_kbs, rx_kbs, disk_r_kbs, disk_w_kbs) since last call."""
    global _pn,_pd,_pt,_tx,_rx,_dr,_dw
    nw=time.time(); dt=max(0.01,nw-_pt); _pt=nw
    cn=psutil.net_io_counters()
    _tx=(cn.bytes_sent-_pn.bytes_sent)/dt/1024
    _rx=(cn.bytes_recv-_pn.bytes_recv)/dt/1024
    _pn=cn
    try:
        cd=psutil.disk_io_counters()
        _dr=(cd.read_bytes-_pd.read_bytes)/dt/1024
        _dw=(cd.write_bytes-_pd.write_bytes)/dt/1024
        _pd=cd
    except: _dr=_dw=0.0
    return max(0,_tx),max(0,_rx),max(0,_dr),max(0,_dw)

def _tp():
    """Top 8 processes by CPU%."""
    try:
        ps=[]
        for p in psutil.process_iter(["name","cpu_percent","memory_percent","status"]):
            try:
                i=p.info
                ps.append((i["cpu_percent"] or 0,i["memory_percent"] or 0,
                            i["name"] or "?",p.pid,i["status"] or "?"))
            except: pass
        return sorted(ps,reverse=True)[:8]
    except: return []

# ── terminal & colour ─────────────────────────────────────────────
W,H=shutil.get_terminal_size((140,38))
C={
    "r":"\033[91m","g":"\033[92m","y":"\033[93m","b":"\033[94m",
    "m":"\033[95m","c":"\033[96m","w":"\033[97m","d":"\033[90m",
    "R":"\033[31m","G":"\033[32m","Y":"\033[33m","B":"\033[34m",
    "0":"\033[0m", "!":"\033[1m", "~":"\033[3m", "^":"\033[7m",
}
SPK="▁▂▃▄▅▆▇█"

def cl(s,*cc): return "".join(C.get(x,"") for x in cc)+str(s)+C["0"]
def mv(r,c):   return f"\033[{r};{c}H"
def hid():     print("\033[?25l",end="",flush=True)
def shw():     print("\033[?25h",end="",flush=True)
def put(b,r,c,s): b.write(mv(r,c)+s)

# ── history buffers ───────────────────────────────────────────────
_HW=120
_ch=[0.0]*_HW; _mh=[0.0]*_HW; _dh=[0.0]*_HW
_th=[0.0]*_HW; _nh=[(0.0,0.0)]*_HW; _io=[(0.0,0.0)]*_HW
_fm=0; _sl=0; _fp=0; _ft=time.time()

def _tk():
    global _ch,_mh,_dh,_th,_nh,_io
    tx,rx,dr,dw=_nd()
    _ch=(_ch+[_cv()])[-_HW:]
    _mh=(_mh+[_mv()])[-_HW:]
    _dh=(_dh+[_dv()])[-_HW:]
    tv=_tv(); _th=(_th+[tv if tv is not None else _th[-1]])[-_HW:]
    _nh=(_nh+[(tx,rx)])[-_HW:]
    _io=(_io+[(dr,dw)])[-_HW:]

# ── render helpers ────────────────────────────────────────────────
_GP=["B","b","c","g","G"]
_RP=["R","r","y","Y","w"]

def gba(v,w=32):
    pl=_GP if v<60 else _RP
    fi=int(v/100*w); out=""
    for i in range(w):
        pi=min(len(pl)-1,int(i/w*len(pl)))
        out+=cl("█" if i<fi else "░",pl[pi])
    return out

def spk(vs,cc="c"):
    if not vs: return ""
    mn,mx=min(vs),max(vs); rng=mx-mn or 1
    return cl("".join(SPK[min(7,int((v-mn)/rng*7.99))] for v in vs),cc)

def lch(vs,w=50,h=8,cc="c"):
    if not vs: return [" "*w]*h
    mn,mx=min(vs),max(vs); rng=mx-mn or 1
    gd=[[" "]*w for _ in range(h)]
    lx=ly=None
    for i,v in enumerate(vs):
        x=int(i/max(1,len(vs)-1)*(w-1))
        y=h-1-int((v-mn)/rng*(h-1))
        gd[y][x]="●"
        if lx is not None and x>lx:
            for s in range(1,x-lx):
                ix=lx+s; iy=round(ly+(y-ly)*s/(x-lx))
                if 0<=iy<h: gd[iy][ix]="·"
        lx,ly=x,y
    return [cl("".join(row),cc) for row in gd]

def pwv(b,r,c,wd,t,cc):
    PW="░▒▒▓▓█▓▓▒▒░"
    row=""
    for i in range(wd):
        v=(math.sin(i*0.18+t)+math.sin(i*0.07+t*1.3)+math.sin(i*0.31-t*0.8))/3
        row+=cl(PW[int((v+1)/2*10)],cc)
    put(b,r,c,row)

DN="ATCGATCGATCGATCGATCG"
def dna(b,r,c,h,t):
    for i in range(h):
        ph=t*3+i*0.55
        lf=int(2+2*math.sin(ph)); rt=int(2+2*math.cos(ph+1.6))
        ln=list("         ")
        for p in range(9):
            if p==lf:   ln[p]=cl(DN[(i+p)%len(DN)],"c","!")
            elif p==rt: ln[p]=cl(DN[(i+p+5)%len(DN)],"m","!")
            elif abs(p-4.5)<1.5 and i%4==2: ln[p]=cl("═" if p%2==0 else "─","d")
        put(b,r+i,c,"".join(ln))

MX="0123456789ABCDEF"
MC={}
def mxr(b,r,c,h,t,wd):
    for x in range(0,wd,2):
        if x not in MC or MC[x][0]>h+4:
            MC[x]=(random.randint(-h,0),random.choice([0.4,0.6,0.7,0.9,1.0]),random.choice(["g","G","c"]))
        pos,sp,cc=MC[x]; MC[x]=(pos+sp*0.5,sp,cc)
        cy=int(pos)
        for dy in range(6):
            ry=cy-dy
            if 0<=ry<h:
                ic="w" if dy==0 else cc if dy<3 else "d"
                put(b,r+ry,c+x,cl(random.choice(MX),ic))

def hpn(b,r,c,h,w,ttl="",cc="c"):
    top="╔═◈"+(f"[ {ttl} ]" if ttl else "")+"◈═"+"═"*max(0,w-7-len(ttl))+"╗"
    put(b,r,c,cl(top,cc,"!"))
    for i in range(h-2):
        sy=cl("◦","d") if i%3==0 else " "
        put(b,r+1+i,c,cl("║",cc)+sy+" "*(w-4)+sy+cl("║",cc))
    put(b,r+h-1,c,cl("╚"+"═"*(w-2)+"╝",cc))

FNT={
    "N":["█▄█","█▀█","█ █"],"E":["███","█▀▀","███"],"U":["█ █","█ █","▀█▀"],
    "R":["█▄ ","███","█ █"],"O":["▄█▄","█ █","▀█▀"],"W":["█ █","█▄█","▀ ▀"],
    "A":["▄▀▄","███","█ █"],"T":["███"," █ "," █ "],"C":["▄▀▀","█  ","▀▄▄"],
    "H":["█ █","███","█ █"],"S":["▄▀▀","▀▄ "," ▀█"],"Y":["█ █"," █ "," █ "],
    "M":["█▄█","█ █","█ █"],"P":["█▄ ","██ ","█  "],"L":["█  ","█  ","███"],
    "I":["███"," █ ","███"],"G":["▄▀▀","█▄█","▀▄▄"],"D":["█▄ ","█ █","█▄▀"],
    "B":["█▄ ","██ ","█▄▀"],"F":["███","█▀ ","█  "],"K":["█▄▀","██ ","█▄▀"],
    "V":["█ █","█ █"," ▀ "],"X":["█ █"," █ ","█ █"],"Z":["▀▀█"," █ ","█▀▀"],
    "0":["▄█▄","█ █","▀█▀"],"1":[" █ ","██ "," █ "],"2":["▀▀█"," █▀","███"],
    "3":["▀▀█","▀▀█","▀▀█"],"4":["█ █","███","  █"],"5":["███","█▀ "," ▀█"],
    "6":["▄▀ ","██ ","▀█▀"],"7":["▀▀█"," █ "," █ "],"8":["▄█▄","▄█▄","▀█▀"],
    "9":["▄█▄","▀▀█"," █▀"]," ":["   ","   ","   "],"/":["  █"," █ ","█  "],
    "-":["   ","▄▄▄","   "],"·":["   "," ▄ ","   "],
}
def big(txt,cc="c"):
    rw=["","",""]
    for ch in txt.upper():
        g=FNT.get(ch,FNT[" "])
        for i in range(3): rw[i]+=cl(g[i] if i<len(g) else "   ",cc)+" "
    return rw

# ── colour by threshold ───────────────────────────────────────────
def tcc(v,hi=80,md=60): return "r" if v>hi else "y" if v>md else "g"

# ── BOOT sequence ─────────────────────────────────────────────────
def boot():
    hid(); print("\033[2J\033[H",end="",flush=True)
    nm=platform.node(); os_=platform.system()+" "+platform.release()
    ln=[
        "N E U R O // W A T C H   Neural System HUD  v4.0",
        f"Host: {nm}   OS: {os_}   Arch: {platform.machine()}",
        f"psutil {psutil.__version__} · Python {platform.python_version()} · LIVE data","",
        "  ◈ CPU topology scanner ............... [ LIVE ]",
        "  ◈ Memory controller bus .............. [ LIVE ]",
        "  ◈ Disk I/O matrix .................... [ LIVE ]",
        "  ◈ Network packet interceptor ......... [ LIVE ]",
        "  ◈ Process table scanner .............. [ LIVE ]",
        "  ◈ Thermal sensor array ............... ["+" OK  " if _tv() is not None else " N/A  "+"]",
        "  ◈ Battery charge monitor ............. ["+" OK  " if hasattr(psutil,"battery") else " N/A  "+"]",
        "  ◈ DNA helix renderer ................. [ INIT ]",
        "  ◈ Plasma wave engine ................. [ INIT ]","",
        ">> NEURAL MATRIX ONLINE",">> NEURO//WATCH ACTIVATED",
    ]
    for i,l in enumerate(ln):
        print(f"\033[{3+i};3H",end="")
        if "[ LIVE ]" in l or "[ INIT ]" in l or "[ OK  ]" in l or "[ N/A  ]" in l:
            for tag,tc in [("LIVE","g"),("INIT","c"),(" OK  ","g"),(" N/A  ","y")]:
                if f"[ {tag}]" in l or f"[{tag}]" in l:
                    bs=l.split("[")[0]
                    print(cl(bs,"d")+cl("[","d")+cl(tag,tc,"!")+cl("]","d"),flush=True)
                    break
        elif l.startswith(">>"):
            for ch in l: print(cl(ch,"g","!"),end="",flush=True); time.sleep(0.006)
            print()
        elif i==0:
            for ch in l: print(cl(ch,"c","!"),end="",flush=True); time.sleep(0.007)
            print()
        elif l: print(cl(l,"d"))
        time.sleep(0.03)
    GC="!@#$%^&*<>|~"; ttx=ln[0]
    for _ in range(6):
        print("\033[3;3H",end="")
        gs="".join(cl(random.choice(GC),random.choice(["r","y","c","m"])) if random.random()<0.3 else ch for ch in ttx)
        print(cl(gs,"c","!"),end="",flush=True); time.sleep(0.05)
        print("\033[3;3H",end=""); print(cl(ttx,"c","!"),end="",flush=True); time.sleep(0.05)
    time.sleep(0.25)

MNU=[("C","CPU   Deep-Dive","r"),("M","Memory & Disk","y"),
     ("N","Network IO","c"),    ("T","Thermals & Procs","m"),("Q","Quit","d")]

# ── HOME HUD ──────────────────────────────────────────────────────
def hud(b):
    global _fm,_fp,_ft
    _fm+=1; _tk()
    nw=time.time(); _fp=1/(nw-_ft+1e-6); _ft=nw
    t=_fm*0.05
    b.write("\033[2J\033[H")
    hpn(b,1,1,H-1,W-1," NEURO//WATCH ","c")
    ts=datetime.datetime.now().strftime("%a %Y-%m-%d  %H:%M:%S")
    put(b,1,4,cl("◈","c")+cl(" NEURO//WATCH ","c","!")+cl("◈","c"))
    put(b,1,W-len(ts)-5,cl("◈","y")+cl(f" {ts} ","y")+cl("◈","y"))
    hd=big("NEURO//WATCH","c")
    put(b,3,4,hd[0]); put(b,4,4,hd[1]); put(b,5,4,hd[2])
    put(b,6,3,cl("◇"+"═"*(W-6)+"◇","c"))
    amp=max(0.4,_ch[-1]/30)
    for wi,cc2 in enumerate(["c","b","d"]):
        pwv(b,7+wi,2,W-4,t+wi*1.05*amp,cc2)
    put(b,10,2,cl("◇"+"─"*(W-6)+"◇","d"))

    # left panel - live gauges
    lc=3; lr=11; pw=28
    hpn(b,lr,lc,18,pw+10," LIVE GAUGES ","c")
    cv=_ch[-1]; mv2=_mh[-1]; dv2=_dh[-1]; tv=_th[-1]
    bat=_bv()
    cc2=tcc(cv); mc=tcc(mv2,85,65); dc=tcc(dv2,85,65); tc=tcc(tv,80,60)
    def row(rr,lb,v,cc3,u="%"):
        put(b,lr+rr,lc+2,cl(f"{lb:<4}","d")+gba(v,pw)+cl(f" {v:5.1f}{u}",cc3,"!"))
    row(2,"CPU ",cv,cc2); row(4,"MEM ",mv2,mc)
    row(6,"DSK ",dv2,dc)
    if tv>0: row(8,"TMP ",min(tv,99),tc,u="°")
    else: put(b,lr+8,lc+2,cl("TMP ","d")+cl("no sensor","d","~"))
    if bat:
        bp,pg=bat; bc=tcc(100-bp,80,50)
        fi=int(bp/100*pw)
        put(b,lr+10,lc+2,cl("BAT ","d")+cl("█"*fi,bc)+cl("░"*(pw-fi),"d")+cl(f" {bp:4.0f}%{'⚡' if pg else '🔋'}",bc,"!"))
    else:
        put(b,lr+10,lc+2,cl("BAT ","d")+cl("no battery","d","~"))
    st=cl("●NOMINAL","g","!") if cv<70 and mv2<80 else cl("●WARNING","y","!") if cv<90 else cl("●CRITICAL","r","!")
    put(b,lr+12,lc+2,cl("SYS ","d")+st+cl(f"  PRC:{_pc():>4}","d"))
    put(b,lr+13,lc+2,cl(f"UP  ","d")+cl(_up(),"c")+cl(f"  FQ:{_fi():.0f}MHz","d"))
    put(b,lr+14,lc+2,cl(f"FPS:{_fp:4.0f}  FRM:{_fm:06d}","d","~"))
    for ii,(hs,cc3) in enumerate([(_ch,cc2),(_mh,mc),(_dh,dc)]):
        put(b,lr+16,lc+2+ii*12,spk(hs[-(pw//3):],cc3))

    # centre - DNA
    dc2=lc+pw+12; dr=11
    hpn(b,dr,dc2,18,12," DNA ","m")
    dna(b,dr+1,dc2+1,16,t)

    # right panel - net+disk live rates
    rc=dc2+14; rw=W-rc-4
    hpn(b,11,rc,18,rw," LIVE I/O ","b")
    tx,rx=_nh[-1]; dr2,dw2=_io[-1]
    put(b,13,rc+2,cl("NET ↑ ","d")+cl(f"{tx:8.2f} KB/s","c","!")+cl("  ","d")+gba(min(tx/100,100),rw-22))
    put(b,15,rc+2,cl("NET ↓ ","d")+cl(f"{rx:8.2f} KB/s","g","!")+cl("  ","d")+gba(min(rx/100,100),rw-22))
    put(b,17,rc+2,cl("DSK R ","d")+cl(f"{dr2:8.2f} KB/s","y","!")+cl("  ","d")+gba(min(dr2/500,100),rw-22))
    put(b,19,rc+2,cl("DSK W ","d")+cl(f"{dw2:8.2f} KB/s","m","!")+cl("  ","d")+gba(min(dw2/500,100),rw-22))
    ni=psutil.net_io_counters()
    put(b,21,rc+2,cl(f"total ↑{ni.bytes_sent/1024**2:.1f}MB ↓{ni.bytes_recv/1024**2:.1f}MB","d"))
    try: nc2=len(psutil.net_connections(kind="inet"))
    except: nc2=0
    put(b,22,rc+2,cl(f"conn:{nc2:>3}  pkt↓{ni.dropin} err↑{ni.errout}","d"))
    vm=psutil.virtual_memory()
    put(b,24,rc+2,cl(f"RAM {vm.used/1024**3:.2f}/{vm.total/1024**3:.1f}GB","w","!"))
    ca=getattr(vm,"cached",0); bf=getattr(vm,"buffers",0)
    put(b,25,rc+2,cl(f"buf:{bf/1024**2:.0f}MB cach:{ca/1024**2:.0f}MB","d") if (bf or ca) else cl(f"avail:{vm.available/1024**3:.2f}GB free","d"))

    # sparkline strip
    sr=lr+18; sw=W-6
    hpn(b,sr,3,5,sw," SPARKLINES ","d")
    sw4=(sw-12)//4
    for ii,(lb,hs,cc3) in enumerate([("CPU",_ch,cc2),("MEM",_mh,mc),("DSK",_dh,dc),("NET",[ x[1] for x in _nh],tcc(rx,100,30))]):
        put(b,sr+1,5+ii*(sw4+3),cl(f"{lb}","d","!"))
        put(b,sr+2,5+ii*(sw4+3),spk(hs[-sw4:],cc3))
        put(b,sr+3,5+ii*(sw4+3),cl(f"{hs[-1]:4.0f}",cc3))

    put(b,H-4,2,cl("◈"+"═"*(W-5)+"◈","c"))
    nav=""
    for i,(k,lb,cc3) in enumerate(MNU):
        sl=i==_sl; pre=C["^"] if sl else ""
        nav+=pre+cl(" ▶ " if sl else "   ","y")+cl(f"[{k}]",cc3,"!")+cl(f" {lb:<22}",cc3 if not sl else "w")+C["0"]+"  "
    put(b,H-3,3,nav)
    put(b,H-2,3,cl("↑↓ select · ENTER or key = dive · host: ","d")+cl(platform.node(),"c","!"))

# ── detail scaffold ───────────────────────────────────────────────
def dvw(ttl,drw,fps=10):
    hid()
    try:
        while True:
            _tk()
            b=io.StringIO(); b.write("\033[2J\033[H")
            hpn(b,1,1,H-1,W-1,f" {ttl[0]} ",ttl[1])
            drw(b)
            put(b,H-2,4,cl(f"live {fps}fps · FRM:{_fm}  [any key → back]","d","~"))
            sys.stdout.write(b.getvalue()); sys.stdout.flush()
            t0=time.time()
            while time.time()-t0<1/fps:
                if gky(): return
                time.sleep(0.01)
    finally: shw()

# ── CPU view ─────────────────────────────────────────────────────
def v_cp():
    def drw(b):
        global _fm; _fm+=1; t=_fm*0.06
        cv=_ch[-1]; cc2=tcc(cv)
        pwv(b,3,3,W-6,t,"c"); pwv(b,4,3,W-6,t+2.1,"b")
        hd=big("CPU","r"); put(b,5,4,hd[0]); put(b,6,4,hd[1]); put(b,7,4,hd[2])
        put(b,9,4,cl("Load  : ","d")+cl(f"{cv:5.1f}%",cc2,"!")+"  "+gba(cv,50))
        put(b,10,4,cl("Peak  : ","d")+cl(f"{max(_ch):5.1f}%","r"))
        put(b,11,4,cl(f"Avg   : ","d")+cl(f"{sum(_ch)/len(_ch):5.1f}%","y"))
        nc=psutil.cpu_count(); nf=_fi()
        put(b,12,4,cl(f"Cores : {nc} logical  {psutil.cpu_count(logical=False)} physical  Freq:{nf:.0f}MHz","d"))
        put(b,13,4,cl(f"Uptime: {_up()}  PIDs:{_pc()}","d"))
        put(b,15,4,cl("━━━ 120s CPU HISTORY ","c","!"))
        ln=lch(_ch,W-14,12,"r")
        for i,l in enumerate(ln): put(b,16+i,4,cl(f"{100-i*8:>3}│","d")+l)
        put(b,29,4,cl("   └"+"─"*(W-14),"d"))
        dna(b,9,W-16,18,t)
        try:
            pcs=psutil.cpu_percent(percpu=True,interval=None)
            put(b,31,4,cl("PER-CORE ","d","!"))
            for ci,cv2 in enumerate(pcs[:min(len(pcs),W//7)]):
                c2=tcc(cv2)
                put(b,32,4+ci*6,cl(f"C{ci:<2}","d")+cl(f"{cv2:3.0f}%",c2))
        except: pass
    dvw(("CPU DEEP-DIVE","r"),drw,fps=8)

# ── Memory view ───────────────────────────────────────────────────
def v_mm():
    def drw(b):
        t=_fm*0.05; mv2=_mh[-1]; dv2=_dh[-1]
        mc=tcc(mv2,85,65); dc=tcc(dv2,85,65)
        pwv(b,3,3,W-6,t,"y"); pwv(b,4,3,W-6,t+1.6,"d")
        hd=big("MEM","y"); put(b,5,4,hd[0]); put(b,6,4,hd[1]); put(b,7,4,hd[2])
        tt,us,av,ca,bf=_vm(); sp,su,st=_sw()
        put(b,9,4,cl("RAM Used : ","d")+cl(f"{mv2:5.1f}%",mc,"!")+"  "+gba(mv2,50))
        put(b,10,4,cl(f"  {us/1024**3:.2f}GB used / {tt/1024**3:.1f}GB total  avail:{av/1024**3:.2f}GB","d"))
        put(b,11,4,cl(f"  cached:{ca/1024**2:.0f}MB  buffers:{bf/1024**2:.0f}MB","d") if (ca or bf) else cl(f"  avail:{av/1024**3:.2f}GB  wired:{getattr(psutil.virtual_memory(),'wired',0)/1024**2:.0f}MB","d"))
        put(b,12,4,cl("Swap     : ","d")+cl(f"{sp:5.1f}%  {su/1024**2:.0f}/{st/1024**2:.0f}MB",tcc(sp),"!"))
        put(b,13,4,cl("Disk Used: ","d")+cl(f"{dv2:5.1f}%",dc,"!")+"  "+gba(dv2,50))
        try:
            di=psutil.disk_io_counters()
            put(b,14,4,cl(f"  R:{di.read_bytes/1024**3:.2f}GB total  W:{di.write_bytes/1024**3:.2f}GB total","d"))
        except: pass
        dr2,dw2=_io[-1]
        put(b,15,4,cl(f"  live R:{dr2:.1f} KB/s  W:{dw2:.1f} KB/s","c"))
        put(b,17,4,cl("━━━ RAM HISTORY ","y","!"))
        ln=lch(_mh,W-14,9,"y")
        for i,l in enumerate(ln): put(b,18+i,4,cl(f"{100-i*11:>3}│","d")+l)
        put(b,28,4,cl("━━━ DISK HISTORY ","c","!"))
        ln=lch(_dh,W-14,5,"c")
        for i,l in enumerate(ln): put(b,29+i,4,cl(f"{100-i*20:>3}│","d")+l)
        dna(b,9,W-16,20,t)
    dvw(("MEMORY & DISK","y"),drw,fps=6)

# ── Network view ──────────────────────────────────────────────────
def v_nt():
    def drw(b):
        t=_fm*0.05
        tx,rx=_nh[-1]; dr2,dw2=_io[-1]
        pwv(b,3,3,W-6,t,"c"); pwv(b,4,3,W-6,t+1.1,"b")
        hd=big("NET","c"); put(b,5,4,hd[0]); put(b,6,4,hd[1]); put(b,7,4,hd[2])
        put(b,9,4,cl("Upload ↑ : ","d")+cl(f"{tx:10.2f} KB/s","c","!")+"  "+gba(min(tx/100,100),40))
        put(b,10,4,cl("Download↓: ","d")+cl(f"{rx:10.2f} KB/s","g","!")+"  "+gba(min(rx/100,100),40))
        put(b,11,4,cl("Disk R   : ","d")+cl(f"{dr2:10.2f} KB/s","y","!")+"  "+gba(min(dr2/500,100),40))
        put(b,12,4,cl("Disk W   : ","d")+cl(f"{dw2:10.2f} KB/s","m","!")+"  "+gba(min(dw2/500,100),40))
        try:
            ni=psutil.net_io_counters()
            put(b,14,4,cl(f"Total ↑{ni.bytes_sent/1024**2:.1f}MB  ↓{ni.bytes_recv/1024**2:.1f}MB","d"))
            put(b,15,4,cl(f"Pkts  ↑{ni.packets_sent:,}  ↓{ni.packets_recv:,}  drop:{ni.dropin}  err:{ni.errin+ni.errout}","d"))
            ifc=psutil.net_if_addrs()
            put(b,16,4,cl("IFaces: ","d")+cl("  ".join(ifc.keys()),"c"))
        except: pass
        try:
            nc=psutil.net_connections(kind="inet"); sts={}
            for cx in nc: sts[cx.status]=sts.get(cx.status,0)+1
            put(b,17,4,cl("Conns: ","d")+cl("  ".join(f"{k}:{v}" for k,v in sts.items()),"y"))
        except: pass
        put(b,19,4,cl("━━━ UPLOAD KB/s ","c","!"))
        ln=lch([x[0] for x in _nh],W-14,7,"c")
        for i,l in enumerate(ln): put(b,20+i,4,cl("   │","d")+l)
        put(b,28,4,cl("━━━ DOWNLOAD KB/s ","g","!"))
        ln=lch([x[1] for x in _nh],W-14,7,"g")
        for i,l in enumerate(ln): put(b,29+i,4,cl("   │","d")+l)
        mxr(b,9,W-22,28,t,20)
    dvw(("NETWORK IO","c"),drw,fps=5)

# ── Thermals + Process view ───────────────────────────────────────
def v_tp():
    def drw(b):
        t=_fm*0.05; tv=_th[-1]; bat=_bv()
        tc=tcc(tv,80,60)
        pwv(b,3,3,W-6,t,"m"); pwv(b,4,3,W-6,t+0.9,"r")
        hd=big("PROCS","m"); put(b,5,4,hd[0]); put(b,6,4,hd[1]); put(b,7,4,hd[2])
        # temps
        if tv>0:
            put(b,9,4,cl(f"CPU Temp: {tv:.1f}°C ","m","!")+gba(min(tv,100),30))
            put(b,10,4,cl(f"Peak: {max(_th):.1f}°C  Avg: {sum(_th)/len(_th):.1f}°C","d"))
        else:
            put(b,9,4,cl("Temperature sensor: not available on this system","d","~"))
        # battery
        if bat:
            bp,pg=bat; bc=tcc(100-bp,80,50); fi=int(bp/100*30)
            put(b,11,4,cl("Battery: ","d")+cl("█"*fi,bc)+cl("░"*(30-fi),"d")+cl(f" {bp:.0f}%  {'Charging ⚡' if pg else 'On battery 🔋'}",bc,"!"))
        else:
            put(b,11,4,cl("Battery: not present (desktop/server)","d","~"))
        put(b,12,4,cl(f"Uptime: {_up()}   PIDs: {_pc()}   CPU cores: {psutil.cpu_count()}","d"))
        # live process table
        put(b,14,4,cl("━━━ TOP PROCESSES (live) ","m","!"))
        put(b,15,4,cl(f"{'PID':>6}  {'NAME':<22}{'CPU%':>6}  {'MEM%':>5}  STATUS","d","!"))
        put(b,16,4,cl("─"*(W-10),"d"))
        ps=_tp()
        for i,pr in enumerate(ps[:min(8,H-24)]):
            cp,mp,nm,pid,st=pr
            cc2=tcc(cp); mc=tcc(mp,80,50)
            put(b,17+i,4,cl(f"{pid:>6}","d")+cl(f"  {nm[:22]:<22}","w")+cl(f"{cp:>6.1f}%",cc2,"!")+cl(f"  {mp:>4.1f}%",mc)+cl(f"  {st}","d"))
        put(b,26,4,cl("━━━ TEMP HISTORY ","m","!"))
        if any(v>0 for v in _th):
            ln=lch(_th,W-14,6,tc)
            for i,l in enumerate(ln): put(b,27+i,4,cl(f"{120-i*10:>3}│","d")+l)
        else:
            put(b,27,4,cl("no thermal data","d","~"))
        dna(b,9,W-16,18,t)
    dvw(("THERMALS & PROCESSES","m"),drw,fps=4)

# ── input ─────────────────────────────────────────────────────────
def gky():
    if _WN:
        if not msvcrt.kbhit(): return ""
        ch=msvcrt.getwch()
        if ch in("\x00","\xe0"):
            return {"H":"UP","P":"DOWN","K":"LEFT","M":"RIGHT"}.get(msvcrt.getwch(),"")
        return ch
    fd=sys.stdin.fileno(); old=termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        rd,_,_=select.select([sys.stdin],[],[],0.0)
        if not rd: return ""
        ch=sys.stdin.read(1)
        if ch=="\033":
            r2,_,_=select.select([sys.stdin],[],[],0.03)
            if r2:
                c2=sys.stdin.read(1)
                if c2=="[": return {"A":"UP","B":"DOWN","C":"RIGHT","D":"LEFT"}.get(sys.stdin.read(1),"")
        return ch
    finally: termios.tcsetattr(fd,termios.TCSADRAIN,old)

# ── main ──────────────────────────────────────────────────────────
def main():
    global _sl
    hid(); boot()
    act={"C":v_cp,"M":v_mm,"N":v_nt,"T":v_tp}
    try:
        while True:
            b=io.StringIO(); hud(b)
            sys.stdout.write(b.getvalue()); sys.stdout.flush()
            k=gky()
            if not k: time.sleep(0.033); continue
            ku=k.upper()
            if ku in("Q","\x03","\x1b"): break
            elif k=="UP":   _sl=(_sl-1)%len(MNU)
            elif k=="DOWN": _sl=(_sl+1)%len(MNU)
            elif k in("\r","\n"):
                mk=MNU[_sl][0]
                if mk=="Q": break
                fn=act.get(mk)
                if fn: fn()
            elif ku in act: act[ku]()
    finally:
        shw(); print("\033[2J\033[H",end="")
        hd=big("GOODBYE","c")
        print(f"\033[{H//2-1};4H{hd[0]}\033[{H//2};4H{hd[1]}\033[{H//2+1};4H{hd[2]}")
        print(f"\033[{H//2+3};4H{cl('NEURO//WATCH  ·  SESSION TERMINATED','d','~')}")
        print(f"\033[{H//2+4};1H",flush=True)

if __name__=="__main__":
    try: main()
    except KeyboardInterrupt: shw(); print("\033[2J\033[H",end="")