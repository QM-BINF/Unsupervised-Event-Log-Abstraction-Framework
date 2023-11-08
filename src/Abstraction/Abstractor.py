import numpy as np 
import math
import pm4py as pm
import statistics as st
from datetime import timedelta
import os as os
from sklearn import cluster as skcl
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import seaborn as sns
import pandas as pd
import calendar
import time
from datetime import datetime

from src.Abstraction.utils_abstraction import *
from src.Abstraction.Session import Session
from src.Abstraction.Event import Event

from progressbar import progressbar as pb

class Abstractor :
    def __init__(self, fileName, threshold=10,attrNames=[],noTrace = None,toSession = True, parallel = False):
        self.name = fileName
        self.hidepb = parallel
        start = time.time()
        self.log = importLog(fileName)
        print(f"{self.name}: Importing Time:",time.time()-start)
        if noTrace != None:
            self.tracefy(limit = noTrace)
        if attrNames== [] and toSession == True:
            attrNames = pm.get_attributes(self.log)
            #print(attrNames)
            toRemove = ['org:resource','time:timestamp','(case)_variant-index','name','position','(case)_creator','concept:name','(case)_variant']
            for i in toRemove:
                if i in attrNames:
                    attrNames.remove(i)
        if toSession == True:
            #print('cerco sessioni')
            self.sessions = self.findSessionsNew(threshold,attrNames)

    def thresholdView (self,imgpath):
        difference = []
        for caseid,case in enumerate(self.log):
            added = []
            for event_id, event in enumerate(case):
                if event['lifecycle:transition'] == 'start' and event_id>0:
                    difference.append ((event["time:timestamp"]-next((e['time:timestamp'] for e in reversed(case[:event_id]) if e['lifecycle:transition'] == 'start'),event["time:timestamp"])).total_seconds())
                    ec = next((e for e in case[event_id:] if e['concept:name'] == event['concept:name'] and e['lifecycle:transition'] == 'complete'),None)
                    if ec != None and not started(ec, case, event_id):
                        added.append(case.index(ec))
                elif event['lifecycle:transition'] == 'complete' and event_id>0 and event not in added:
                    difference.append((event["time:timestamp"]-next((e['time:timestamp'] for e in reversed(case[:event_id]) if e['lifecycle:transition'] == 'start'),case[-1]['time:timestamp'])).total_seconds())
        if difference != []:
            mean = np.mean([d for d in difference if d>0])
            median = st.median([d for d in difference if d>0])
            print('mean',mean)
            plt.plot(difference,marker='o',linewidth = 0,zorder=1)
            plt.hlines(mean,xmin = 0, xmax = len(difference),color='red',linewidth=2,zorder = 2,label= 'Mean value = '+str(mean/60)+' min')
            plt.hlines(median,xmin = 0, xmax = len(difference),color='orange',linewidth=2,zorder = 3,label= 'Median value = '+str(median/60)+' min')
            plt.legend()
            plt.savefig(os.path.join(imgpath,'thresholdView.png'))
            plt.close()
            print('THRESHOLD VARIANCE' , np.std(np.divide(difference,[60 for i in difference])))
    
    def tracefy (self,limit):
        log = self.log[0]
        traced = []
        trace = []
        weekend = []
        for event_id, event in enumerate(log):
            if event_id == 0 or trace == []:
                trace.append(event)
            elif event['lifecycle:transition'] == 'start' and (trace[0]["time:timestamp"].hour <limit and event["time:timestamp"].   day == trace[0]["time:timestamp"].day and event["time:timestamp"].hour <limit) or (trace[0]["time:timestamp"].hour >= limit and ((
                    (event["time:timestamp"].day == (trace[0]["time:timestamp"].day)+1) and event["time:timestamp"].hour <limit) or 
                    (event["time:timestamp"].day == trace[0]["time:timestamp"].day and event["time:timestamp"].hour>=limit))):
                trace.append(event)
            elif event['lifecycle:transition'] == 'complete':
                starter = next((i for i,e in enumerate(reversed(trace)) if e['lifecycle:transition'] == 'start' and e['concept:name'] == event['concept:name']),None)
                if starter != None and not completed(trace,starter,event['concept:name']):
                        trace.append(event)
                elif (trace[0]["time:timestamp"].hour <limit and event["time:timestamp"].   day == trace[0]["time:timestamp"].day and event["time:timestamp"].hour <limit) or (trace[0]["time:timestamp"].hour >= limit and (((event["time:timestamp"].day == (trace[0]["time:timestamp"].day)+1) and event["time:timestamp"].hour <limit) or (event["time:timestamp"].day == trace[0]["time:timestamp"].day and event["time:timestamp"].hour>=limit))):
                    trace.append(event)
                else:
                    traced.append(trace)
                    trace = [event]
            else:
                traced.append( trace)
                trace = [event]
        self.log = traced

    def findSessionsNew(self,threshold,attrNames):
        start = time.time()
        if self.hidepb == False: print(f"Sessioning started at {datetime.fromtimestamp(start)}")
        self.attrNames = attrNames
        sessions = []
        loopvar = enumerate(self.log) if self.hidepb == True else pb(enumerate(self.log))
        for caseid,case in loopvar:
            added = []
            for event_id, event in enumerate(case):
                if event_id == 0 or session.events == []:
                    session = Session(caseid=caseid,events = [Event(event,attrNames)])
                elif ('lifecycle:transition' in event) and event['lifecycle:transition'] == 'start':
                    if event["time:timestamp"]-next((e.timestamp for e in reversed(session.events) if e.state == 'start'),session.events[-1].timestamp)<=timedelta(minutes=threshold):
                        session.addEvent(Event(event,attrNames))
                        ec = next((e for e in case[event_id:] if e['concept:name'] == event['concept:name'] and e['lifecycle:transition'] == 'complete'),None)
                        if ec != None and not started(ec, case, event_id) and (ec['time:timestamp'] - event['time:timestamp'])<= timedelta(hours=11):
                            session.addEvent(Event(ec,attrNames))
                            added.append(ec)
                    else:
                        sessions.append(session)
                        session = Session(caseid=caseid, events = [Event(event,attrNames)])
                elif not('lifecycle:transition' in event) or event['lifecycle:transition'] == 'complete':
                    if  event not in added:
                        if event["time:timestamp"]-next((e.timestamp for e in reversed(session.events) if e.state == 'start'),session.events[-1].timestamp)<=timedelta(minutes=threshold):
                            session.addEvent(Event(event,attrNames))
                        else:
                            sessions.append(session)
                            session = Session(caseid=caseid, events = [Event(event,attrNames)])
                '''
                else :
                    if session.events!=[]:
                        sessions.append(session)
                    session = Session(caseid=caseid, events = [Event(event,attrNames)])
                '''
            if sessions != [] and session != sessions[-1] and session.events!=[]:
                sessions.append(session)
                session = Session(caseid=caseid)
        distinct = []
        for i in sessions:
            distinct = list(set(distinct) | set(i.distinct))
        distinct.sort()
        self.distinct = distinct
        print(f"{self.name}: Sessioning Time:",time.time()-start)
        return sessions

    def encode (self, encoding,norm = 'session',useAttributes = False):
        start = time.time()
        if self.hidepb == False: print(f"Encoding started at {datetime.fromtimestamp(start)}")
        encDf = pd.DataFrame([], columns = self.distinct)
        loopvar = range(len(self.sessions)) if self.hidepb == True else pb(range(len(self.sessions)))
        if encoding == "time":
            for i in loopvar:
                self.sessions[i].timeEncodingNew(self.distinct)
                encDf = encDf.append(pd.Series(self.sessions[i].encoded, index = encDf.columns),ignore_index= True)
                if useAttributes:
                    self.sessions[i].addAttributesMeanDF(self.attrNames)
                    for j in self.attrNames:
                        encDf.loc[i,j] = self.sessions[i].attrEncoded[j]
        if encoding == 'freq':
            for i in loopvar:
                self.sessions[i].freqEncodingNew(self.distinct)
                encDf = encDf.append(pd.Series(self.sessions[i].encoded, index = encDf.columns),ignore_index= True)
                if useAttributes:
                    self.sessions[i].addAttributesMeanDF(self.attrNames)
                    for j in self.attrNames:
                        encDf.loc[i,j] = self.sessions[i].attrEncoded[j]
        if encoding == 'time' or useAttributes:
            encDf = linearEstimator(encDf,encDf.columns,self.sessions,self.distinct)
        onlyEvents = encDf.loc[:,self.distinct]
        if useAttributes:
            onlyAttr = encDf.loc[:,self.attrNames]
            onlyAttr = self.normalizeAttrNew(onlyAttr,self.attrNames)
            encDf.loc[:,self.attrNames] = onlyAttr
        if norm == 'session':
            onlyEvents = onlyEvents.div(onlyEvents.sum(axis=1),axis=0).replace(np.nan,0)
        elif norm == 'absolute':
            onlyEvents = self.normalizeEvents(onlyEvents)
        encDf.loc[:,self.distinct] = onlyEvents
        self.encodedLog = encDf
        print(f"{self.name}: Encoding Time:",time.time()-start)

    def normalizeAttrNew(self,attributes,newNames):
        shift = {i: abs(math.floor(np.min(attributes.loc[:,[i]].values.tolist()))) if np.min(attributes.loc[:,[i]].values.tolist()) <0 else 0  for i in self.attrNames}
        for i in newNames:
            attributes.loc[:,i] = attributes.loc[:,i]+shift[i]
        lower = {i: np.min(attributes.loc[:,[i]].values.tolist()) for i in self.attrNames}
        higher = {i: np.max(attributes.loc[:,[i]].values.tolist()) for i in self.attrNames}
        for i in newNames:
            attributes.loc[:,i] = (attributes.loc[:,i]-lower[i]).div(higher[i]-lower[i])
        return attributes

    def normalizeEvents(self,events):
        lower = {i: np.min(events.loc[:,[i]].values.tolist()) for i in self.distinct}
        higher = {i: np.max(events.loc[:,[i]].values.tolist()) for i in self.distinct}
        for i in self.distinct:
            events.loc[:,i] = (events.loc[:,i]-lower[i]).div(higher[i]-lower[i])
        return events.fillna(0)
    
    def findFrequency(self,max):
        absFreq = np.array([0 for i in self.distinct])
        for s in self.sessions:
            absFreq = np.sum([absFreq,s.frequency], axis=0)
        return absFreq.tolist()

    def attrCipher(self):
        values = {i:{} for i in self.attrNames}
        unique = {i:0 for i in self.attrNames}
        for s in self.sessions:
            for e in s.events:
                for a in e.attributes.values():
                    if a.value not in values[a.name].keys():
                        values[a.name][a.value] = unique[a.name]
                        unique[a.name] +=1
        return values

    def cluster (self,params = {"alg":"KMeans","num":10}):
        start = time.time()
        if self.hidepb == False: print(f"Clustering started at {datetime.fromtimestamp(start)}")
        encodedLog = self.encodedLog.values.tolist()
        if params["alg"].lower() == "kmeans":
            if not "runs" in params:
                params["runs"] = 0
            cluster = TTestKMeans2(params["num"],encodedLog)
            if self.hidepb == True: print("SSE : ", cluster.inertia_)
            print(f"{self.name}: Clustering Time:",time.time()-start)
            return cluster.predict(encodedLog),cluster.cluster_centers_
        elif params["alg"].lower() == "dbscan":
            cluster = skcl.DBSCAN(min_samples=params["minsamples"], eps = params["eps"]).fit(encodedLog)
            y_pred = cluster.labels_
            centers = calcCenters(y_pred, encodedLog)
            print(f"{self.name}: Clustering Time:",time.time()-start)
            if "assignNoisy" in params and params["assignNoisy"] == True:
                y_pred, centers = assignNoisyPoints(y_pred,encodedLog,centers)
            return y_pred,centers
    
    def exportSubP (self,y_pred,centers,path,SubDir):
        # path = path+'/Clusters/'+str(calendar.timegm(time.gmtime()))
        path = path+'/Clusters/'+SubDir.replace(".xes","")
        try:
            os.makedirs(path,exist_ok=True)
        except OSError:
            print ("Creation of the directory %s failed" % path)
        else:
            print ("Successfully created the directory %s " % path)
            frames = [[] for i in range(max(y_pred)+1)]
            for i,s in enumerate(self.sessions):
                frames[y_pred[i]].extend(s.export(self.attrNames,i))
            for i in range(max(y_pred)+1):
                ind = list(np.flip(np.argsort(centers[i][:len(self.distinct)])[-1:]))
                subP = concatName(self.distinct,ind)
                newFile = "cluster"+str(i)+'.xes'
                log = pd.concat(frames[i],ignore_index=True)
                log = pm.format_dataframe(log,case_id='case',activity_key='concept:name',timestamp_key='time:timestamp')
                log = pm.convert_to_event_log(log)
                fileNameAndPath=os.path.join(path,newFile)
                pm.write_xes(log,fileNameAndPath)
            if self.hidepb == True: print("Sessions exported")


    def convertLog(self,centers, y_pred,path,exportSes = False):
        start = time.time()
        if self.hidepb == False: print(f"Conversion started at {datetime.fromtimestamp(start)}")
        frames = []
        log = pd.DataFrame()
        loopvar = enumerate(self.sessions) if self.hidepb == True else pb(enumerate(self.sessions), prefix = "Converting sessions | ")
        for i,s in loopvar:
            abstracted = s.convertSession(centers[y_pred[i]],y_pred[i], self.distinct,self.attrNames)
            frames.append(abstracted)
        log = pd.concat(frames,ignore_index=True)
        log = pm.format_dataframe(log,case_id='case',activity_key='concept:name',timestamp_key='time:timestamp')

        log = pm.convert_to_event_log(log)
        
        try:
            os.makedirs(path,exist_ok=True)
        except OSError:
            print ("Creation of the directory %s failed" % path)
        else:
            exportname = os.path.join(path,os.path.basename(self.name).replace(".xes", "") + "_AbstractedLog" + ".xes")
            pm.objects.log.exporter.xes.exporter.apply(log, exportname, parameters = {"show_progress_bar": False})
            # pm.write_xes(log,os.path.join(path,os.path.basename(self.name).replace(".xes", "") + "_AbstractedLog" + ".xes"))

        if exportSes:
            self.exportSubP(y_pred,centers,path,os.path.basename(self.name))
        print(f"{self.name}: Conversion Time:",time.time()-start)

    def renameTasks (self,names,datapath):
        if names != {}:
            try:
                for ic,case in enumerate(self.log):
                    for ie,event in enumerate(case):
                            if event['cluster'] in names:
                                self.log[ic][ie]['concept:name'] = names[event['cluster']]
                pm.write_xes(self.log,os.path.join(datapath,self.name+".xes"))
            except:
                print('Event-log not suitable for renaming')
        else:
            print('No name given')

            
    def betterPlotting (self,centers, y_pred, path, params,mode = "linear"):
        distinct = self.distinct
        attrValues = self.attrNames
        if (len(centers[0])> len(distinct)):
            attr = [c[len(distinct):] for c in centers]
            attrNames = attrValues
        else:
            attr = []
            attrNames = []
        centers = np.array([c[range(len(distinct))] for c in centers])
        
        #Normalizzazione solo per plotting
        if any(i>1 for c in centers for i in c):
            for i,c in enumerate(centers):
                lower =  min(c)
                if lower <0 :
                    lower = abs(lower)
                    centers[i] = [j+lower for j in c]
            centers = centers/centers.sum(axis=1,keepdims = True)
        newCenters= []
        newDistinct = []
        for i,e in enumerate(distinct):
            drop = True
            for c in centers:
                if c[i] >= 0.01 :
                    drop = False
            if not drop:
                newDistinct.append(e)
        for i,c in enumerate(centers):
            cn = []
            for e in newDistinct:
                cn.append(c[distinct.index(e)])
            if attr != [] :
                cn = [*cn, *attr[i]]
            newCenters.append(cn)
        if attr != []:
            columns = newDistinct + attrNames
        else:
            columns = newDistinct
        df1 = pd.DataFrame(newCenters,index=range(max(y_pred)+1),columns =columns)
        logmin = 0.001
        fig, ax = plt.subplots()
        fig.set_size_inches((len(columns),len(newCenters)))
        if mode == "linear":
            sns.heatmap(df1, cmap="YlOrRd", linewidths=.5,xticklabels=True, yticklabels= True, ax = ax)
        else:
            sns.heatmap(df1, cmap="YlOrRd", linewidths=.5,norm =LogNorm(), vmin= max(centers.min().min(),logmin),xticklabels=True, yticklabels= True, ax= ax)
        if attr != []:
            ax.vlines([len(newDistinct)], *ax.get_ylim())
        ax.set_title(params)
        fig.savefig(path+".png",bbox_inches='tight') 
        ax.clear()