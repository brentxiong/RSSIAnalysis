import MySQLdb
from collections import Counter
from Tkinter import *
import time
import datetime

import ConfigParser
import os
import re

import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt

mac = []
mac_bad = []
goodsn=open('goodsn','r')
for line in goodsn:
    m = re.match(r'\d{10}',line.strip())
    #print line
    if m :
        mac.append(m.group(0))
goodsn.close()

badsn = open('badsn','r')
for line in badsn:
    m = re.match(r'\d{10}',line.strip())
    #print line
    if m :
        mac_bad.append(m.group(0))
badsn.close()

print mac,mac_bad

class Analyzer():
    def __init__(self):
        self.db = None
        self.getdbconfig()
        self.connectdb()
    def connectdb(self):
        self.db = MySQLdb.connect(host= self.dbhost,user=self.user,passwd=self.passwd,db=self.db)
        self.cursor = self.db.cursor()
    def getdbconfig(self):
        conf = ConfigParser.ConfigParser()
        conf.read('db.conf')
        self.dbhost = conf.get('database','dbhost')
        
        self.user = conf.get('database','user')
        self.passwd = conf.get('database','passwd')
        self.db = conf.get('database','db')
        
    def closedb(self):
        self.db.close()
        
    def get_rx_result(self, macaddr='2021282952'):
        sql = "select rssi_2, rssi_3, rssi_4, rssi_1, evm_1 from dat_Assy_dp_dut where job_id = (select max(job_id) from mfgtest.JobIdTbl where sn_product = '{}' and station like 'Assy%')".format(macaddr)
        try:
            #get all data
            self.cursor.execute(sql)
            results = ()
            results = self.cursor.fetchall()

            # construct the data
            RE = {}
            RE['Chain 1'] = {'RSSI':[ results[i][0]for i in range(6)], \
                             'EVM': [results[i][4]for i in range(6)]}
            RE['Chain 2'] = {'RSSI':[ results[i][1]for i in range(6,12)], \
                             'EVM': [results[i][4]for i in range(6,12)]}
            RE['Chain 3'] = {'RSSI':[ results[i][2]for i in range(12,18)], \
                             'EVM': [results[i][4]for i in range(12,18)]}
            RE['Chain 4'] = {'RSSI':[ results[i][3]for i in range(18,24)], \
                             'EVM': [results[i][4]for i in range(18,24)]}
            #print macaddr, RE
            return RE
        
        except:
            print "Error: unable to fetch data"    
    def get_tx_result(self, macaddr='2021282952', row=0):
        sql = "select rssi_1, rssi_2, evm_1 from dat_Assy_dp_gold where job_id = (select max(job_id) from mfgtest.JobIdTbl where sn_product = '{}' and station like 'Assy%')".format(macaddr)
        try:
            #get all data
            self.cursor.execute(sql)
            results = ()
            results = self.cursor.fetchall()
            # construct the data
            RE = {}
            RE['Chain 1'] = {'RSSI':[ results[i][0]for i in range(6)], \
                             'EVM': [results[i][2]for i in range(6)]}
            RE['Chain 2'] = {'RSSI':[ results[i][1]for i in range(6,12)], \
                             'EVM': [results[i][2]for i in range(6,12)]}
            RE['Chain 3'] = {'RSSI':[ results[i][0]for i in range(12,18)], \
                             'EVM': [results[i][2]for i in range(12,18)]}
            RE['Chain 4'] = {'RSSI':[ results[i][1]for i in range(18,24)], \
                             'EVM': [results[i][2]for i in range(18,24)]}
            return RE
        except:
            print "Error: unable to fetch data"

if __name__ == '__main__':
    # index = 0 will get 0, 90 degree data
    # index = 2 will get 180, 270 degree data
    index = 0
    result_good = {}
    result_bad = {}
    for i in range(2):
        result_good['RX CHAIN {}'.format(index + i + 1)] = {'RSSI':[],'EVM':[]}
        result_good['TX CHAIN {}'.format(index + i + 1)] = {'RSSI':[],'EVM':[]}
        
        result_bad['RX CHAIN {}'.format(index + i + 1)] = {'RSSI':[],'EVM':[]}
        result_bad['TX CHAIN {}'.format(index + i + 1)] = {'RSSI':[],'EVM':[]}
    
    print result_good
   
    analyzer = Analyzer()
    
    #'''
    for m in mac:
        #rssi, evm = analyzer.get_rx_result(macaddr=m, row=6)
        rxre = analyzer.get_rx_result(macaddr=m)
        txre = analyzer.get_tx_result(macaddr=m)
        for i in range(2):
            #print rssi, evm
            result_good['RX CHAIN {}'.format(index + i + 1)]['RSSI'] = result_good['RX CHAIN {}'.format(index + i + 1)]['RSSI'] + (rxre['Chain {}'.format(index + i + 1)]['RSSI'])
            result_good['RX CHAIN {}'.format(index + i + 1)]['EVM'] = result_good['RX CHAIN {}'.format(index + i + 1)]['EVM'] + (rxre['Chain {}'.format(index + i+ 1)]['EVM'])

            result_good['TX CHAIN {}'.format(index + i + 1)]['RSSI'] = result_good['TX CHAIN {}'.format(index + i + 1)]['RSSI'] + (txre['Chain {}'.format(index + i + 1)]['RSSI'])
            result_good['TX CHAIN {}'.format(index + i + 1)]['EVM'] = result_good['TX CHAIN {}'.format(index + i + 1)]['EVM'] + (txre['Chain {}'.format(index + i+ 1)]['EVM'])
    for m in mac_bad:
        #rssi, evm = analyzer.get_rx_result(macaddr=m, row=6)
        rxre = analyzer.get_rx_result(macaddr=m)
        txre = analyzer.get_tx_result(macaddr=m)
        for i in range(2):
            #print rssi, evm
            result_bad['RX CHAIN {}'.format(index + i + 1)]['RSSI'] = result_bad['RX CHAIN {}'.format(index + i + 1)]['RSSI'] + (rxre['Chain {}'.format(index + i + 1)]['RSSI'])
            result_bad['RX CHAIN {}'.format(index + i + 1)]['EVM'] = result_bad['RX CHAIN {}'.format(index + i + 1)]['EVM'] + (rxre['Chain {}'.format(index + i+ 1)]['EVM'])

            result_bad['TX CHAIN {}'.format(index + i + 1)]['RSSI'] = result_bad['TX CHAIN {}'.format(index + i + 1)]['RSSI'] + (txre['Chain {}'.format(index + i + 1)]['RSSI'])
            result_bad['TX CHAIN {}'.format(index + i + 1)]['EVM'] = result_bad['TX CHAIN {}'.format(index + i + 1)]['EVM'] + (txre['Chain {}'.format(index + i+ 1)]['EVM'])

            
    analyzer.closedb()
    #print result_good['RX CHAIN {}'.format(index + 1)]['RSSI']#, result_good['RX CHAIN {}'.format(index + 1)]['EVM']
    #print result_bad['RX CHAIN {}'.format(index + 1)]['RSSI']#, result_bad['RX CHAIN {}'.format(index + 1)]['EVM']
    
    # Define limits
    AXIS_X_MIN = -85
    AXIS_X_MAX = -30
    AXIS_Y_MIN = -40
    AXIS_Y_MAX = -10

    AXIS_TX_X_MIN = -55
    AXIS_TX_X_MAX = -25
    AXIS_TX_Y_MIN = -40
    AXIS_TX_Y_MAX = -10
    
    fig = plt.figure(figsize=(12, 6))
    
    c_1_rx = fig.add_subplot(221)
    c_1_rx.set_xlabel('Measured RSSI')
    c_1_rx.set_ylabel('Measured EVM')
    c_1_rx.set_title('RX_{} Degree - All Channels'.format(index*90))
    # Define axis
    c_1_rx.axis([AXIS_X_MIN, AXIS_X_MAX, AXIS_Y_MIN, AXIS_Y_MAX])
    

    # For High power around -40dBm
    c_1_rx.vlines(-76,-40,-10,color='b')
    c_1_rx.vlines(-66,-40,-10,color='b')
    c_1_rx.hlines(-12,-85, -30, color='b')
        
    # For Low power around -70dBm 
    c_1_rx.vlines(-46,-40,-10,color='r')
    c_1_rx.vlines(-36,-40,-10,color='r')
    c_1_rx.hlines(-22,-85, -30, color='r')
    
    c_2_rx = fig.add_subplot(222)
    c_2_rx.axis([AXIS_X_MIN, AXIS_X_MAX, AXIS_Y_MIN, AXIS_Y_MAX])
    c_2_rx.set_xlabel('Measured RSSI')
    c_2_rx.set_ylabel('Measured EVM')
    c_2_rx.set_title('RX_{} Degree - All Channels'.format((index + 1)*90))
    c_2_rx.vlines(-76,-40,-10,color='b')
    c_2_rx.vlines(-66,-40,-10,color='b')
    c_2_rx.hlines(-12,-85, -30, color='b')
    # For Low power around -70dBm 
    c_2_rx.vlines(-46,-40,-10,color='r')
    c_2_rx.vlines(-36,-40,-10,color='r')
    c_2_rx.hlines(-22,-85, -30, color='r')
    
    # TX
    c_1_tx = fig.add_subplot(223)
    c_1_tx.axis([AXIS_TX_X_MIN, AXIS_TX_X_MAX, AXIS_TX_Y_MIN, AXIS_TX_Y_MAX])
    c_1_tx.set_xlabel('Measured RSSI')
    c_1_tx.set_ylabel('Measured EVM')
    c_1_tx.set_title('TX_{} Degree - All Channels'.format(index*90))
    c_1_tx.vlines(-44,-40,-10,color='r')
    c_1_tx.vlines(-34,-40,-10,color='r')
    c_1_tx.hlines(-12,-55, -25, color='r')
    
    
    c_2_tx = fig.add_subplot(224)
    c_2_tx.axis([AXIS_TX_X_MIN, AXIS_TX_X_MAX, AXIS_TX_Y_MIN, AXIS_TX_Y_MAX])
    c_2_tx.set_xlabel('Measured RSSI')
    c_2_tx.set_ylabel('Measured EVM')
    c_2_tx.set_title('TX_{} Degree - All Channels'.format((index + 1)*90))
    c_2_tx.vlines(-44,-40,-10,color='r')
    c_2_tx.vlines(-34,-40,-10,color='r')
    c_2_tx.hlines(-12,-55, -25, color='r')
    
    # Plot Data
    c_1_rx.plot(result_good['RX CHAIN {}'.format(index + 1)]['RSSI'], result_good['RX CHAIN {}'.format(index + 1)]['EVM'], 'r1', color='g', label='Good')
    c_1_rx.plot(result_bad['RX CHAIN {}'.format(index + 1)]['RSSI'], result_bad['RX CHAIN {}'.format(index + 1)]['EVM'], 'r2', color='r', label='Bad')
    c_1_rx.legend(('Good','Bad'),loc='upper right', fancybox=True, shadow=True)
    
    c_2_rx.plot(result_good['RX CHAIN {}'.format(index + 2)]['RSSI'], result_good['RX CHAIN {}'.format(index + 2)]['EVM'], 'r1', color='g')
    c_2_rx.plot(result_bad['RX CHAIN {}'.format(index + 2)]['RSSI'], result_bad['RX CHAIN {}'.format(index + 2)]['EVM'], 'r2', color='r')
    c_2_rx.legend(('Good','Bad'),loc='upper right', fancybox=True, shadow=True)

    c_1_tx.plot(result_good['TX CHAIN {}'.format(index + 1)]['RSSI'], result_good['TX CHAIN {}'.format(index + 1)]['EVM'], 'r1', color='g', label='Good')
    c_1_tx.plot(result_bad['TX CHAIN {}'.format(index + 1)]['RSSI'], result_bad['TX CHAIN {}'.format(index + 1)]['EVM'], 'r2', color='r', label='Bad')
    c_1_tx.legend(('Good','Bad'),loc='upper right', fancybox=True, shadow=True)
    
    c_2_tx.plot(result_good['TX CHAIN {}'.format(index + 2)]['RSSI'], result_good['TX CHAIN {}'.format(index + 2)]['EVM'], 'r1', color='g')
    c_2_tx.plot(result_bad['TX CHAIN {}'.format(index + 2)]['RSSI'], result_bad['TX CHAIN {}'.format(index + 2)]['EVM'], 'r2', color='r')
    c_2_tx.legend(('Good','Bad'),loc='upper right', fancybox=True, shadow=True)
    
    fig.suptitle("A5-18 SLT_L30")
    plt.tight_layout()
    plt.show()


    #'''
    #analyzer.closedb()
