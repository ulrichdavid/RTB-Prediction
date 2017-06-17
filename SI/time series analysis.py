#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 16 17:17:52 2017

@author: dulrich@kargo.com

Performs analysis on tracker data from articles

"""
import pandas as pd
import matplotlib.pyplot as plt
import os


files = ["american-detained-nk.csv",
         "london-attack.csv",
         "michael-flynn-testimony.csv",
         "ohio-nightclub-shooting.csv",
         "trump-crowd-size.csv",
         "trump-eo-obamacare.csv",
         "trump-repub-support.csv",
         "trump-women-march.csv",
         "racoon-stuck.csv",
         "aa-video-confrontation.csv"
         ]
         
# initialize the graph
plt.figure(figsize=(10,5)) 
lifecycle = plt.figure(1)
ax1 = lifecycle.add_subplot(111)

decay = plt.figure(1)
ax2 = decay.add_subplot(111)

def graph_lifespan(X, y, file):
    ax1.plot(X, y, label=file)
    ax1.legend(loc='upper right', shadow=True)
    
def graph_decay(X, y, file):
    ax2.plot(X, y, label=file)
    
directory = os.path.join("d:\\","Kargo\\SI")
print(directory)
for root,dirs,files in os.walk(directory):
    for file in files:
       if file.endswith(".csv"):
           X = []
           j = 0
           df = pd.read_csv(file, index_col=None)
           y = df['COUNT(*)']
           
           for i in y:
               j+=1
               X.append(j)
           
           #graph_lifespan(X,y, file)
           graph_decay(X, pd.Series(y).pct_change(), file)
           
# focus the graph into 15 days with a cap of 5M impressions 
plt.axis([1,30,-2,10])
ax1.set_title('CNN Article Lifespan')
ax1.set_xlabel('Days')
ax1.set_ylabel('Impressions')

ax2.set_title('CNN Article Decay')
ax2.set_xlabel('Days')
ax2.set_ylabel('% Change Day/Day')

plt.show()           
   
"""
y = df['COUNT(*)']
X = df['DY']

# put impressions in order
X = []
j = 0
for i in y:
    j+=1
    X.append(j)
    
# plot 30 day lifecycle
lifecycle = plt.figure(1)
ax1 = lifecycle.add_subplot(111)
ax1.plot(X, y, label='30 Day Lifecycle')
legend = ax1.legend(loc='upper center', shadow=True)

# plot 30 day change
change = plt.figure(2)
ax2 = change.add_subplot(111)
ax2.plot(X, pd.Series(y).pct_change(), 'r', label='% Decrease by Day')
legend = ax2.legend(loc='upper center', shadow=True)
"""