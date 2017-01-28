# -*- coding: utf-8 -*-
"""
Created on Sat Jan 14 17:11:41 2017

@author: daveu
"""

import mysql.connector
import json
import csv
from collections import defaultdict

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import pandas as pd

from sklearn.svm import SVR
from sklearn import preprocessing
from sklearn.preprocessing import LabelEncoder

from sklearn import metrics
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.linear_model import LinearRegression


#Configure the size of graph
from pylab import rcParams
rcParams['figure.figsize'] = 12.5, 5

db = mysql.connector.connect(user='user', password='pass',
                              host='127.0.0.1',
                              database='deals')
cur = db.cursor()

with open('D:\\Kraken Tree\\K-P-dfd85cdf_values.csv', 'r') as f1:
    td = pd.read_csv(f1)
    

def barchart():
    fig = plt.figure()
    
    width = .35
    ind = np.arange(len(data['Count']))
    plt.bar(ind, data['Count'], width=width)
    plt.xticks(ind + width / 2, data['Seat'])
    
def cmap():
    jet=plt.get_cmap('coolwarm')
    
    x = data['Count']
    y = data['Price']

    plt.scatter(y[0], x[0], s=x[0]/1000, c=1, cmap=jet, vmin=0, vmax=4, label="Not Synced")
    plt.scatter(y[1], x[1], s=x[1]/1000, c=2, cmap=jet, vmin=0, vmax=4, label="No UUID")
    #plt.scatter(y[2], x[2], s=x[2]/1000, c=3, cmap=jet, vmin=0, vmax=4, label="Synced")

    sm = plt.cm.ScalarMappable(cmap=jet, norm=plt.Normalize(vmin=0, vmax=0.02))
    plt.clim(0.0,0.02)
    plt.colorbar()
    plt.show()    
    
def decision_tree(train = ["K-P-3605ed52",
  "K-IND-d239ba29",
  "K-P-d6091348",
  "K-P-3a98c113",
  "K-IND-b7df83cd",
  "K-IND-db227d0f",
  "K-P-c7fe04bc",
  "K-IND-cba56af7",
  "K-IND-2fda5b7b",
  "K-P-dfd85cdf",
  "K-P-207d1edc",
  "K-IND-7183350f",
  "K-IND-1fca8f18",
  "K-IND-507757d8"], actual = "K-P-dfd85cdf"):
  
    train_data = train or []
    deal_data = defaultdict(list)
    winner_price = 0
    winner = ""
    
    # Populate train data
    for deal in train_data:
        cur.execute("SELECT deal,deal_type, price FROM deal_history WHERE deal = '"+deal+"' order by price DESC LIMIT 1;")
        for row in cur.fetchall() :
            if winner == "":
                winner = deal
                winner_type = row[1]
                winner_price = row[2]
            if row[1] == "second_price_plus":
                if row[2] > winner_price or winner_type == "fixed_price":
                    winner_price = row[2]
                    winner = deal
                    winner_type = row[1]
            #print(deal,row[1],row[2])
            #deal_data[row[0]].append(row[1])
            #deal_data[row[0]].append(row[2])
    for deal in train_data:
        cur.execute("SELECT count(deal) as count, deal FROM deal_history WHERE deal = '"+deal+"' group by deal order by count DESC;")
        for row in cur.fetchall():
            print(row)
    print ("Predicted ", winner, winner_price, winner_type, "Actual: ", actual)
    # Find highest priced second_price_plus
    for deal in deal_data:
        print(deal)
    
def SVM():
    X = td.iloc[:500,(1)].reshape(-1,1)
    y = td.iloc[:500,(0)]
    
    #X_test = np.sort(5 * np.random.rand(40, 1), axis=0)
    #Y_test = np.sin(X_test).ravel()
    
    #svr_rbf = SVR(kernel='rbf', C=1e3, gamma=0.1)
    svr_lin = SVR(kernel='linear', C=1e3)
    #svr_poly = SVR(kernel='poly', C=1e3, degree=2)
    #y_rbf = svr_rbf.fit(X, y).predict(X)
    y_lin = svr_lin.fit(X, y).predict(X)
    #y_poly = svr_poly.fit(X, y).predict(X)
    
    lw = 2
    plt.scatter(y, X, color='darkorange', label='data')
    plt.hold('on')
    #plt.plot(X, y_rbf, color='navy', lw=lw, label='RBF model')
    plt.plot(X, y_lin, color='c', lw=lw, label='Linear model')
    #plt.plot(X, y_poly, color='cornflowerblue', lw=lw, label='Polynomial model')
    plt.xlabel('data')
    plt.ylabel('target')
    plt.title('Support Vector Regression')
    plt.legend()
    plt.show()