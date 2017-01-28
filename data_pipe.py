# -*- coding: utf-8 -*-#
"""
Created on Mon Jan  9 21:44:46 2017
Builds deal_index by piping filtered JSON data into a MySQL table
@author: daveu
"""
import mysql.connector
import json
import csv
import re

db = mysql.connector.connect(user='user', password='pass',
                              host='127.0.0.1',
                              database='deals')
cur = db.cursor()

def write():
    total_ios = 0
    ios_yes = 0
    app_yes = 0
    web_yes = 0
    
    # Note: there would not be any no_bids applicable to this because a Deal ID/Name is not present (obviously)
    with open('D:\\Logs\\Nov_23.json') as json_data:
        d = json.load(json_data)
        for i in d:
            if i["bid"]["status"] == "yes_bid":
                deal_id = i["demand"]["demand_data"]["bidder"]["deal_id"]["string"]
                deal_name = i["demand"]["demand_data"]["bidder"]["deal_name"]["string"].replace("'","")
                deal_type = "NA"
                yes_bids = 1
                no_bids = 0
                price = i["bid"]["adv"]
                #Deal ID, Deal Name, Deal Type, Yes Bids, No Bids, Price
                add_row = ("INSERT INTO deal_index (deal_id, deal_name, deal_type, yes_bids, no_bids, price) "
                " VALUES ('"+deal_id+"', '"+deal_name+"','"+deal_type+"','"+str(yes_bids)+"','"+str(no_bids)+"','"+str(price)+"') ON DUPLICATE KEY UPDATE yes_bids = yes_bids + 1")                
                cur.execute(add_row)

    
def bydealname(name=""):
    # deal, deal_type, price, bid_status, esync_flag, num_deals, domain, deal_name, time
    cur.execute("SELECT deal, deal_type, deal_name, domain, esync_flag FROM bid_responses WHERE deal_name='"+name+"' GROUP BY esync_flag")
    #cur.execute("SELECT count(deal) as count,deal FROM deal_history group by deal order by count DESC;")
    for row in cur.fetchall() :  
        print (row)
        
def bydomain(name=""):
    # deal, deal_type, price, bid_status, esync_flag, num_deals, domain, deal_name, time
    cur.execute("SELECT deal, deal_name, esync_flag FROM bid_responses WHERE domain='"+name+"'")
    #cur.execute("SELECT count(deal) as count,deal FROM deal_history group by deal order by count DESC;")
    for row in cur.fetchall() :  
        print (row)
        
def read():
    # deal, deal_type, price, bid_status, esync_flag, num_deals, domain, deal_name, time
    cur.execute("SELECT AVG(price) FROM bid_responses")
    #cur.execute("SELECT count(deal) as count,deal FROM deal_history group by deal order by count DESC;")
    for row in cur.fetchall() :  
        print (row) 

def grab():
    #deal, deal_name, deal_type, bidder_id, seat_id
    cur.execute('SELECT deal, bidder_id, seat_id FROM deal_data WHERE deal="K-P-4ee25bd7"');
    for row in cur.fetchall() :  
        print (row)         
        
def deal_batch():
    #'K-P-3605ed52','K-P-dfd85cdf'
    cur.execute("SELECT count(*) as count, deal, deal_type, deal_name, num_deals FROM bid_responses GROUP BY deal_name;")
    for row in cur.fetchall() :
        print(row[0],row[2],row[4],re.split('\W+|_',row[3])[0])
        
def delete():
    cur.execute("TRUNCATE deal_data;")
    
def csv_requests_to_db():
    deals = []
    names = []
    types = []
    
    # make sure lock out isn't exceeded
    cur.execute("set innodb_lock_wait_timeout=500")
    db.commit()
    
    with open('D:\\Kraken Tree\\request_batch_2.csv', 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            for deal in eval(row['DEALS']):
                deals.append(deal)
            for name in eval(row['NAMES']):
                names.append(name.replace("'",""))
            for deal_type in eval(row['TYPES']):
                types.append(deal_type)
    
    for i in range (0,len(deals)):
        add_row = ("INSERT REPLACE deal_data (deal, deal_name, deal_type) "
                   "VALUES ('"+deals[i]+"','"+names[i]+"','"+types[i]+"')")
        cur.execute(add_row)
        
    db.commit()
    
def csv_to_db():
    with open('D:\\Kraken Tree\\bid_responses_2.csv', 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            dealname = row['DEALNAME'].replace("'","")
            #print(row['DEALID'],row['PRICE'],row['IMPRESSIONID'],row['KARGOID'],row['PLATFORM'],row['TIME'])
            add_row = ("INSERT INTO bid_responses (deal, deal_type, price, bid_status, esync_flag, num_deals, domain, deal_name, time)"
            " VALUES ('"+row['DEAL_ID']+"', '"+row['DEALTYPE']+"','"+row['PRICE']+"','"+row['BID_STATUS']+"','"+row['ESYNCFLAG']+"','"+row['NUMDEALS']+"','"+row['DOMAIN']+"','"+dealname+"','"+row['TIME']+"')")
            cur.execute(add_row)
            
    db.commit()
    
def mine_deal():
    with open('D:\\Kraken Tree\\bid_responses_2.csv', 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            dealname = row['DEALNAME'].replace("'","")
            add_row = ("INSERT INTO deal_data (deal, deal_name, deal_type, bidder_id, seat_id)"
            " VALUES ('"+row['DEAL_ID']+"', '"+dealname+"', '"+row['DEALTYPE']+"', '"+row['BIDDERID']+"', '"+row['SEATID']+"')")
            cur.execute(add_row)            
    db.commit()
    
def db_to_prediction():
    deal_id = 'K-P-dfd85cdf'
    # Init CSV
    f = open('D:\\Kraken Tree\\'+deal_id+'_values.csv','w', newline='')
    writer = csv.writer(f)
    writer.writerow(["time","price","deals"])
    i = 0
    
    # DB -> CSV
    cur.execute("SELECT time,price,num_deals FROM bid_responses WHERE deal='"+deal_id+"';")
    for row in cur.fetchall() :
        i+=1
        writer.writerow([row[0],row[1],row[2]])
        
    print(i, "rows written")
    f.close()
    
def dump_to_csv(rows = 50000):
    f = open('D:\\Kraken Tree\\test.csv','w', newline='')
    writer = csv.writer(f)
    writer.writerow(["deal","deal_type","price","bid_status","esync_flag","num_deals","domain","deal_name","time"])
    i = 0
    
    # DB -> CSV
    cur.execute("SELECT deal,deal_type,price,bid_status,esync_flag,num_deals,domain,deal_name,time FROM bid_responses LIMIT 50001,75000;")
    for row in cur.fetchall() :
        i+=1
        writer.writerow([row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8]])
        
    print(i, "rows written")
    f.close()    

def db_to_histogram():
    f = open('D:\\Kraken Tree\\esync_flag.csv','w', newline='')
    writer = csv.writer(f)
    writer.writerow(["Flag","Price","Count"])
    i = 0
    
    cur.execute("SELECT esync_flag, AVG(price), count(*) as Count FROM bid_responses GROUP BY esync_flag")
    for row in cur.fetchall() :  
        i+=1
        writer.writerow([row[0],row[1],row[2]]) 
        
    print(i, "rows written")
    f.close()