#! /usr/bin/env python3
# version 2 
import logging
import logging.handlers
import random
import psutil
import pymysql
from datetime import datetime , timedelta , date 
from math import log, tanh , copysign , floor
#from artwo import *
import operator
import decimal
import statistics
import traceback
import numpy as np
import re
import random
from math import log, tanh , copysign , floor
from functools import cmp_to_key

#TODO:
# - differenti funzioni di attivazione
# - nuovi gp (gara)
# - nuove simulazioni 
 



class Neuron:
  def __init__(self,copydata):
    self.liblogger=logging.getLogger('refo')
    self.bias=copydata[2]
    self.itsme=copydata[0]
    self.tipo=copydata[1]
    self.deep=copydata[3]
    self.function=copydata[4]

  def valuta(self,connectionvalues):
    valore=0
    for rr in connectionvalues:
      valore=valore+rr
    if self.function=='tanh':
      self.valore=tanh(valore)
    elif self.function == 'step':
      self.valore=valore=max(0.0,valore)
    elif self.function == 'minstep':
      self.valore=valore=max(0.1 * valore,valore)


  def getvalore(self):
    return self.valore

  def copy(self):
    return [self.itsme,self.tipo,self.bias,self.deep,self.function]



class Connection:
  def __init__(self,copydata,startNeuron):
    self.liblogger=logging.getLogger('refo')
    self.itsme=copydata[0]
    self.start=copydata[1]
    self.end=copydata[2]
    self.startNeuron=startNeuron
    self.peso=copydata[3]
    self.active=copydata[4]    

  def checkend(self,end):
    if self.active: 
      if self.end == end : 
        return True
    return False

  def setactive(self):
    self.active=True    
  
  def inactive(self):
    self.active=False    

  def valore(self):
    return self.startNeuron.getvalore()*self.peso

  def copy(self):
    return [self.itsme,self.start,self.end,self.peso,self.active]


class ConnectionManager:
  def __init__(self):
    self.liblogger=logging.getLogger('refo')
    self.connessioni={}
    self.currentid=0
    
  def checkandcreate(self,newid):
    if newid in self.connessioni.keys():
      return self.connessioni[newid]
    self.currentid=self.currentid+1
    self.connessioni[newid]=self.currentid
    return self.currentid


class Player:
  def __init__(self,id,front,lastline,connectionmanager,copydata):
    self.liblogger=logging.getLogger('refo')
    self.itsme=id
    self.outputline=lastline
    self.inputline=front
    self.getmappingstatico()
    self.connectionmanager=connectionmanager
    self.neuronlist={}
    self.connections={}
    self.order2eval=copydata['base'][1]
    self.progressivoNeuroni=copydata['base'][0]
    self.storia=copydata['base'][2]
    self.tipo=copydata['base'][3]
    for rr in copydata['neurons']:
     # self.liblogger.debug("creating neuron %s with len %d" % (rr[0],len(rr)))
      self.neuronlist[rr[0]]=Neuron(rr)
    for ss in copydata['connections']:
      self.connections[ss[0]]=Connection(ss,self.neuronlist[ss[1]])
    self.sistemaordine()

  def getmappingstatico(self):
    self.staticoinput={}
    for rr in range(0,self.inputline):
      nome="f%d" % rr
      self.staticoinput[nome]=rr
    
  def addfather(self,father):
    self.storia=self.storia + " => %s" % self.itsme 

  def testami(self):
    test=[]
    for aa in range(self.inputline):
      test.append(1)
    try:
      self.valuta(test)
      return True
    except:
      return False


  def valuta(self,invalues):
    tobevalued=self.order2eval[:]
    #for cc in invalues:
    #  self.neuronlist[tobevalued[0]].valuta([cc])
    #  tobevalued.remove(tobevalued[0])
    for aa in tobevalued :
      incomings=[]
      if self.neuronlist[aa].tipo == 'Front' :
        incomings.append(invalues[self.staticoinput[aa]])
      for gg in self.getconnections(aa):
        incomings.append(self.connections[gg].valore())
      self.neuronlist[aa].valuta(incomings)
    toret=[]
    for rr in range(0,self.outputline):
      id="l%d" % rr
      toret.append(self.neuronlist[id].getvalore())
    return toret

  def sistemaordine(self):
    if self.tipo=='Standard':
      temporaneo={}
      for cc in self.neuronlist.keys():
        ordine=self.neuronlist[cc].deep
        if ordine in temporaneo.keys():
          temporaneo[ordine].append(cc)
        else:
          temporaneo[ordine]=[cc]
      self.order2eval=[]
      for cc in sorted(list(temporaneo.keys())):
        for rr in temporaneo[cc]:
          self.order2eval.append(rr)
    elif self.tipo == 'Retro':
      temporaneo=[]
      for cc in self.neuronlist.keys():
        if cc[0] == 'f' :
          temporaneo[int(cc[1:])]=cc
        elif cc[0] == 'l' :
          temporaneo[1000000 + int(cc[1:])]=cc
        else:          
          temporaneo[1000 + int(cc[1:])]=cc
      for cc in sorted(list(temporaneo.keys())):
          self.order2eval.append(cc)

  def getconnections(self,idend):
    toret=[]
    for nn in self.connections.keys():
      if self.connections[nn].checkend(idend) :
        toret.append(nn)
    return toret        


  def copy(self):
    toret={}
    toret['base']=[self.progressivoNeuroni,self.order2eval.copy(),self.storia,self.tipo]
    toret['neurons']=[]
    for cc in self.neuronlist.keys():
      toret['neurons'].append(self.neuronlist[cc].copy())
    toret['connections']=[]
    for cc in self.connections.keys():
      toret['connections'].append(self.connections[cc].copy())
    return toret.copy()

class Reportistica:
  def __init__(self,reportname):
    self.report=open(reportname,'w')
    self.perfmanager={}
    self.perfmanager['players']={}
    self.perfmanager['registri']={'migliore' : []}

  def addplayer(self,id,gennum):
    self.perfmanager['players'][id]={'changeC' : 0 , 'changeN' : 0 , 'generation' : gennum , 'punteggi' : [] , 'peggiore' : 0}
    
  def addplayerperformance(self,id,punteggio):
    self.perfmanager['players'][id]['punteggi'].append(punteggio)

  def migliore(self,punteggio):
    self.perfmanager['registri']['migliore'].append(punteggio)

  def writemiglioramenti(self):
    self.report.write("Evoluzioni della media\n\n")
    dimcampione=int(len(self.perfmanager['registri']['migliore'])/20)
    for rr in range(0,20):
      da=rr*dimcampione
      ad=(rr +1)*dimcampione
      subset=self.perfmanager['registri']['migliore'][da:ad]
      media=statistics.mean(subset)
      self.report.write(" %3.2f => " % media)
    subset=self.perfmanager['registri']['migliore'][ad:]
    media=statistics.mean(subset)
    self.report.write(" %3.2f \n\n " % media)

  def registerworst(self,id):
    self.perfmanager['players'][id]['peggiore']=self.perfmanager['players'][id]['peggiore']+1
    
  def writeplayerstats(self,id):
    self.report.write("\n %s ha vissuto %d cicli, con una media di %3.2f \n" % (id,len(self.perfmanager['players'][id]['punteggi']), statistics.mean(self.perfmanager['players'][id]['punteggi'])))


class OldEcosystem:
  def __init__(self,front,lastline,tipoplayer='Standard'):
    self.liblogger=logging.getLogger('refo')
    self.manager=ConnectionManager()
    self.front=front
    self.lastline=lastline
    self.players={}
    self.tipo=tipoplayer
    self.ratemutation=[0.3,0.3,0.01,0.01,0.1,0.1]
    self.generationnumber=0
    self.idnumber={}
    self.idnumber[0]=0

  def getgeneration(self,name):
    val=re.search('g(.+)f.*',name)
    return int(val[1])


  def newgeneration(self):
    self.generationnumber=self.generationnumber+1
    self.idnumber[self.generationnumber]=0

  def createplayers(self,number,midlayer,funzioni):
    for nn in range(0,number):
      self.idnumber[self.generationnumber]=self.idnumber[self.generationnumber]+1
      self.createnewplayer("g%df%d" % (self.generationnumber,self.idnumber[self.generationnumber]),midlayer,funzioni)
      self.liblogger.debug("creato Player g%df%d" % (self.generationnumber,self.idnumber[self.generationnumber]))

  def runmutations(self,number):
    for cc in range(0,number):
      sc=random.choice(list(self.players.keys()))
      genum=self.getgeneration(sc)
      self.idnumber[genum]=self.idnumber[genum]+1
      self.createclone(sc,'g%df%d' % (genum,self.idnumber[genum]))
      self.mutations('g%df%d' % (genum,self.idnumber[genum]))

  def runconnections(self,number):
    for cc in range(0,number):
      if (random.uniform(0.0,1.0) < self.ratemutation[5]):
        #self.idnumber=self.idnumber+1
        mutando=random.choice(list(self.players.keys()))
        self.newconnection(mutando)

  def terminateplayer(self,id):
    del self.players[id]

  def popolazione(self):
    return len(self.players.keys())

  def getactiveplayers(self):
    return self.players.keys()
    
  def getplayer(self,name):
    return self.players[name]
    
  def createclone(self,fromid,toid):
    try:
      self.players[toid]=Player(toid,self.front,self.lastline,self.manager,self.players[fromid].copy())
    except:
      self.liblogger.error("error cloning %s" % str(self.players[fromid].copy()))
    self.players[toid].addfather(toid)
    self.liblogger.debug("Player %s figlio di %s" % (toid,fromid))

  def radioterapy(self,metrica):
    if (random.uniform(0.0,1.0) < self.ratemutation[4]):
      pmutato=random.choice(list(self.players.keys()))
      genum=self.getgeneration(pmutato)
      self.idnumber[genum]=self.idnumber[genum]+1
      self.createclone(pmutato,'g%df%d' % (genum,self.idnumber[genum]))
      mutato='g%df%d' % (genum,self.idnumber[genum])
      self.liblogger.debug("Player %s figlio di %s" % (mutato,pmutato))
      self.liblogger.warning("aggiunta neurone per %s " % mutato )
      dati=self.players[mutato].copy()
      link=random.choice(range(0,len(dati['connections'])))
      dati['base'][0]=dati['base'][0]+1
      nid="m%d" % dati['base'][0]
      dati['neurons'].append([nid,'Middle',random.uniform(-2.0,2.0),0,metrica])
      dati['connections'][link][4]=False
      id="%s->%s" % (dati['connections'][link][1],nid)
      idn=self.manager.checkandcreate(id)
      dati['connections'].append([id,dati['connections'][link][1],nid,dati['connections'][link][3],True])
      id="%s->%s" % (nid,dati['connections'][link][2])
      idn=self.manager.checkandcreate(id)
      dati['connections'].append([id,nid,dati['connections'][link][2],1.0,True])
      dati['neurons']=self.gestdeep(dati['neurons'],dati['connections'])
      dove=dati['base'][1].index(dati['connections'][link][1])
      dati['base'][1].insert(dove+1,nid)
      dati['base'][2]=dati['base'][2] + "R"
      self.players[mutato]=Player(id,self.front,self.lastline,self.manager,dati.copy())
    else:
      self.liblogger.debug("no radioterapy "  )

  def newconnection(self,idp):
    dati=self.players[idp].copy()
    primo=random.choice(dati['neurons'])
    secondo=random.choice(dati['neurons'])
    if primo[0]==secondo[0] :
      return False
    if primo[1] == 'Last':
      return False
    #if primo[3] > ( secondo[3] + 1 ) :
    #  self.liblogger.warning("possibile loop per %d > %d" %(primo[3],secondo[3]) )
    #  return False
    idn="%s->%s" % (primo[0],secondo[0])
    idnbis="%s->%s" % (secondo[0],primo[0])
    if ( self.connectionexists(idn,dati['connections']) or self.connectionexists(idnbis,dati['connections']) ) :
      return False
    dati['connections'].append([idn,primo[0],secondo[0],1.0,True])
    #self.liblogger.debug("player %s possible a new connection %s" % (idp,idn) )
    try:
      dati['neurons']=self.gestdeep(dati['neurons'],dati['connections'])
    except:
      return False
    #  dati['base'][1]=self.verifyorder(primo[0],secondo[0],dati['base'][1])
    dati['base'][2]=dati['base'][2] + "C"
    genum=self.getgeneration(idp)
    self.idnumber[genum]=self.idnumber[genum]+1
    self.createclone(idp,'g%df%d' % (genum,self.idnumber[genum]))
    nidp = 'g%df%d' % (genum,self.idnumber[genum])
    #self.players[nidp]=Player(nidp,self.front,self.lastline,self.manager,dati.copy())
    if self.players[nidp].testami() :
      self.liblogger.warning("player %s has a new connection %s" % (nidp,idn) )
    else:
      self.liblogger.error("purtroppo player va cancellato %s" % str(self.players[nidp].copy()) ) 
      self.terminateplayer(nidp)
    return True
    
  # def verifyorder(self, primo,secondo,lista):
    # idprimo=lista.index(primo)
    # idsecondo=lista.index(secondo)
    # if primo < secondo:
      # return lista
    # lista.insert(idprimo,lista.pop(idsecondo))
    # return lista
 
  def gestdeep(self,neurons,connections):
    maxdeep=100000
    deep=0
    comodo={}
    for nn in neurons:
      comodo[nn[0]]=nn
    controlla=True
    while controlla:
      controlla=False
      deep=deep+1
      if deep > maxdeep:
        self.liblogger.error("GOT MAXDEEP !!!")
        self.liblogger.debug("connections are %s" % str(connections)  )
        self.liblogger.debug("neurons are %s" % str(comodo)  )
        raise Exception("max deep exception")
      for cc in connections:
        if comodo[cc[1]][3] >= comodo[cc[2]][3] :
          comodo[cc[2]][3]=comodo[cc[1]][3] + 1
          controlla=True
    newneurons=[]
    for nn in comodo.keys():
      newneurons.append(comodo[nn])
    return newneurons[:]
    

  def connectionexists(self,conn,listaconn):
    for nn in listaconn:
      if conn == nn[0]:
        return True
    return False
       
       
  def mutations(self,id):
    dati=self.players[id].copy()
    newneurons=[]
    for nn in dati['neurons']:
      if (random.uniform(0.0,1.0) < self.ratemutation[0]):
     #   self.liblogger.debug("mutazione per %s a %s da %3.2f" %(id,nn[0],nn[2]) )
        nn[2]=nn[2] + random.uniform(-nn[2]/10.0,nn[2]/10.0)
      #  self.liblogger.debug("mutazione per %s a %s a %3.2f" %(id,nn[0],nn[2]) )
      if (random.uniform(0.0,1.0) < self.ratemutation[2]):
        self.liblogger.debug("flip per %s" % id )
        nn[2]=-nn[2]
      newneurons.append(nn)
    dati['neurons']=newneurons[:]
    newconn=[]
    for nn in dati['connections']:
      if (random.uniform(0.0,1.0) < self.ratemutation[0]):
     #   self.liblogger.debug("mutazione connessione per %s a %s da %3.2f" %(id,nn[0],nn[3]) )
        nn[3]=nn[3] + random.uniform(-nn[3]/10.0,nn[3]/10.0)
    #    self.liblogger.debug("mutazione connessione per %s a %s a %3.2f" %(id,nn[0],nn[3]) )
      if (random.uniform(0.0,1.0) < self.ratemutation[3]):
        self.liblogger.debug("flip connessione per %s" % id )
        nn[3]=-nn[3]
      newconn.append(nn)
    dati['connections']=newconn[:]
    self.players[id]=Player(id,self.front,self.lastline,self.manager,dati.copy())

  def nuovofiglio(self):
    padre=random.choice(list(self.players.keys()))
    madre=random.choice(list(self.players.keys()))
    if padre != madre :
      self.idnumber[self.generationnumber]=self.idnumber[self.generationnumber] + 1
      self.liblogger.debug("possibile figlio g%df%d da %s e %s" % (self.generationnumber,self.idnumber[self.generationnumber],padre,madre))
      self.generafiglio(padre,madre,'g%df%d' % (self.generationnumber,self.idnumber[self.generationnumber]))
      self.liblogger.info("creato figlio g%df%d da %s e %s" % (self.generationnumber,self.idnumber[self.generationnumber],padre,madre))
       
  def generafiglio(self,padre,madre,toid):
    pconf=self.players[padre].copy()
    mconf=self.players[madre].copy()
    newneurons=[]
    newconn=[]
    fatti=[]
    ordine=[]
    pneurons=pconf['neurons']
    mneurons=mconf['neurons']
    for nn in pneurons:
      fatti.append(nn[0])
      newneurons.append(self.sceglineurone(nn,mneurons))
      ordine.append(nn[0])
    for gg in mneurons:
      if not (gg[0] in fatti):
        newneurons.append(gg[:])
        ordine.append(nn[0])        
    pconn=pconf['connections']
    mconn=mconf['connections']
    fatti=[]
    for nn in pconn:
      fatti.append(nn[0])
      inverso=self.inverticonnessione(nn)
      fatti.append(inverso[0])
      newconn.append(self.scegliconnessione(nn,mconn))
    for gg in mconn:
      if not (gg[0] in fatti):
        newconn.append(gg[:])
    newdata={}
    newdata['base']=[len(newneurons) - self.front - self.lastline,ordine[:],"%s+%s => %s" % (padre,madre,toid),self.tipo]    
    newdata['connections']=newconn[:]
    newdata['neurons']=newneurons[:]
    if self.tipo=='Retro':
      self.players[toid]=Player(toid,self.front,self.lastline,self.manager,newdata.copy())
    else:
      try:
        newdata['neurons']=self.gestdeep(newdata['neurons'],newdata['connections'])
        self.players[toid]=Player(toid,self.front,self.lastline,self.manager,newdata.copy())
      except:
        self.liblogger.error("genitori %s e %s sono sterili per loop connessioni" % (padre,madre) )

  def sceglineurone(self,nn,lmadre):
    ritorno=nn[:]
    for kk in lmadre:
      if kk[0] == nn[0]:
        scelta=random.choice([0,1])
        if scelta > 0 :
          ritorno=kk[:]
    return ritorno
       
  def scegliconnessione(self,nn,lmadre):
    ritorno=nn[:]
    inverso=self.inverticonnessione(nn)
    for kk in lmadre:
      if kk[0] == nn[0]:
        scelta=random.choice([0,1])
        if scelta > 0 :
          ritorno=kk[:]
      if kk[0] == inverso[0]:
        scelta=random.choice([0,1])
        if scelta > 0 :
          ritorno=kk[:]
    return ritorno

  def inverticonnessione(self,conn):
    return ["%s->%s" % (conn[2],conn[1]),conn[2],conn[1],conn[3],True]
    
  def dumponfile(self,filename):
    fdump=open(filename,'w')
    for rr in self.players.keys():
      fdump.write("%s\n" % self.players[rr].copy() )
    fdump.close()

  def loadplayers(self,filename):
    self.idnumber[0]=0
    fdump=open(filename,'r')
    for cc in fdump.readlines():
      immagine=eval(cc)
      self.idnumber[0]=self.idnumber[0]+1
      idplayer="g0f%d" % (self.idnumber[0])
      immagine['base'][2]=idplayer
      self.players[idplayer]=Player(idplayer,self.front,self.lastline,self.manager,immagine.copy())
      self.liblogger.debug("creato Player %s" % idplayer )            

  def createsingleplayer(self,immagine):
    idplayer="test"
    self.players[idplayer]=Player(idplayer,self.front,self.lastline,self.manager,immagine.copy())
  
  def createnewplayer(self,idplayer,midlayer,funzioni):
    tocreate={}
    order2eval=[]
    inmezzo=0
    tocreate['neurons']=[]
    tocreate['connections']=[]
    for rr in range(0,self.front):
      id="f%d" % rr
      tocreate['neurons'].append([id,'Front',random.uniform(-2.0,2.0),0,funzioni[0]])
      order2eval.append(id)
    if midlayer:
      inmezzo=int(self.front/2)
      for rr in range(0,inmezzo):
        id="m%d" % rr
        tocreate['neurons'].append([id,'Last',random.uniform(-2.0,2.0),1,funzioni[1]])
        order2eval.append(id)
      for rr in range(0,self.lastline):
        id="l%d" % rr
        tocreate['neurons'].append([id,'Last',random.uniform(-2.0,2.0),10,funzioni[2]])
        order2eval.append(id)
      for rr in range(0,self.front):
        for cc in range(0,inmezzo):
          id="f%d->m%d" % (rr,cc)
          idn=self.manager.checkandcreate(id)
          tocreate['connections'].append([id,"f%d" % rr,"m%d" % cc,1.0,True])
      for rr in range(0,inmezzo):
        for cc in range(0,self.lastline):
          id="m%d->l%d" % (rr,cc)
          idn=self.manager.checkandcreate(id)
          tocreate['connections'].append([id,"m%d" % rr,"l%d" % cc,1.0,True])
    else:
      for rr in range(0,self.lastline):
        id="l%d" % rr
        tocreate['neurons'].append([id,'Last',random.uniform(-2.0,2.0),10,funzioni[2]])
        order2eval.append(id)
      for rr in range(0,self.front):
        for cc in range(0,self.lastline):
          id="f%d->l%d" % (rr,cc)
          idn=self.manager.checkandcreate(id)
          tocreate['connections'].append([id,"f%d" % rr,"l%d" % cc,1.0,True])
    tocreate['base']=[inmezzo,order2eval[:],idplayer,self.tipo]
    self.players[idplayer]=Player(idplayer,self.front,self.lastline,self.manager,tocreate.copy())




class RicoPlayer:
  def __init__(self,nome,front,lastline,tipoplayer='Standard'):
    self.front=front
    self.itsme=nome
    self.lastline=lastline
    self.finoa=front+lastline
    self.storia=''
    self.tipoplayer=tipoplayer
    self.iterazioni={'Standard' : 5 , 'Super' : 10 }

  def generate(self,midlayer):
    self.storia="new"
    if midlayer:
      layerincrease=75
    else:
      layerincrease=32
    self.dimensione=self.front+self.lastline+layerincrease
    self.internalmatrix=np.zeros((self.dimensione,self.dimensione))
    to_modify=int(self.dimensione*self.dimensione/8)
    for ncel in range(0,to_modify):
      riga=random.choice(range(0,self.dimensione))
      colonna=random.choice(range(0,self.dimensione))
      if self.internalmatrix[riga,colonna] == 0 :
        self.internalmatrix[riga,colonna] = random.uniform(-2.0,2.0)
    pbase=[]
    for ncel in range(0,self.dimensione):
      pbase.append(random.uniform(-5.0,5.0))
    self.internalmatrix=np.vstack([pbase,self.internalmatrix])

  def fromparents(self,padre,madre):
    self.storia="%s + %s" % (padre.itsme,madre.itsme)
    pdim=padre.dimensione
    mdim=madre.dimensione
    self.dimensione=max(pdim,mdim)
    self.internalmatrix=np.zeros((self.dimensione+1,self.dimensione))
    for cc in range(0,self.dimensione):
      for rr in range(0,self.dimensione+1):
        if rr > pdim :
          self.internalmatrix[rr,cc]=madre.internalmatrix[rr,cc]
        elif rr > mdim:
          self.internalmatrix[rr,cc]=padre.internalmatrix[rr,cc]
        elif cc > (pdim -1):
          self.internalmatrix[rr,cc]=madre.internalmatrix[rr,cc]
        elif cc > (mdim -1):
          self.internalmatrix[rr,cc]=padre.internalmatrix[rr,cc]
        else:
          if madre.internalmatrix[rr,cc] != 0.0 :
            if padre.internalmatrix[rr,cc] != 0.0 :
              self.internalmatrix[rr,cc]=random.choice([madre.internalmatrix[rr,cc],padre.internalmatrix[rr,cc]])
            else:
              self.internalmatrix[rr,cc]=madre.internalmatrix[rr,cc]
          else:
            if padre.internalmatrix[rr,cc] != 0.0 :
              self.internalmatrix[rr,cc]=padre.internalmatrix[rr,cc]
      

  def valuta(self,inputs):
    vettore=np.array(inputs)
    delta=self.dimensione-len(inputs)
    vettore=np.hstack((vettore,np.array([0]*delta)))
    for rr in range(0,self.iterazioni[self.tipoplayer]):
      inputv=np.hstack((np.array(1),vettore))
      vettore=np.tanh(np.dot(inputv,self.internalmatrix))
    return vettore[self.front:self.finoa].tolist()

  def radioterapy(self):   
    righe=self.dimensione
    daaggiungere=np.array([0.001]*righe)
    laterale=np.array([0.001]*(righe+2))
    laterale=laterale[:, np.newaxis]
    self.internalmatrix=np.vstack([self.internalmatrix,daaggiungere])
    self.internalmatrix=np.hstack([self.internalmatrix,laterale])
    self.dimensione=self.dimensione+1
    
  def getstoria(self):
    return self.storia
      
  def getmatrix(self):
    return self.internalmatrix.copy()

  def setmatrix(self,inmatrix):
    self.internalmatrix=inmatrix.copy()

  def setdimensione(self,dim):
    self.dimensione=dim
      
  def copyfrom(self,sorgente):
    self.internalmatrix=sorgente.getmatrix()
    self.dimensione=sorgente.dimensione
    self.storia=sorgente.getstoria() + " => %s" % self.itsme    
      
  def runmutations(self,mute_rate,flip_rate):
    for cc in range(0,self.iterazioni[self.tipoplayer]):
      if (random.uniform(0.0,1.0) < mute_rate) :
        riga=random.choice(range(0,self.dimensione+1))
        colonna=random.choice(range(0,self.dimensione))
        if self.internalmatrix[riga,colonna] != 0.0 :
          self.internalmatrix[riga,colonna] =  self.internalmatrix[riga,colonna] * ( 9.0/10.0 + random.uniform(0.0,0.2))
        else:
          self.internalmatrix[riga,colonna] =  random.uniform(-0.5,0.5)
      if (random.uniform(0.0,1.0) < flip_rate):        
        riga=random.choice(range(0,self.dimensione+1))
        colonna=random.choice(range(0,self.dimensione))
        self.internalmatrix[riga,colonna] =  -1.0 * self.internalmatrix[riga,colonna] 

  def upperconnection(self):
    riga=random.choice(range(0,self.dimensione+1))
    colonna=random.choice(range(0,self.dimensione))
    if self.internalmatrix[riga,colonna] != 0.0 :
      if ((self.internalmatrix[riga,colonna] < 1.0) or (self.internalmatrix[riga,colonna] > -1.0)) :
        self.internalmatrix[riga,colonna]=self.internalmatrix[riga,colonna]*10.0
      else:
        self.internalmatrix[riga,colonna]=self.internalmatrix[riga,colonna]*2.5
    else:
      self.internalmatrix[riga,colonna] =  random.uniform(-1.5,1.5)

  def copy(self):
    toret={}
    toret['base']=[self.itsme,self.front,self.lastline,self.tipoplayer,self.storia,self.dimensione]
    #toret['matrix']=self.internalmatrix
    return toret.copy()


###end of rico


class EvoPlayer:
  def __init__(self,nome,front,lastline,tipoplayer='Standard'):
    self.front=front
    self.itsme=nome
    self.lastline=lastline
    self.layers=[]
    self.storia=''

  def generate(self,midlayer):
    self.storia="new"
    if midlayer:
      layerincrease=[10,12,15,15,12,10]
    else:
      layerincrease=[10,12,10]
    self.layernum=[self.front]
    actual=self.front
    for rr in layerincrease:
      actual=actual + rr
      self.layers.append(np.zeros((self.layernum[-1],rr)))
      self.layernum.append(actual)
    self.layers.append(np.zeros((actual,self.lastline)))
    ''' per tutti i layer calcolo il numero di celle e ne calcolo un quinto 
        poi inizializzo quel numero di caselle al massimo'''
    for rr in range(0,len(self.layers)):
      righe,colonne=self.layers[rr].shape
      to_modify=int(righe*colonne/4)
      for ncel in range(0,to_modify):
        riga=random.choice(range(0,righe))
        colonna=random.choice(range(0,colonne))
        if self.layers[rr][riga,colonna] == 0 :
          self.layers[rr][riga,colonna] = random.uniform(-2.0,2.0)
    ''' devo aggiungere i bias, lo aggiungo come una riga all'inizio della matrice '''
    for rr in range(0,len(self.layers)):
      righe,colonne=self.layers[rr].shape
      pbase=[]
      for ncel in range(0,colonne):
        pbase.append(random.uniform(-5.0,5.0))
      self.layers[rr]=np.vstack([pbase,self.layers[rr]])

  def fromparents(self,padre,madre):
    self.storia="%s + %s" % (padre.itsme,madre.itsme)
    self.layernum=[]
    players=len(padre.layers)
    mlayers=len(madre.layers)
    if players > mlayers:
      nlayers=players
    else:
      nlayers=mlayers
    for aa in range(0,nlayers):
      prighe,pcolonne=padre.layers[aa].shape   #qui ci vorranno i try, e magari una buona idea per intercettare casi con numo di layer differenti
      mrighe,mcolonne=madre.layers[aa].shape
      self.layers.append(np.zeros((max(prighe,mrighe),max(pcolonne,mcolonne))))
      self.layernum.append(max(prighe,mrighe))
      for cc in range(0,max(pcolonne,mcolonne)):
        for dd in range(0,max(prighe,mrighe)):
          if dd >= prighe :
            self.layers[aa][cc,dd]=madre.layers[aa][cc,dd]
          elif dd >= mrighe:
            self.layers[aa][cc,dd]=padre.layers[aa][cc,dd]
          elif cc >= pcolonne :
            self.layers[aa][cc,dd]=madre.layers[aa][cc,dd]
          elif cc >=mcolonne:             
            self.layers[aa][cc,dd]=madre.layers[aa][cc,dd]
          else:
            if padre.layers[aa][cc,dd] != 0.0 :
              if madre.layers[aa][cc,dd] != 0.0 :
                self.layers[aa][cc,dd]=random.choice([padre.layers[aa][cc,dd],madre.layers[aa][cc,dd]])
              else:
                self.layers[aa][cc,dd]=padre.layers[aa][cc,dd]
            else:
              if madre.layers[aa][cc,dd] != 0.0 :
                self.layers[aa][cc,dd]=madre.layers[aa][cc,dd]


  def valuta(self,inputs):
    vettore=np.array(inputs)
    for rr in range(0,len(self.layers)):
      inputv=np.hstack((np.array(1),vettore))
      output=np.tanh(np.dot(inputv,self.layers[rr]))
      vettore=np.hstack((vettore,output))
    return output.tolist()

  def radioterapy(self):
    dove=random.choice(range(0,len(self.layers)-1))
    righe,colonne=self.layers[dove].shape
    daaggiungere=np.array([0.001]*righe)
    daaggiungere=daaggiungere[:, np.newaxis]
    self.layers[dove]=np.hstack([self.layers[dove],daaggiungere])
    self.layernum[dove]=self.layernum[dove]+1
    dove=dove+1
    while dove < len(self.layers):
      ra,ca=self.layers[dove].shape
      daaggiungere=np.array([0.0001]*ca)
      daaggiungere=daaggiungere[:, np.newaxis].transpose()
      layers[dove]=np.vstack([layers[dove][0:colonne,:],daaggiungere,layers[dove][colonne:,:]])
      self.layernum[dove]=self.layernum[dove]+1
    

  def getlayers(self):
    return self.layers[:]

  def getlayernum(self):
    return self.layernum[:]

  def getstoria(self):
    return self.storia
      
  def copyfrom(self,sorgente):
    self.layernum=sorgente.getlayernum()
    self.layers=sorgente.getlayers()
    self.storia=sorgente.getstoria() + " => %s" % self.itsme    
      
  def runmutations(self,mute_rate,flip_rate):
    for cc in range(0,len(self.layers)):
      if (random.uniform(0.0,1.0) < mute_rate) :
        righe, colonne = self.layers[cc].shape
        riga=random.choice(range(0,righe))
        colonna=random.choice(range(0,colonne))
        if self.layers[cc][riga,colonna] != 0 :
          self.layers[cc][riga,colonna] =  self.layers[cc][riga,colonna] * ( 9.0/10.0 + random.uniform(0.0,0.2))
        else:
          self.layers[cc][riga,colonna] =  random.uniform(-0.5,0.5)
      if (random.uniform(0.0,1.0) < flip_rate):        
        righe, colonne = self.layers[cc].shape
        riga=random.choice(range(0,righe))
        colonna=random.choice(range(0,colonne))
        self.layers[cc][riga,colonna] =  -1.0 * self.layers[cc][riga,colonna] 

class Ecosystem:
  def __init__(self,front,lastline,tipoplayer='Standard'):
    self.liblogger=logging.getLogger('refo')
    self.front=front
    self.lastline=lastline
    self.players={}
    self.tipo=tipoplayer
    self.ratemutation=[0.3,0.3,0.01,0.01,0.1,0.1]
    self.generationnumber=0
    self.idnumber={}
    self.idnumber[0]=0

  def getgeneration(self,name):
    val=re.search('g(.+)f.*',name)
    return int(val[1])


  def newgeneration(self):
    self.generationnumber=self.generationnumber+1
    self.idnumber[self.generationnumber]=0

  def createplayers(self,number,midlayer,funzioni):
    for nn in range(0,number):
      self.idnumber[self.generationnumber]=self.idnumber[self.generationnumber]+1
      nome="g%df%d" % (self.generationnumber,self.idnumber[self.generationnumber])
      self.players[nome]=EvoPlayer(nome,self.front,self.lastline,self.tipo)
      self.players[nome].generate(midlayer)
      self.liblogger.debug("creato Player g%df%d" % (self.generationnumber,self.idnumber[self.generationnumber]))

  def runmutations(self,number):
    for cc in range(0,number):
      sc=random.choice(list(self.players.keys()))
      genum=self.getgeneration(sc)
      self.idnumber[genum]=self.idnumber[genum]+1
      self.createclone(sc,'g%df%d' % (genum,self.idnumber[genum]))
      self.players['g%df%d' % (genum,self.idnumber[genum])].runmutations(self.ratemutation[0],self.ratemutation[3])

  def runconnections(self,number):
    if (random.uniform(0.0,10.0) < self.ratemutation[5]):
      self.liblogger.warn("Nuovi layer non ancora implementato.. peccato")


  def terminateplayer(self,id):
    del self.players[id]

  def popolazione(self):
    return len(self.players.keys())

  def getactiveplayers(self):
    return self.players.keys()
    
  def getplayer(self,name):
    return self.players[name]
    
  def createclone(self,fromid,toid):
    self.players[toid]=EvoPlayer(self.front,self.lastline,self.tipo)
    self.players[toid].copyfrom(self.players[fromid])


  def radioterapy(self,metrica):
    if (random.uniform(0.0,1.0) < self.ratemutation[4]):
      pmutato=random.choice(list(self.players.keys()))
      genum=self.getgeneration(pmutato)
      self.idnumber[genum]=self.idnumber[genum]+1
      self.createclone(pmutato,'g%df%d' % (genum,self.idnumber[genum]))
      mutato='g%df%d' % (genum,self.idnumber[genum])
      self.liblogger.debug("Player %s figlio di %s" % (mutato,pmutato))
      self.liblogger.warning("aggiunta neurone per %s " % mutato )
      self.players[mutato].radioterapy()
    else:
      self.liblogger.debug("no radioterapy "  )
    raise Exception("yet not implemented")
       
       
  def nuovofiglio(self):
    padre=random.choice(list(self.players.keys()))
    madre=random.choice(list(self.players.keys()))
    if padre != madre :
      self.idnumber[self.generationnumber]=self.idnumber[self.generationnumber] + 1
      figlio="g%df%d" % (self.generationnumber,self.idnumber[self.generationnumber])
      self.liblogger.debug("possibile figlio %s da %s e %s" % (figlio,padre,madre))
      self.players[figlio]=EvoPlayer(self.front,self.lastline,self.tipo)
      self.players[figlio].fromparents(self.players[padre],self.players[madre])
      self.liblogger.info("creato figlio %s da %s e %s" % (figlio,padre,madre))
       
    
  def dumponfile(self,filename):
    raise Exception("dump yet not implemented")

  def createsingleplayer(self,immagine):
    raise Exception("yet not implemented")
  


class RicoEcosystem:
  def __init__(self,front,lastline,tipoplayer='Standard'):
    self.liblogger=logging.getLogger('refo')
    self.front=front
    self.lastline=lastline
    self.players={}
    self.tipo=tipoplayer
    self.ratemutation=[0.3,0.3,0.01,0.01,0.1,0.1]
    self.generationnumber=0
    self.idnumber={}
    self.idnumber[0]=0

  def getgeneration(self,name):
    val=re.search('g(.+)f.*',name)
    return int(val[1])


  def newgeneration(self):
    self.generationnumber=self.generationnumber+1
    self.idnumber[self.generationnumber]=0

  def createplayers(self,number,midlayer,funzioni):
    for nn in range(0,number):
      self.idnumber[self.generationnumber]=self.idnumber[self.generationnumber]+1
      nome="g%df%d" % (self.generationnumber,self.idnumber[self.generationnumber])
      self.players[nome]=RicoPlayer(nome,self.front,self.lastline,self.tipo)
      self.players[nome].generate(midlayer)
      self.liblogger.debug("creato Player g%df%d" % (self.generationnumber,self.idnumber[self.generationnumber]))

  def runmutations(self,number):
    for cc in range(0,number):
      sc=random.choice(list(self.players.keys()))
      genum=self.getgeneration(sc)
      self.idnumber[genum]=self.idnumber[genum]+1
      self.createclone(sc,'g%df%d' % (genum,self.idnumber[genum]))
      self.players['g%df%d' % (genum,self.idnumber[genum])].runmutations(self.ratemutation[0],self.ratemutation[3])

  def runconnections(self,number):
    for cc in range(0,number):
      if (random.uniform(0.0,1.0) < self.ratemutation[5]):
        #self.idnumber=self.idnumber+1
        mutando=random.choice(list(self.players.keys()))
        self.players[mutando].upperconnection()

  def terminateplayer(self,id):
    del self.players[id]

  def popolazione(self):
    return len(self.players.keys())

  def getactiveplayers(self):
    return self.players.keys()
    
  def getplayer(self,name):
    return self.players[name]
    
  def createclone(self,fromid,toid):
    self.players[toid]=RicoPlayer(toid,self.front,self.lastline,self.tipo)
    self.players[toid].copyfrom(self.players[fromid])


  def radioterapy(self,metrica):
    if (random.uniform(0.0,1.0) < self.ratemutation[4]):
      pmutato=random.choice(list(self.players.keys()))
      genum=self.getgeneration(pmutato)
      self.idnumber[genum]=self.idnumber[genum]+1
      self.createclone(pmutato,'g%df%d' % (genum,self.idnumber[genum]))
      mutato='g%df%d' % (genum,self.idnumber[genum])
      self.liblogger.debug("Player %s figlio di %s" % (mutato,pmutato))
      self.liblogger.warning("aggiunta neurone per %s " % mutato )
      self.players[mutato].radioterapy()
    else:
      self.liblogger.debug("no radioterapy "  )
       
       
  def nuovofiglio(self):
    padre=random.choice(list(self.players.keys()))
    madre=random.choice(list(self.players.keys()))
    if padre != madre :
      self.idnumber[self.generationnumber]=self.idnumber[self.generationnumber] + 1
      figlio="g%df%d" % (self.generationnumber,self.idnumber[self.generationnumber])
      self.liblogger.debug("possibile figlio %s da %s e %s" % (figlio,padre,madre))
      self.players[figlio]=RicoPlayer(figlio,self.front,self.lastline,self.tipo)
      self.players[figlio].fromparents(self.players[padre],self.players[madre])
      self.liblogger.info("creato figlio %s da %s e %s" % (figlio,padre,madre))
       
    
  def dumponfile(self,filename):
    fdump=open(filename,'w')
    tofile={}
    for rr in self.players.keys():
      fdump.write("%s\n" % self.players[rr].copy() )
      tofile[self.players[rr].itsme]=self.players[rr].internalmatrix
    fdump.close()
    dfile='dati_' + filename
    np.savez(dfile,**tofile)

  def loadplayers(self,filename):
    self.idnumber[0]=0
    fdump=open(filename,'r')
    mapping={}
    for cc in fdump.readlines():
      immagine=eval(cc)
      self.idnumber[0]=self.idnumber[0]+1
      idplayer="g0f%d" % (self.idnumber[0])
      mapping[idplayer]=immagine['base'][0]
      self.players[idplayer]=RicoPlayer(idplayer,immagine['base'][1],immagine['base'][2],immagine['base'][3])
      self.players[idplayer].setdimensione(immagine['base'][4])
      self.liblogger.debug("creato Player %s" % idplayer )
    dfile='dati_' + filename + '.npz'
    oldmatrix=np.load(dfile)
    for cc in list(self.players.keys()):
      self.players[cc].setmatrix(oldmatrix[mapping[cc]])
      self.liblogger.debug("aggiunta matrice %s" % cc )            




  def createsingleplayer(self,immagine):
    raise Exception("yet not implemented")
  
