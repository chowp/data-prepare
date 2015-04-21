
__author__ = 'niexiaohui pch'
import os
import urllib
import traceback
import sys
import commands
import socket
import MySQLdb
campus_ip = "166.111.9.242"
lab_ip = "219.243.215.205"
ip = ""
# test sever connection
def test_connect():
    global ip
    global campus_ip
    sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sk.settimeout(10)
    try:
        sk.connect(campus_ip,80)
        ip = campus_ip
    except Exception:
        print campus_ip + " can not connect"
        ip = lab_ip
    sk.close()
test_connect()
ip = campus_ip#here change ip
monitorap = ''
DATA_STEP = 100
HOLD_TIME = 100
RAW_DATA_DIR = "/home/pch/delay_data"
TCP_SYN     = 1
TCP_DATA    = 2
TCP_ACK     = 3
TCP_SYN_ACK = 4
TCP_FIN_ACK = 5
TCP_FIN     = 6
TCP_RST     = 7
TCP_OTHER   = 8
#transmit packet info to server
def transmit_delay(cur,conn,table_name):
    try:
        tcp_data_list = range(1,HOLD_TIME)
        start = 0
        end = 0
        wireless_last_match_postion = 0
        print RAW_DATA_DIR
        aps = os.listdir(RAW_DATA_DIR)
        print aps
        for ap in aps:
                print ap
                branch = os.listdir(RAW_DATA_DIR+"/"+ ap)
                for data_type in branch:   		
                    print data_type
                    if data_type != "wire_data":
                        continue
                    dataset = os.listdir(RAW_DATA_DIR+"/"+ap+"/"+data_type)
                    for datafile in dataset: # datafile is particular file
                        print datafile
                        items = datafile.split('-')
                        if len(items) !=3 :
                            continue
                        else:
                            monitorap = items[0]
                        fp = open(RAW_DATA_DIR+"/"+ap+"/"+data_type+"/"+datafile)
                        for line in fp:
                            print line
                            items = line.strip('\n').split(',')
                            tcp_type = int(items[9])
                            srcIP = items[1]
                            dstIP = items[2]
                            srcMac = items[3]
                            dstMac = items[4]
                            seq = items[5]
                            next_seq = items[6]
                            ack = items[7]
                            timestamps = items[0]
                            if tcp_type != TCP_ACK:
                                tcp_data_list[end] = next_seq
                                end = (end+1)%HOLD_TIME
                            else #search the correlation data
                                for i in range(end,start,-1):
                                    if i < 0:
                                        i = i + HOLD_TIME
                                    if tcp_data_list[i] == ack:
                                        final_item=tcp_data_list[i].strip('\n')
                                        final_item = final_item+","+str(timestamps)
                                        seq_index = seq         # come in
                                        if srcMac == monitorap: # COME OUT
                                            seq_index = tcp_data_list[i].split(',')[5]
                                        # start find the wireless delay?
                                        wireless_dir = RAW_DATA_DIR+"/"+ap+"/delay_data"
                                        files = os.listdir(wireless_dir)
                                        files_num = len(files)
                                        quit = 0
                                        for j in range(wireless_last_match_postion,wireless_last_match_postion+files_num):
                                            wireless_file = RAW_DATA_DIR+"/"+ap+"/delay_data"+monitorap+"-1-"+str(j)
                                            for k in open(wireless_file):
                                                kk = k.split(',')
                                                if float(kk[0]) > float(timestamps):
                                                    quit = 1
                                                    break
                                                if seq_index == kk[5]: # successfully find
                                                    wireless_last_match_postion = j
                                                    final_item = final_item + "," + str(kk[0])+"\n"
                                                    print final_item
                                            if quit == 1:
                                                break






    except:
    	traceback.print_exc()                                                                   
    	return 1
    
                                                                                                

if __name__ == "__main__":
    conn=MySQLdb.connect(host='localhost',user='root',passwd='pch',port=3306)
    cur=conn.cursor()
    conn.select_db('wifiunion')
    wireless_n = "ing"
    wire_n = "d_0128_wire" 
    print "Choose server ip is " + ip
    if len(sys.argv)!=2:
        print "input transmit data  type : 1 delay,2 inf 3 wifi "
        sys.exit(0)
    if sys.argv[1] == "1":
        print "#####transmit delay data#####"
        transmit_delay(cur,conn,wireless_n)
    if sys.argv[1] == "2":
        print "#####transmit interference data#####"
    if sys.argv[1] == "3":
        print "#####transmit wifi data#####"
    cur.close()     
    conn.close()

