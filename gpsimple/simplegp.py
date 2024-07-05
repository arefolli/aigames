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

class SimpleGP:
  def __init__(self,parameters):
    self.liblogger=logging.getLogger('refo')
    self.ecosistema=Ecosystem(11,2)
    self.parameters=parameters
    self.report=Reportistica(parameters['repname'])
    self.autodromi=Autodromi()
    self.controllo=open("verifica.csv","w")

  def runtest(self):
    self.liblogger.info("start mock test")
    if self.parameters['create']:
      self.ecosistema.createplayers(self.parameters['sussistenza'],self.parameters['midlayer'],self.parameters['funzioni'])
    else:
      self.ecosistema.loadplayers("gp.dump")
    punteggio={}
    for kgen in range(self.parameters['gennum']):
      self.liblogger.info("running generation %d" % kgen )
      for iteration in range(0,self.parameters['genlen']):
        self.liblogger.info("iter %d" % iteration)
        self.controllo.write("generation => %d , iter => %d\n" %(kgen,iteration))
        actualval=self.campionato(self.parameters['gare'])
        for nn in punteggio.keys():
          punteggio[nn]= 0.8 * punteggio[nn]
        punti = 0.0
        orapunti={}
        lastval=-1.0
        #increment=1.0
        for rr in sorted(list(actualval.keys()),key=lambda x: actualval[x]):
          #if actualval[rr] == lastval :
          #  increment=increment + 1.0
          #else:
          #  punti = punti + increment
          #  lastval=actualval[rr]
          #  increment=1.0
          punti=actualval[rr]*actualval[rr]
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
    actualval=self.campionato(self.parameters['gare'])
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
    self.liblogger.debug("start valutazioni su autodromo %s di lunghezza %d " % (autodromename,self.autodromi.lunghezza(autodromename)))
    risultato={}
    finito=0
    giocatori=0
    for plname in self.ecosistema.getactiveplayers():
      risultato[plname]=self.corsalibera(plname,autodromename)
      giocatori=giocatori+1
      if risultato[plname] > 4300 :
        finito=finito +1
    self.controllo.write("AUTODROMO => %s , finiti => %d/%d\n " % (autodromename,finito,giocatori))
      #self.liblogger.debug("%s ha avuto punteggio %d" % (plname,risultato[plname]))
    return risultato.copy()

  def lanciodadi(self,numb):
    toret=[]
    faccie=['50','50','50','50','R','V']
    for rr in range(numb):
      toret.append(random.choice(faccie))
    return toret[:]

  def corsalibera(self,plname,adname):
    giri=0
    posizione=0
    marcia=1
    gomme=16
    benzina=16
    tempo=0
    lunghezza=self.autodromi.lunghezza(adname)
    nextbonus=True
    continua=True
    while continua:
      if giri > 2 :
        break
      lancio=self.lanciodadi(marcia)
      tempo=tempo+1
      if nextbonus :
        if marcia < 4 :
          mossa=1
        else:
          mossa=2
      else:
        mossa=0
      for nn in lancio:
        if nn == 'R':
          mossa=mossa+1
          benzina=benzina-1
        if nn == '50':
          mossa=mossa+1
      fullrun=mossa
      while mossa > 0 :
        mossa=mossa -1
        if fullrun > self.autodromi.vistasecca(adname,posizione):
          delta=fullrun - self.autodromi.vistasecca(adname,posizione)
          gomme=gomme - delta
          posizione=posizione + 1
          if posizione >= lunghezza:
            giri=giri +1
            posizione=posizione - lunghezza
            if benzina < 8 :
              benzina=16
              tempo=tempo+1
              marcia=1
              posizione=0
              mossa=0
            if gomme < 8 :
              gomme=16
              tempo=tempo+1
              marcia=1
              posizione=0
              mossa=0
        else:
          posizione=posizione + 1          
          if posizione >= lunghezza:
            giri=giri +1
            posizione=posizione - lunghezza
            if benzina < 8 :
              benzina=16
              tempo=tempo+1
              marcia=1
              posizione=0
              mossa=0
            if gomme < 8 :
              gomme=16
              tempo=tempo+1
              marcia=1
              posizione=0
              mossa=0              
      datipista=self.autodromi.vistasemplice(adname,posizione)
      inputs=[marcia,gomme,benzina] + datipista
      controllo=self.ecosistema.getplayer(plname).valuta(inputs)
      #controllo=(nextbonus,marcia) #inputs sono 11
      if controllo[0] > 0 :
        nextbonus = True
      else:
        nextbonus=False
      if ( 3 + 3 * controllo[1]) < 1.0 :
        marcia=max(1,marcia -3)
      elif ( 3 + 3 * controllo[1]) < 2.0 :
        marcia=max(1,marcia -2)
      elif ( 3 + 3 * controllo[1]) < 3.0 :
        marcia=max(1,marcia -1)
      elif ( 3 + 3 * controllo[1]) < 4.0 :
        marcia=min(6,marcia)
      elif ( 3 + 3 * controllo[1]) < 5.0 :
        marcia=min(6,marcia +1)
      else:
        marcia=min(6,marcia+2)
      if ( benzina < 1 ) or (gomme < 1 ):
        continua=False
    if giri > 2 : posizione = 0
    punteggio=1500 * giri + 10 * posizione - tempo
    if giri > 2 :
      self.liblogger.debug("WOW fine corsa per %s dopo %d giri , %d posizione e %d tempo => punteggio %d" % (plname,giri,posizione,tempo,punteggio)   )
      self.autodromi.checkrecord(adname,plname,tempo)      
    #self.liblogger.debug("dati %s , %d gomme e %d benzina" % (plname,gomme,benzina)   )    
    return punteggio    
        
if ( __name__ == '__main__' ):
  logger=logging.getLogger('refo')
  configurazione={'sussistenza' : 30 , 'genlen' : 150 , 'gennum' : 100 ,  'sonnumber' : 20 , 'repname' : 'gp.txt', 'gare' : 2 , 'create' : False, 'midlayer' : False, 'funzioni' : ['step','step','tanh'],'verbose' : False }
  options , remainder = getopt.getopt(sys.argv[1:],'ht:vmcl:n:s:',['verbose'])
  for opt,args in options:
    if opt in ('-v','--verbose'):
      configurazione['verbose']=True
    elif opt in ('-h'):
      print("esempio python ./simplegp.py -v -t [flat|standard]")
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
  handler = logging.handlers.RotatingFileHandler('simplegp.log', maxBytes=20000000, backupCount=3)
  handler.setFormatter(logging.Formatter("%(asctime)s | %(name)s | %(levelname)s | %(module)s | %(funcName)s | %(message)s"))
  handler.setLevel(mylevel)
  logger.addHandler(handler)
  logger.info("START evoluzione")
  random.seed()
  nowis=datetime.today()
  ecosistema=SimpleGP(configurazione)
  ecosistema.runtest()
  delta=datetime.today() - nowis
  logger.info("Done in %s" % str(delta))  
  logger.info("STOP")
