
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
        tcp_data_list = range(0,HOLD_TIME)
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
                    dataset.sort(key= lambda x:int(x[15:]))
                    for datafile in dataset: # datafile is particular file
                        print datafile
                        items = datafile.split('-')
                        if len(items) !=3 :
                            continue
                        else:
                            monitorap = items[0]
                        fp = open(RAW_DATA_DIR+"/"+ap+"/"+data_type+"/"+datafile)
                        for line in fp: #every line of the wired data file
                            items = line.strip('\n').split(',')
                            if len(items) != 10:
                                continue
                            tcp_type = -1 
                            if items[9] !='':
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
                            else:#search the correlation data
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
                                        files.sort(key= lambda x:int(x[15:]))
                                        if wireless_last_match_postion == 0:
                                            wireless_last_match_postion = int(files[0][15:])
                                                                                                
                                        quit = 0
                                        last_file_no = int(files[-1][15:])
                                        print "from %d to %d\n"%(wireless_last_match_postion,last_file_no)
                                        for j in range(wireless_last_match_postion, last_file_no + 1   ):
                                            wireless_file = RAW_DATA_DIR+"/"+ap+"/delay_data/"+monitorap+"-1-"+str(j)
                                            short_name = monitorap+"-1-"+str(j)
                                            if short_name not in files:
                                                print "%s is missing"%(short_name)
                                                wireless_last_match_postion = j + 1
                                                continue
                                            wireless_f = open(wireless_file)
                                            if len(wireless_f.read()) == 0 :
                                                print "file is empty"
                                                wireless_last_match_postion = j+1
                                                continue
                                            print wireless_f
                                            for k in open(wireless_file):
                                                kk = k.strip('\n').split(',')
                                                if len(kk) != 3:
                                                    print "%s format error!"%(k)
                                                    continue
                                                print "two kind of time is :%s,%s"%(str(kk[0]),str(timestamps))
                                                if float(kk[0]) > float(timestamps) + 5: # 10 seconds window
                                                    print "F wired    line is %s"%(line)
                                                    print "F wireless line is %s\n"%(k)
                                                    wireless_last_match_postion = j
                                                    quit = 1
                                                    break
                                                if float(kk[0]) < float(timestamps) - 5:
                                                    print "B wired    line is %s"%(line)
                                                    print "B wireless line is %s\n"%(k)
                                                    wireless_last_match_postion = j+1
                                                    
                                                if seq_index == kk[2]: # successfully find
                                                    wireless_last_match_postion = j # this may be cause some missing, because some wireless packet is early than wired part
                                                    final_item = final_item + "," + str(kk[0])+"\n"
                                                    print "$$$$find$$$ %s"%(final_item)
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

