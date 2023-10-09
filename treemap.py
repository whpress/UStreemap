import matplotlib.pyplot as plt
import math
import os

def printme(plt, **kwargs) :
    if 'filename' in kwargs :
        location = kwargs['filename']
    else :
        location = 'MyJupyterFig.pdf'
    print('saving to',os.path.abspath(location))
    plt.savefig(location)

def grabdata(filename):
    vals = []
    with open(filename) as f:
        for line in f:
            vals.append(float(line))
        return vals

def colormap(v):
    return 1 - math.sqrt(1 - v)
    #return v

def colors(vv, rr, gg, bb):
    for i in range(51):
        vv[i] += 1e-6
        rr[i] = min(255, max(0, int(255 * colormap(min(1, 1 + vv[i])))))
        gg[i] = min(255, max(0, int(255 * colormap(1 - abs(vv[i]))))) 
        bb[i] = min(255, max(0, int(255 * colormap(min(1, 1 - vv[i])))))
        
def signedsqrt(x) :
    return (math.sqrt(x) if x >= 0 else -math.sqrt(-x))
        
def colorspurple(vvv, rr, gg, bb):
    unsat = 0.3
    vv = vvv.copy()
    for i in range(51):
        v = signedsqrt(vv[i]) # replace by "probable outcome"?
        v += 1e-6
        b = min(1., max(0., (max(1 - (v + 1) / 2, 0))))
        g = 0.
        r = min(1., max(0., (max((v + 1) / 2, 0))))
        rr[i] = 255*(r + (1 - r) * unsat)
        gg[i] = 255*(g + (1 - g) * unsat)
        bb[i] = 255*(b + (1 - b) * unsat)
        

class PSpage:
    def __init__(self, ax):
        self.ax = ax
        self.font_stack = []
        self.cur_font = None
        self.cur_font_size = 12
        self.cur_r = 0
        self.cur_g = 0        
        self.cur_b = 0
        
    def setcolor(self, r, g, b):
        self.cur_r = r
        self.cur_g = g
        self.cur_b = b
        
    def plot(self, x, y):
        xx = x.copy()
        xx.append(x[0])
        yy = y.copy()
        yy.append(y[0])
        #print(xx)
        #print(yy)
        self.ax.plot(xx, yy, color=(self.cur_r/255, self.cur_g/255, self.cur_b/255))
        
    def drawandfill(self, x, y) :
        self.ax.fill(x, y, facecolor=(self.cur_r/255, self.cur_g/255, self.cur_b/255),
                    edgecolor='black', linewidth=1.0)
        
    def pushfont(self, fontname, fontsize):
        self.font_stack.append((self.cur_font, self.cur_font_size))
        self.cur_font = fontname
        self.cur_font_size = fontsize
        
    def popfont(self):
        self.cur_font, self.cur_font_size = self.font_stack.pop()
        
    def text(self, x, y, text):
        self.ax.text(x, y, text, fontname=self.cur_font, fontsize=self.cur_font_size,
                     horizontalalignment='center', verticalalignment='center')
    def title(self,text,x,y):
        #self.ax.set_title(text)
        self.ax.text(x,y,text,fontfamily='serif',fontsize=10.)

class Region:
    def __init__(self):
        self.xl = 0.0 
        self.xr = 0.0
        self.yb = 0.0
        self.yt = 0.0
        self.val = 0.0
        self.r = 255
        self.g = 255 
        self.b = 255
        self.mom = None
        self.firstdau = None
        self.sis = None
        self.stateid = 0
        self.id = ""
        self.statelist = []
        
    def reportval(self):
        return self.val

    def grabval(self, vals):
        for i in range(len(vals)):
            vals[i] += 1e-6
        self.val = 0.0
        dau = self.firstdau
        while dau:
            dau.grabval(vals)
            self.val += dau.reportval()
            dau = dau.sis
        if self.stateid:
            self.val = vals[self.stateid-1]

    def grabcolors(self, rr, gg, bb):
        dau = self.firstdau
        while dau:
            dau.grabcolors(rr, gg, bb)
            dau = dau.sis
        if self.stateid:
            self.r = rr[self.stateid-1]
            self.g = gg[self.stateid-1]
            self.b = bb[self.stateid-1]
        else:
            self.r = 255
            self.g = 255
            self.b = 255
            
    def label(self, pg):
        fontsiz = min(15.0, 0.5*min(self.xr-self.xl, self.yt-self.yb))
        if fontsiz > 2.0:
            pg.pushfont("Arial", fontsiz) 
            pg.text(0.5*(self.xl+self.xr), 0.5*(self.yb+self.yt) - 0.3*fontsiz, self.id)
            pg.popfont()

    def drawme(self, pg):
        if not self.firstdau:
            x = [self.xl, self.xr, self.xr, self.xl] 
            y = [self.yb, self.yb, self.yt, self.yt]
            pg.setcolor(self.r, self.g, self.b)
            pg.drawandfill(x,y)
            self.label(pg)
        else:
            dau = self.firstdau
            while dau:
                dau.drawme(pg)
                dau = dau.sis
                
    def placeme(self):
        print("placeme called for region %s of unknown geometry" % self.id)
        
    def add(self, newid, newreg, sid):
        if not self.firstdau:
            self.firstdau = newreg
        else:
            dau = self.firstdau
            while dau.sis:
                dau = dau.sis
            dau.sis = newreg
        newreg.mom = self 
        newreg.stateid = sid
        newreg.id = newid
        return newreg
    
    def rollcall(self):
        #print(self.mom.id + " --> ", end="") if self.mom else ""
        #print("%s = %g (%d) [%g %g %g %g]" % 
        #      (self.id, self.val, self.stateid, self.xl, self.xr, self.yb, self.yt))
        statelist = []
        if self.stateid > 0 :
            #print(f"{self.id} {self.stateid}")
            statelist.append((self.stateid,self.id))
        dau = self.firstdau
        while dau:
            dau.rollcall()
            dau = dau.sis
        self.statelist = sorted(self.statelist)
        
class Vreg(Region):
    def placeme(self):
        last = self.yb 
        dau = self.firstdau
        while dau:
            dau.xl = self.xl
            dau.xr = self.xr
            dau.yb = last
            dau.yt = dau.yb + (self.yt - self.yb) * dau.reportval() / self.val
            dau.placeme() 
            last = dau.yt
            dau = dau.sis

class Hreg(Region):
    def placeme(self):
        last = self.xl
        dau = self.firstdau
        while dau:
            dau.yb = self.yb
            dau.yt = self.yt
            dau.xl = last
            dau.xr = dau.xl + (self.xr - self.xl) * dau.reportval() / self.val
            dau.placeme()
            last = dau.xr
            dau = dau.sis
            
class NWcornerreg(Region):
    def placeme(self):
        dau = self.firstdau
        dau.xl = self.xl
        dau.xr = self.xr
        dau.yb = self.yb 
        dau.yt = self.yt
        dau = dau.sis
        dau.xr = self.xr
        dau.yt = self.yt
        dau.xl = self.xr - math.sqrt(dau.val / self.val) * (self.xr - self.xl)
        dau.yb = self.yt - math.sqrt(dau.val / self.val) * (self.yt - self.yb)
        
class State(Vreg):
    def add(self, newid, newreg, sid):
        print("illegal attempt to add to State")
        return None

class CalNevRegion(Region):  
    def reportval(self):
        return (6./5.)*self.val
    
    def placeme(self):
        dau = self.firstdau
        dau.xl = self.xl
        dau.xr = self.xr
        dau.yb = self.yb
        dau.yt = self.yt
        dau = dau.sis
        dau.xr = self.xr
        dau.yt = self.yt
        
        dau.xl = self.xr - math.sqrt(1.5*dau.val / (1.2*self.val)) * (self.xr - self.xl)
        dau.yb = self.yt - math.sqrt(1.5*dau.val / (1.2*self.val)) * (self.yt - self.yb)
        
class California(State):
    def drawme(self, pg):
        x = [self.xr, self.xr, self.xl, self.xl, 0.5*(self.xl+self.xr)]
        y = [self.yb, self.yt, self.yt, self.yb, self.yb]
        pg.setcolor(self.r, self.g, self.b)
        pg.drawandfill(x,y)
        self.label(pg)
        
class Nevada(State):
    def drawme(self, pg):
        x = [self.xr, self.xr, self.xl, self.xl]
        y = [self.yb, self.yt, self.yt, 0.66*self.yt+0.34*self.yb]
        pg.setcolor(self.r, self.g, self.b)
        pg.drawandfill(x,y)
        self.yb = self.yt - 0.4*(self.yt-self.yb) 
        self.label(pg)
        
class Hawaii(State):
    def reportval(self):
        return 0.
    
    def drawme(self, pg):
        eps = 0.05 * (self.mom.yt - self.mom.yb)
        length = math.sqrt(self.val*(self.mom.xr - self.mom.xl)*(self.mom.yt - self.mom.yb) / self.mom.val)
        self.xl = self.mom.xl
        self.xr = self.mom.xl + length
        self.yb = self.mom.yb - length - eps
        self.yt = self.mom.yb - eps
        Region.drawme(self, pg)
        
class Alaska(State):
    def reportval(self):
        return 0.
    
    def drawme(self, pg):
        eps = 0.05 * (self.mom.yt - self.mom.yb) 
        length = math.sqrt(self.val*(self.mom.xr - self.mom.xl)*(self.mom.yt - self.mom.yb) / self.mom.val)
        self.xl = self.mom.xl
        self.xr = self.mom.xl + length
        self.yb = self.mom.yt + eps
        self.yt = self.mom.yt + length + eps
        Region.drawme(self, pg)
        
class Texas(State):
    def reportval(self):
        return (2./3.)*self.val
    
    def drawme(self, pg):
        x = [self.xr, self.xr, self.xl, self.xl, 0.5*(self.xl+self.xr)]
        y = [self.yb, self.yt, self.yt, self.yb, self.yb-(self.yt-self.yb)]
        pg.setcolor(self.r, self.g, self.b)
        pg.drawandfill(x,y)
        self.label(pg)
        
class Florida(State):
    def reportval(self):
        return 0.
    
    def drawme(self, pg):
        length = math.sqrt(self.val*(self.mom.xr - self.mom.xl)*(self.mom.yt - self.mom.yb) / self.mom.val)
        self.xl = self.mom.xr - length/1.8
        self.xr = self.mom.xr
        self.yb = self.mom.yb - 1.8*length
        self.yt = self.mom.yb
        
        x = [self.xr, self.xr, 1.4*self.xl-0.4*self.xr, self.xl, self.xl, 0.8*self.xl+0.2*self.xr, 0.2*self.xl+0.8*self.xr]
        y = [0.9*self.yb+0.1*self.yt, self.yt, self.yt, 0.9*self.yt+0.1*self.yb, 0.9*self.yb+0.1*self.yt, self.yb, self.yb]
        
        pg.setcolor(self.r, self.g, self.b)
        pg.drawandfill(x,y)
        self.label(pg)
        
class Virginia(State):
    def label(self, pg):
        cent = self.sis.xl - self.sis.sis.xr
        bottom = min(self.sis.yb,self.sis.sis.yb) - self.yb
        left = min(self.sis.sis.yb - self.yb, self.xl - self.sis.xl)
        if cent > bottom and cent > left:
            self.xl = self.sis.sis.xr
            self.xr = self.sis.xl
        elif bottom > left:
            self.yt = min(self.sis.yb,self.sis.sis.yb)
        else:
            self.xr = self.sis.xl
            self.yt = self.sis.sis.yb
        Region.label(self, pg)
            
class VAbox(NWcornerreg):
    def placeme(self):
        dau = self.firstdau
        sav = 0.0
        dau.xl = self.xl
        dau.xr = self.xr
        dau.yb = self.yb
        dau.yt = self.yt
        dau = dau.sis
        dau.xr = self.xr
        dau.yt = self.yt
        dau.xl = sav = self.xr - math.sqrt(dau.val / self.val) * (self.xr - self.xl)
        dau.yb = self.yt - math.sqrt(dau.val / self.val) * (self.yt - self.yb)
        dau = dau.sis
        dau.xl = self.xl
        dau.yt = self.yt
        dau.xr = min(sav, self.xl + math.sqrt(dau.val / self.val) * (self.xr - self.xl))
        dau.yb = self.yt - math.sqrt(dau.val / self.val) * (self.yt - self.yb)
        
class NewEngland(Vreg):
    def reportval(self):
        return 0.
    
    def placeme(self):
        length = math.sqrt(self.val*(self.mom.xr - self.mom.xl)*(self.mom.yt - self.mom.yb) / self.mom.val)
        self.xr = self.xr + length
        if length < self.yt-self.yb:
            self.yb = self.yt - length
        else:
            self.yt = self.yb + length
        Vreg.placeme(self)
        self.xr = self.mom.xr
        self.yb = self.mom.yb
        self.yt = self.mom.yt
        
class Maryland(State):
    def label(self, pg):
        self.xr = self.sis.xl
        Region.label(self, pg)
        
class Connecticut(State):
    def label(self, pg):
        self.xr = self.sis.xl
        Region.label(self, pg)

def USmap(pg, xxl, xxr, yyb, yyt, r, g, b, vals, caption):
    
    us = Hreg()
    us.id = "US"
    us.xl = xxl
    us.yb = yyb 
    us.xr = xxr
    us.yt = yyt
    
    pacwest = us.add("PacWest", Vreg(), 0)  
    hawaii = pacwest.add("HI", Hawaii(), 12)
    CANV = pacwest.add("CaNv", CalNevRegion(), 0)
    california = CANV.add("CA", California(), 5)
    nevada = CANV.add("NV", Nevada(), 29)
    oregon = pacwest.add("OR", State(), 38)
    washington = pacwest.add("WA", State(), 48)
    alaska = pacwest.add("AK", Alaska(), 2)

    mtwest = us.add("MountainWest", Vreg(), 0)
    AZNM = mtwest.add("AzNm", Hreg(), 0)
    arizona = AZNM.add("AZ", State(), 3)
    newmexico = AZNM.add("NM", State(), 32)
    UTCO = mtwest.add("UtCo", Hreg(), 0)  
    utah = UTCO.add("UT", State(), 45)
    colorado = UTCO.add("CO", State(), 6)
    COWS = mtwest.add("Cows", Hreg(), 0)
    idaho = COWS.add("ID", State(), 13)
    WYMT = COWS.add("WyMt", Vreg(), 0)
    wyoming = WYMT.add("WY", State(), 51)
    montana = WYMT.add("MT", State(), 27)

    midtier = us.add("MidTier", Vreg(), 0)
    greatertexas = midtier.add("GreaterTexas", Hreg(), 0)
    texas = greatertexas.add("TX", Texas(), 44)
    louisiana = greatertexas.add("LA", State(), 19)
    OKAR = midtier.add("OKAR", Hreg(), 0)
    oklahoma = OKAR.add("OK", State(), 37) 
    arkansas = OKAR.add("AR", State(), 4)

    uppertier = midtier.add("UpperTier", Hreg(), 0)
    midwest = uppertier.add("MidWest", Vreg(), 0)
    kansas = midwest.add("KS", State(), 17)
    nebraska = midwest.add("NB", State(), 28)
    sdakota = midwest.add("SD", State(), 42)
    ndakota = midwest.add("ND", State(), 35)

    mideast = uppertier.add("MidEast", Vreg(), 0)
    missouri = mideast.add("MO", State(), 26)
    iowa = mideast.add("IA", State(), 16)
    minn = mideast.add("MN", State(), 24)

    east = us.add("East", Vreg(), 0)
    deepsouth = east.add("DeepSouth", Hreg(), 0)
    missis = deepsouth.add("MS", State(), 25)
    alabama = deepsouth.add("AL", State(), 1)
    GAFL = deepsouth.add("GAFL", Vreg(), 0)
    florida = GAFL.add("FL", Florida(), 10)
    georgia = GAFL.add("GA", State(), 11)
    south = east.add("South", Hreg(), 0)
    TNKY = south.add("TNKY", Vreg(), 0)
    tennessee = TNKY.add("TN", State(), 43)
    kentucky = TNKY.add("KY", State(), 18)
    southeast = south.add("Southeast", Vreg(), 0)
    scarolina = southeast.add("SC", State(), 41)
    ncarolina = southeast.add("NC", State(), 34)
    VABOX = southeast.add("VAbox", VAbox(), 0)
    virginia = VABOX.add("VA", Virginia(), 47)
    district = VABOX.add("DC", State(), 9)
    wvirginia = VABOX.add("WV", State(), 49)
    north = east.add("North", Hreg(), 0)
    lakes = north.add("Lakes", Vreg(), 0)
    rust = lakes.add("Rust", Hreg(), 0)
    illinois = rust.add("IL", State(), 14)
    indiana = rust.add("IN", State(), 15)
    ohio = rust.add("OH", State(), 36)
    dairy = lakes.add("Dairy", Hreg(), 0)
    wisconsin = dairy.add("WI", State(), 50)
    michigan = dairy.add("MI", State(), 23)
    northeast = north.add("Northeast", Vreg(), 0)
    midatl = northeast.add("MidAtl", Hreg(), 0)
    penna = midatl.add("PA", State(), 39)
    MDDENJ = midatl.add("MDDENJ", Vreg(), 0)
    MDDE = MDDENJ.add("MDDE", NWcornerreg(), 0)
    maryland = MDDE.add("MD", Maryland(), 21)
    delaware = MDDE.add("DE", State(), 8)
    newjersey = MDDENJ.add("NJ", State(), 31) 
    NYNE = northeast.add("NYNE", Hreg(), 0)
    newyork = NYNE.add("NY", State(), 33)
    newengland = NYNE.add("NewEngland", NewEngland(), 0)
    CTRI = newengland.add("CTRI", NWcornerreg(), 0)
    conn = CTRI.add("CT", Connecticut(), 7)
    rhode = CTRI.add("RI", State(), 40)
    mass = newengland.add("MA", State(), 22)
    downeast = newengland.add("DownEast", Hreg(), 0)
    vermont = downeast.add("VT", State(), 46)
    newhamp = downeast.add("NH", State(), 30)
    maine = downeast.add("ME", State(), 20)

    us.grabval(vals)
    us.grabcolors(r, g, b)  
    us.placeme()
    us.drawme(pg)
    
    pg.pushfont("Arial",12) 
    pg.title(caption,alaska.xr+10.,alaska.yb+2.)
    pg.popfont()
    #us.rollcall()

def inextensive(filex, filin, caption, rr, gg, bb, mod=0):    
    r = [0] * 51
    g = [0] * 51 
    b = [0] * 51
    exten = []
    inten = []
    if filex:
        exten = grabdata(filex)
    else:
        exten = [1.0] * 51
    if filin:
        inten = grabdata(filin)
    else:
        inten = exten.copy()
    frac = [0.0] * 51
    if mod == 2:
        for i in range(51):
            frac[i] = inten[i] / (exten[i] + 1e-10)
    else:
        for i in range(51):
            frac[i] = exten[i] / (inten[i] + 1e-10)   
    maxfrac = max(frac)
    for i in range(51):
        if mod == 1:
            frac[i] = min(1.0, 2.2*frac[i]/maxfrac) 
        else:
            frac[i] = frac[i] / maxfrac
        r[i] = int(frac[i]*rr + (1-frac[i])*255)
        g[i] = int(frac[i]*gg + (1-frac[i])*255)
        b[i] = int(frac[i]*bb + (1-frac[i])*255)

    fig, ax = plt.subplots(figsize=(8, 8))
    plt.xticks([])
    plt.yticks([])
    ax.axis('off')
    pg = PSpage(ax)
    USmap(pg, 50.0, 450.0, 250.0, 450.0, r, g, b, exten, caption)
    
def redblue(repubs, dems, pops, caption):    
    r = [0] * 51
    g = [0] * 51 
    b = [0] * 51    
    vv = [0.0] * 51
    rep = grabdata(repubs) 
    dem = grabdata(dems)    
    pop = grabdata(pops)    
    for i in range(51):
        vv[i] = (rep[i]-dem[i])/(rep[i]+dem[i]+1e-10)        
    colorspurple(vv, r, g, b) # was colors()    
    fig, ax = plt.subplots(figsize=(8, 8))
    plt.xticks([])
    plt.yticks([])
    ax.axis('off')
    pg = PSpage(ax)
    USmap(pg, 50.0, 450.0, 250.0, 450.0, r, g, b, pop, caption)
