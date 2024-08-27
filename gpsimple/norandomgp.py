#! /usr/bin/env python3
import logging
import logging.handlers
import random
import psutil
import pymysql
from datetime import datetime, timedelta, date
from math import log, tanh, copysign, floor
import operator
import decimal
import statistics
import traceback
import numpy as np
import re
import random
import getopt
import sys
from math import log, tanh, copysign, floor
from functools import cmp_to_key
from superevoluzione import *



def taglio(lista,posizione):
  toret=[lista.get(posizione,0)]
  for aa in [1,2,3,4,5,6]:
    if (posizione + 1) > len(lista):
      posizione=0
    else:
      posizione=posizione+1
    toret.append(lista.get(posizione,0))
  return toret        




class Autodromi:
  def __init__(self,parameters={}):
    self.liblogger=logging.getLogger('refo')
    self.inventario={}
    self.crea_autodromi()

  def crea_autodromi(self):
    base={}
    self.records={}
    base['Monza']=[[10,7],[2,6],[10,3],[6,3],[10,8],[2,3],[10,4],[4,2],[10,2],[3,2],[10,12],[4,5],[10,12],[4,5],[10,8]]
    base['Spagna']=[[10,13],[3,2],[10,10],[4,3],[10,6],[2,4],[10,2],[4,2],[10,5],[3,3],[10,6],[4,2],[10,12],[2,3],[10,3],[3,5],[10,3],[5,2],[10,6],[5,3],[10,11]]
    base['Belgio']=[[10,5],[1,3],[10,12],[5,3],[10,13],[3,3],[10,5],[2,3],[10,2],[4,2],[10,2],[4,2],[10,7],[3,3],[4,5],[10,15],[6,2],[10,2],[2,3],[10,3],[4,3],[10,3]]
    base['Canada']=[[3,6],[2,2],[10,8],[3,3],[10,6],[3,5],[10,6],[4,3],[10,9],[1,3],[10,6],[6,3],[10,12],[3,3],[10,5]]
    base['UK']=[[10,7],[5,2],[10,7],[5,2],[10,3],[4,3],[10,15],[3,6],[10,6],[3,6],[10,6],[4,3],[10,4],[3,3],[10,2],[2,2],[10,2],[2,2],[10,2],[3,2],[10,3],[6,2],[10,5]]
    base['Imola']=[[10,8],[3,4],[10,6],[3,3],[2,2],[10,4],[4,2],[10,4],[3,2],[10,7],[3,3],[10,13],[5,1],[10,6],[2,4],[10,13],[2,3],[10,5]]
    base['USA']=[[10,14],[4,3],[10,3],[2,2],[10,3],[3,2],[10,2],[2,2],[10,8],[2,3],[4,3],[10,5],[3,3],[10,7],[6,3],[10,14],[6,3],[10,5]]
    base['Germania']=[[10,9],[6,2],[10,16],[2,3],[10,9],[2,3],[10,3],[4,4],[10,12],[3,3],[10,9],[4,3],[10,8],[2,5],[3,4],[10,3],[4,2],[10,5]]
    for cc in base.keys():
      self.inventario[cc]=[]
      for rr in base[cc]:
        for ii in range(rr[1]):
          self.inventario[cc].append(rr[0])
    for cc in base.keys():
       self.records[cc]=[8000,'NONE']   

  def checkrecord(self,adname,player,time):
    if time < self.records[adname][0]:
      self.liblogger.info("Nuovo record per %s fatto da %s con %d" %(adname,player,time)  )
      self.records[adname]=[time,player]

  def vistasemplice(self,name,pos):
    lunga=self.inventario[name]+self.inventario[name]
    if pos < 0 :
        pos = pos + len(self.inventario[name])
    fino=pos+8
    toret=lunga[pos:fino]
    return toret
      
  def vistasecca(self,name,pos):
    try:
      return self.inventario[name][pos]
    except:
      self.liblogger.error("mi hai chiesto %d per %s" %(pos,name) )
      raise Exception("unable to complete")
    
  def lunghezza(self,adname):
    return len(self.inventario[adname])


class FullGP:
  def __init__(self,parameters):
    self.liblogger=logging.getLogger('refo')
    self.ecosistema=RicoEcosystem(18,2) 
    self.parameters=parameters
    self.report=Reportistica(parameters['repname'])
    self.autodromi=Autodromi()
    self.controllo=open("verifica.csv","w")
    self.staticlancio={1: ['50'], 2: ['50','50'] , 3:['50','50','50'], 4: ['R','50','50','50'] , 5: ['50','R','50','50','50'] , 6: ['50','50','R','50','50','50'] }
    self.semifinalrule={12 : [[6,6],3] , 13 : [[6,7],3], 14 : [[7,7],3] , 15 : [[7,8],3], 16 : [[8,8],3], 17 : [[8,9],3],
                        18 : [[6,6,6],2], 19: [[6,6,7],2], 20 : [[6,7,7],2], 21 : [[7,7,7],2], 22 : [[7,7,8],2], 23 :[[7,8,8],2],
                        24 : [[8,8,8],2] , 25: [[9,8,8],2], 26: [[9,9,8],2], 27 : [[9,9,9],2] , 28 : [[10,9,9],2] , 29 : [[10,10,9],2] , 30: [[10,10,10],2] ,
                        31 : [[8,8,8,7],2] , 32 : [[8,8,8,8],2] , 33 : [[9,8,8,8],2] , 34 : [[9,9,8,8],2], 35 : [[9,9,9,8],2], 36 : [[9,9,9,9],2], 37 : [[10,9,9,9],2],
                        38 : [[10,10,9,9],2], 39 : [[10,10,10,9],2], 40 : [[10,10,10,10],2], 41 : [[9,8,8,8,8],2] , 42 : [[9,9,8,8,8],2] , 43 : [[9,9,9,8,8],2],
                        44 : [[9,9,9,9,8],2], 45 : [[9,9,9,9,9],2], 46 : [[10,9,9,9,9],2] , 47 : [[10,10,9,9,9],2] , 48 : [[10,10,10,9,9],2] , 49 : [[10,10,10,10,9],2] , 50 : [[10,10,10,10,10],2]}

  def lanciodadi(self,numb):
    toret=[]
    faccie=['50','50','50','50','R','V']
    for rr in range(numb):
      toret.append(random.choice(faccie))
    return toret[:]

  def sistemalancio(self,lista):
    toret=[]
    for rr in lista:
      toret.append('50')
    return toret[:]

    
  def runtest(self):
    self.liblogger.info("start mock test")
    if self.parameters['create']:
      self.ecosistema.createplayers(self.parameters['sussistenza'],self.parameters['midlayer'],self.parameters['funzioni'])
    else:
      self.ecosistema.loadplayers("gp.dump")
    punteggio={}
    for kgen in range(self.parameters['gennum']):
      self.liblogger.info("running generation %d" % kgen )
      for iter in range(0,self.parameters['genlen']):
        self.liblogger.info("iter %d" % iter)
        actualval=self.campionato(self.parameters['gare'])
        for nn in punteggio.keys():
          punteggio[nn]= 0.8 * punteggio[nn]
        punti = 0.0
        orapunti={}
        lastval=-1.0
        increment=1.0
        for rr in sorted(list(actualval.keys()),key=lambda x: actualval[x]):
          if actualval[rr] == lastval :
            increment=increment + 1.0
          else:
            punti = punti + increment
            lastval=actualval[rr]
            increment=1.0
          if rr in punteggio.keys():
            punteggio[rr]=punteggio[rr] + punti
          else:
            punteggio[rr]=punti
          orapunti[rr]=punti
        for nn in sorted(list(punteggio.keys()),key=lambda x: punteggio[x]):
          self.liblogger.info("%s ha avuto punteggio di %3.2f, ora ne prende %3.2f con punteggio totale %3.2f" % (nn,actualval[nn],orapunti[nn],punteggio[nn]))
        surplus=max(3,self.ecosistema.popolazione() - self.parameters['sussistenza'])
        modnum=random.choice(range(surplus-3,surplus+3))
        for ciclo in range(0,modnum):
          gamma=sorted(list(punteggio.keys()),key=lambda x: punteggio[x])
          preso=random.choice(gamma[0:5])
          self.liblogger.debug("peggiore %s" % gamma[0])
          self.ecosistema.terminateplayer(preso)
          del punteggio[preso]
          self.liblogger.info("rimosso %s" % preso)
        self.ecosistema.runmutations(5)
        self.ecosistema.radioterapy(self.parameters['funzioni'][1])
        self.ecosistema.runconnections(3)
      self.ecosistema.newgeneration()
      for rr in range(self.parameters['sonnumber']):
        self.ecosistema.nuovofiglio()
    actualval=self.campionato()
    for nn in punteggio.keys():
      punteggio[nn]= 0.6 * punteggio[nn]
    punti = 0.0
    for rr in sorted(list(actualval.keys()),key=lambda x: actualval[x]):
      if rr in punteggio.keys():
        punteggio[rr]=punteggio[rr] + punti
      else:
        punteggio[rr]=punti
      punti = punti + 1.0
    for nn in sorted(list(punteggio.keys()),key=lambda x: punteggio[x]):
      self.liblogger.info("%s ha avuto punteggio corrente di %3.2f con punteggio %3.2f" % (nn,actualval[nn],punteggio[nn]))        
    gamma=sorted(list(punteggio.keys()),key=lambda x: punteggio[x],reverse=True) 
    for gps in ['Monza','Spagna','Belgio','Canada','UK','Imola','USA','Germania']:
      self.liblogger.info("record per %s è di %s con %d" % (gps,self.autodromi.records[gps][1],self.autodromi.records[gps][0]) )    
    self.liblogger.info("migliore %s" % gamma[0])
    self.liblogger.info("storia del migliore %s" % self.ecosistema.getplayer(gamma[0]).storia)
    self.liblogger.info("descrizione del migliore %s" % str(self.ecosistema.getplayer(gamma[0]).copy()) )
    self.ecosistema.dumponfile("gp.dump")        

  def campionato(self,gare):
    campionato={}
    debugreg={}
    for aa in self.ecosistema.getactiveplayers():
      campionato[aa]=0
      debugreg[aa]={'performance' : [] , 'finiti' :0 }
    for cc in range(gare):
      for gps in ['Monza','Spagna','Belgio','Canada','UK','Imola','USA','Germania']:
        risgara=self.valutazione(gps)
        for cc in risgara.keys():
          debugreg[cc]['performance'].append(risgara[cc])
          if risgara[cc] > 29000:
            debugreg[cc]['finiti']=debugreg[cc]['finiti'] + 1
        apunti=sorted(list(risgara.keys()), key = lambda x : risgara[x])
        campionato[apunti[-1]]=campionato[apunti[-1]]+5
        campionato[apunti[-2]]=campionato[apunti[-2]]+3
        campionato[apunti[-3]]=campionato[apunti[-3]]+2
        campionato[apunti[-4]]=campionato[apunti[-4]]+1
    #punti=0
    for ss in sorted(list(campionato.keys()), key=lambda x: campionato[x]):
      self.liblogger.debug("%s ha avuto %d punti campionato" % (ss,campionato[ss]))
      best=ss
    media=statistics.mean(debugreg[best]['performance'])
    self.controllo.write("%s;%3.2f;%d\n" % (best,media,debugreg[cc]['finiti']))
    #  toout[ss]=punti
    #  punti=punti +1
    return campionato.copy()

  def valutazione(self,autodromename):
    self.liblogger.debug("start gara su autodromo %s di lunghezza %d " % (autodromename,self.autodromi.lunghezza(autodromename)))
    risultato={}
    listaplayers=list(self.ecosistema.getactiveplayers())
    random.shuffle(listaplayers)
    for cc in listaplayers:
      risultato[cc]=0
    idrule=len(listaplayers)
    if idrule in self.semifinalrule.keys():
      semifinalrule=self.semifinalrule[idrule]
    else:
      self.liblogger.error("idrule %d not defined" % idrule)
      raise Exception("configurazione insufficiente")
    finale=[]
    for cc in semifinalrule[0]:
      dd=cc
      semifinale=[]
      partialresult={}
      while dd > 0 :
        semifinale.append(listaplayers.pop(0))
        dd=dd - 1
      for cc in self.garavera(semifinale,autodromename):
        partialresult[cc[0]]=cc[1]
      ordine=sorted(partialresult.keys(), key=lambda x : partialresult[x], reverse = True)
      for rr in range(0,semifinalrule[1]):
        finale.append(ordine[rr])
    random.shuffle(finale)
    fullresult=self.garavera(finale,autodromename)
    for aa in fullresult:
      risultato[aa[0]]=aa[1]
    return risultato.copy()

  def garavera(self,partenti,autodromename):
    tempo=0
    self.liblogger.debug(f"Partenza {'-'.join(partenti)}" )
    lunghezza=self.autodromi.lunghezza(autodromename)
    quanti=len(partenti)
    stato={}
    posizione=0
    numero=3
    griglia=1
    raccolta={}
    for aa in partenti:
      if griglia > 2 :
        griglia=1
        posizione=posizione - 1
      else :
        griglia=griglia +1
      stato[aa]=[True,0,posizione,16,16,1,True,0]
      if posizione >= 0 : raccolta[posizione]=raccolta.get(posizione,0) + 1
    incorso=True
    while incorso:
      ordine=sorted(partenti,key = lambda x : (stato[x][1] * 1000 + stato[x][2]), reverse = True)
      #self.liblogger.debug(f"A {tempo:5} ordine {"-".join(ordine)}" )
      scia=[]  # [posizione, marcia , lancio]
      incorso=False
      tempo=tempo+1
      for rr in ordine :
        if not stato[rr][0] : continue
        incorso = True
        lancio=[]        
        for cc in scia:
          if cc[0] == (stato[rr][2] + 1 ) :
            if cc[1] == stato[rr][5] :
              lancio=self.sistemalancio(cc[2])
              break
        if len(lancio) < 1 :
          lancio=self.staticlancio[stato[rr][5]]
        scia.append([stato[rr][2],stato[rr][5],lancio[:]])
        if stato[rr][6] :
          if stato[rr][5] < 4 :
            mossa=1
          else:
            mossa=2
        else:
          mossa=0
        for nn in lancio:
          if nn == 'R':
            mossa=mossa+1
            stato[rr][3]=stato[rr][3]-1
          if nn == '50':
            mossa=mossa+1
        fullrun=mossa
        raccolta[stato[rr][2]]=raccolta.get(stato[rr][2],0) -1
        while mossa > 0 :
          if fullrun > self.autodromi.vistasecca(autodromename,stato[rr][2]):
            delta=fullrun - self.autodromi.vistasecca(autodromename,stato[rr][2])
            stato[rr][4]=stato[rr][4] - delta
          stato[rr][2]=stato[rr][2] + 1
          if stato[rr][2] >= lunghezza:
            stato[rr][1]=stato[rr][1] +1
            stato[rr][2]=stato[rr][3] - lunghezza
            if ( stato[rr][3] < 8 ) or ( stato[rr][4] < 8 ) :
              stato[rr][3]=16
              stato[rr][4]=16
              stato[rr][2]=0
              marcia=1
          mossa=mossa-1
        if raccolta.get(stato[rr][2],0) > 3 :
          stato[rr][2]=stato[rr][2]-1
          stato[rr][4]=stato[rr][4]-1
        if ( stato[rr][3] < 1 ) or (stato[rr][4] < 1 ) or (stato[rr][1] > 2 ):
          stato[rr][0]=False
          stato[rr][7]=1500 * stato[rr][1] + 10 * stato[rr][2] - tempo
          if ( stato[rr][1] < 3 ):
            self.liblogger.debug(f"{rr} is out at {tempo} con benzina {stato[rr][3]} , gomme {stato[rr][4]} e giri {stato[rr][1]}")
          else:
            self.liblogger.debug(f"WOW {rr} completed at {tempo} con benzina {stato[rr][3]} , gomme {stato[rr][4]} e giri {stato[rr][1]}")            
          if stato[rr][1] > 2 :
            self.autodromi.checkrecord(autodromename,rr,tempo)
        else :
          raccolta[stato[rr][2]]=raccolta.get(stato[rr][2],0) +1
      for rr in ordine :
        if not stato[rr][0] : continue
        datipista=self.autodromi.vistasemplice(autodromename,stato[rr][2])
        inputs=inputs=[stato[rr][5],stato[rr][4],stato[rr][3]] + datipista + taglio(raccolta,stato[rr][2])
        output=self.ecosistema.getplayer(rr).valuta(inputs)
        if output[0] > 0 :
          stato[rr][6] = True
        else:
          stato[rr][6]=False
        if ( 3 + 3 * output[1]) < 1.0 :
          stato[rr][5]=max(1,stato[rr][5] -3)
        elif ( 3 + 3 * output[1]) < 2.0 :
          stato[rr][5]=max(1,stato[rr][5] -2)
        elif ( 3 + 3 * output[1]) < 3.0 :
          stato[rr][5]=max(1,stato[rr][5] -1)
        elif ( 3 + 3 * output[1]) < 4.0 :
          stato[rr][5]=min(6,stato[rr][5])
        elif ( 3 + 3 * output[1]) < 5.0 :
          stato[rr][5]=min(6,stato[rr][5] +1)
        else:
          stato[rr][5]=min(6,stato[rr][5]+2)
    toret=[]
    for aa in partenti:
      toret.append([aa,stato[aa][7]])
    return toret[:]
          




if ( __name__ == '__main__' ):
  logger=logging.getLogger('refo')
  configurazione={'sussistenza' : 20 , 'genlen' : 150 , 'gennum' : 100 ,  'sonnumber' : 20 , 'repname' : 'gp.txt', 'gare' : 2 , 'create' : False, 'midlayer' : False, 'funzioni' : ['step','step','tanh'],'verbose' : False }
  options , remainder = getopt.getopt(sys.argv[1:],'ht:vmcl:n:s:',['verbose'])
  for opt,args in options:
    if opt in ('-v','--verbose'):
      configurazione['verbose']=True
    elif opt in ('-h'):
      print("esempio python ./fullgp.py -v -t [flat|standard]")
      exit(0)
    elif opt in ('-t'):
      if args == 'flat':
        configurazione['funzioni']= ['tanh','tanh','tanh']
      if args == 'minflat':
        configurazione['funzioni']= ['tanh','minstep','tanh']
    elif opt in ('-m'):
      configurazione['midlayer']= True
    elif opt in ('-l'):
      configurazione['genlen']= int(args)
    elif opt in ('-n'):
      configurazione['gennum']= int(args)
    elif opt in ('-s'):
      configurazione['sussistenza']= int(args)
    elif opt in ('-c'):
      configurazione['create']= True
  if configurazione['verbose'] :
    mylevel=logging.DEBUG
  else:
    mylevel=logging.INFO
  logger.setLevel(mylevel)
  handler = logging.handlers.RotatingFileHandler('fullgp.log', maxBytes=20000000, backupCount=3)
  handler.setFormatter(logging.Formatter("%(asctime)s | %(name)s | %(levelname)s | %(module)s | %(funcName)s | %(message)s"))
  handler.setLevel(mylevel)
  logger.addHandler(handler)
  logger.info("START evoluzione")
  random.seed()
  nowis=datetime.today()
  ecosistema=FullGP(configurazione)
  ecosistema.runtest()
  delta=datetime.today() - nowis
  logger.info("Done in %s" % str(delta))  
  logger.info("STOP")

