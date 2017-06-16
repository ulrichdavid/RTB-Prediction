#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 16 17:17:52 2017

@author: dulrich@kargo.com

Performs analysis on tracker data from articles

"""
import pandas as pd
import matplotlib.pyplot as plt

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

    
df = pd.read_csv("american-detained-nk.csv", index_col=None)

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