# -*- coding: utf-8 -*-
"""
Created on Fri Jan 27 23:18:14 2017
TensorFlow Linear Classification Model
Uses standard or Deep NN to predict whether the price of a given auction
will be greater than the overall average deal price (0.010524640477314492)
@author: daveu
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os, sys

import pandas as pd
import tensorflow as tf
import tempfile


#Column definitions
COLUMNS = ["deal","deal_type","price","bid_status","esync_flag","num_deals",
           "domain","deal_name"]
#Our "activation" column.  Since this is a classification, it will either be 1 or 0
LABEL_COLUMN = "label"

#Columns without numbers
CATEGORICAL_COLUMNS = ["deal","deal_type","bid_status","esync_flag","domain","deal_name"]
#Columns with numbers
CONTINUOUS_COLUMNS = ["price","num_deals"]

def build_estimator(model_dir,model_type):
    dealname = tf.contrib.layers.sparse_column_with_hash_bucket("deal_name",hash_bucket_size=1000)
    dealtype = tf.contrib.layers.sparse_column_with_keys(column_name="deal_type", keys=["fixed_price","second_price_plus"])
    deal = tf.contrib.layers.sparse_column_with_hash_bucket("deal",hash_bucket_size=100)
    esync = tf.contrib.layers.sparse_column_with_hash_bucket("esync_flag",hash_bucket_size=100)
    status = tf.contrib.layers.sparse_column_with_hash_bucket("bid_status",hash_bucket_size=100)
    domain = tf.contrib.layers.sparse_column_with_hash_bucket("domain",hash_bucket_size=1000)
    
    price = tf.contrib.layers.real_valued_column("price")
    deals = tf.contrib.layers.real_valued_column("num_deals")
    
    #Specify feature inferences
    wide_columns = [
                    deal, dealtype, status, esync, domain, dealname,
                    tf.contrib.layers.crossed_column([dealtype,deal,dealname], hash_bucket_size=int(1e6)),
                    tf.contrib.layers.crossed_column([dealname,domain], hash_bucket_size=int(1e6))]

    deep_columns = [
                    tf.contrib.layers.embedding_column(dealname,dimension=8),
                    tf.contrib.layers.embedding_column(dealtype,dimension=8),
                    tf.contrib.layers.embedding_column(deal,dimension=8),
                    tf.contrib.layers.embedding_column(esync,dimension=8),
                    tf.contrib.layers.embedding_column(status,dimension=8),
                    tf.contrib.layers.embedding_column(domain,dimension=8),
                    price, deals
                    ]
    
    # Set model type.  Note: CombinedClassier is not working at this time
    if model_type == "wide":
        m = tf.contrib.learn.LinearClassifier(model_dir=model_dir,feature_columns=wide_columns)
    elif model_type == "deep":
        m = tf.contrib.learn.DNNClassifier(model_dir=model_dir,feature_columns=deep_columns,hidden_units=[100,50])
    else:
        m = tf.contrib.learn.DNNLinearCombinedClassifier(model_dir=model_dir,linear_feature_columns=wide_columns, dnn_feature_columns=deep_columns, dnn_hidden_units=[100,50])
        
    return m
    
def input_fn(df):
    continuous_cols = {k: tf.constant(df[k].values) for k in CONTINUOUS_COLUMNS}
    categorical_cols = {
                        k: tf.SparseTensor(
                                           indices=[[i,0] for i in range(df[k].size)],
                                           values=df[k].values,
                                           shape=[df[k].size, 1])
                        for k in CATEGORICAL_COLUMNS}
    feature_cols = dict(continuous_cols)
    feature_cols.update(categorical_cols)
    label = tf.constant(df[LABEL_COLUMN].values)
    
    return feature_cols, label
    
def train_and_eval(model_dir, model_type, train_steps):
    data_path = os.path.dirname(os.path.realpath('__file__'))
    
    df_train = pd.read_csv(os.path.join(data_path, "Data/train.csv"), low_memory=False)
    df_test = pd.read_csv(os.path.join(data_path, "Data/test.csv"), low_memory=False)
    
    
    df_train = df_train.dropna(how='any',axis=0)
    df_test = df_test.dropna(how='any',axis=0)
    
    df_train[LABEL_COLUMN] = (df_train["price"].apply(lambda x: 1 if float(x) > 0.010524640477314492 else 0)).astype(int)
    df_test[LABEL_COLUMN] = (df_test["price"].apply(lambda x: 1 if float(x) > 0.010524640477314492 else 0)).astype(int)
    
    model_dir = tempfile.mkdtemp() if not model_dir else model_dir
    print("model directory = %s" % model_dir)
    
    m = build_estimator(model_dir, model_type)
    m.fit(input_fn=lambda: input_fn(df_train), steps=train_steps)
    results = m.evaluate(input_fn=lambda: input_fn(df_test), steps=10)
    for key in sorted(results):
        print("%s: %s" % (key, results[key]))
    
        
def run():
    train_and_eval("D:\\Kraken Tree\\Assets","deep",200)
