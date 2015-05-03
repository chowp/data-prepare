
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
debug_time = "1429806462.450838"
#transmit packet info to server
def transmit_delay(cur,conn,table_name):
    try:
        tcp_data_list = range(0,HOLD_TIME)
        tcp_next_seq_list = range(0,HOLD_TIME)
        start = 0
        end = 0
        wireless_last_match_postion = 0
        print RAW_DATA_DIR
        aps = os.listdir(RAW_DATA_DIR)
        print aps
        for ap in aps:
                print ap
                branch = os.listdir(RAW_DATA_DIR+"/"+ ap)
                if ap != "4494FC74F534":
                    continue
                for data_type in branch:   		
                    print data_type
                    if data_type != "wire_data":
                        continue
                    dataset = os.listdir(RAW_DATA_DIR+"/"+ap+"/"+data_type)
                    dataset.sort(key= lambda x:int(x[24:]))
                    for datafile in dataset: # datafile is particular file
                        items = datafile.split('-')
                        if len(items) !=3 :
                            continue
                        else:
                            monitorap = items[0]
                            if monitorap == "008EF25FC610":
                                monitorap = "008ef25fc611"
                            elif monitorap == "04A151A80133":
                                monitorap = "04a151a80134"
                            elif monitorap == "4494fc74f534":
                                monitorap = "4494fc74f535"
                            else:
                                a = 1
                                #do noing
                        fp = open(RAW_DATA_DIR+"/"+ap+"/"+data_type+"/"+datafile)
                        for line in fp: #every line of the wired data file
                            items = line.strip('\n').split(',')
                            if len(items) != 11: # caution here
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
                            hdrlen = 0
                            if items[10] != '':
                                hdrlen = int(items[10])
                            if tcp_type != TCP_ACK:
                                tcp_next_seq_list[end] = next_seq
                                tcp_data_list[end] = line
                                end = (end+1)%HOLD_TIME
                            else:#ack
                                no = (end - start + HOLD_TIME)%HOLD_TIME
                                index = end
                                i = 0
                                if timestamps == debug_time:
                                    print line
                                while (i < no):
                                    if timestamps == debug_time:
                                        print "index=%d,nex_seq=%s,ack=%s\n"%(index,tcp_next_seq_list[index],ack)
                                    if tcp_next_seq_list[index] == ack:
                                        check = tcp_data_list[index].split(',')
                                        if timestamps == debug_time:
                                            print "come in "
                                        seq_index = seq         # RTT + downstream
                                        ack_index = ack
                                        hdrlen_index = hdrlen
                                        go_dir = 1
                                        time1 = check[0]
                                        time2 = timestamps
                                        time3 = ''
                                        if srcMac.lower() == monitorap.lower(): # downstream + upstream
                                            go_dir = 2
                                            seq_index = check[5]
                                            ack_index = check[7]
                                            hdrlen_index = int(check[10])
                                            time2 =''
                                            time3 =timestamps
                                        # last check ip address and mac address
                                        if srcIP != check[2] or dstIP != check[1] :#or srcMac != check[4] or dstMac != check[3]:
                                            i = i + 1
                                            index = (index -1 + HOLD_TIME)%HOLD_TIME
                                            if timestamps == debug_time:
                                                print check
                                                print "so this check fails!!"
                                            continue
                                        
                                        #out = str(time1) + "," + str(time2) + "," \
                                        #   + str(time3) "," + str(check[1]) + ","\
                                        #    + str(check[2]) + "," + str(check[3]) + ","\
                                        #   + str(check[4]) + "," + str(seq_index) + ","\
                                        #    + str(check[8]) + "," + str(go_dir) + "\n"
                                        #print out 
                                        sql_insert = "insert ignore into %s (time1,time2,time3,srcIP,dstIP,srcMac,dstMac,seq,ack,len,tcplen,direction) values('%s','%s','%s','%s','%s','%s','%s','%d','%d','%d','%d','%d')" \
                                        %(table_name,time1,time2,time3,check[1],check[2],check[3],check[4],int(seq_index),int(ack_index),int(check[8]),int(hdrlen_index),int(go_dir))
                                        if timestamps == debug_time:
                                            print sql_insert
                                            print tcp_data_list[index]
                                            print line
                                        count_insert = cur.execute(sql_insert)
                                        
                                        start = index
                                        break
                                    i = i + 1
                                    index = (index -1 + HOLD_TIME)%HOLD_TIME
                        conn.commit()


    except:
        traceback.print_exc()                                                                   
        return 1

def transmit_wireless_delay(cur,conn,table_name):
    try:
        print RAW_DATA_DIR
        wireless_all = 0.00001
        find_match_in_wire = 0
        find_only_match_in_wire = 0
        aps = os.listdir(RAW_DATA_DIR)
        print aps
        for ap in aps:
                print ap
                if ap != "4494FC74F534":
                    continue
                branch = os.listdir(RAW_DATA_DIR+"/"+ ap)
                for data_type in branch:        
                    print data_type
                    if data_type != "delay_data":
                        continue
                    dataset = os.listdir(RAW_DATA_DIR+"/"+ap+"/"+data_type)
                    dataset.sort(key= lambda x:int(x[24:]))
                    for datafile in dataset: # datafile is particular file
                        print "match ratio is %f,%f"%(float(find_match_in_wire)/float(wireless_all),float(find_only_match_in_wire)/float(wireless_all) )
                        conn.commit()
                        items = datafile.split('-')
                        if len(items) !=3 :
                            continue
                        else:
                            monitorap = items[0]
                        fp = open(RAW_DATA_DIR+"/"+ap+"/"+data_type+"/"+datafile)
                        for line in fp: #every line of the wired data file
                            wireless_all = wireless_all + 1
                            items = line.strip('\n').split(',')
                            if len(items) != 5:
                                continue
                            if int(items[2]) != 0:
                                sql_find = "select * from %s where seq ='%s' and ack='%s'"%(table_name,items[2],items[3])
                                count_find = cur.execute(sql_find)
                                results = cur.fetchall()
                                if count_find > 0 :
                                    find_match_in_wire =find_match_in_wire + 1
                                #    print count_find
                                #    print sql_find
                                #    print results
                                if count_find == 1: # cation this may be changed
                                    find_only_match_in_wire = find_only_match_in_wire + 1
                                    if int(results[0][11]) == 1: # RTT and downsteam
                                        sql_update = "update %s set time3=%s,len=%d where seq='%s'"%(table_name,items[1],int(items[4]),items[2])
                                        #print sql_update
                                        count_update = cur.execute(sql_update)
                                    elif int(results[0][11]) == 2: # downstream and upstream
                                        sql_update = "update %s set time2=%s,len=%d where seq='%s'"%(table_name,items[1],int(items[4]),items[2])
                                        #print sql_update
                                        count_update = cur.execute(sql_update) 
    except:
        traceback.print_exc()                                                                   
        return 1
                                                                                                

if __name__ == "__main__":
    conn=MySQLdb.connect(host='localhost',user='root',passwd='pch',port=3306)
    cur=conn.cursor()
    conn.select_db('wifiunion')
    wireless_n = "delay"
    print "Choose server ip is " + ip
    if len(sys.argv)!=2:
        print "input transmit data  type : 1 delay,2 inf 3 wifi "
        sys.exit(0)
    if sys.argv[1] == "1":
        print "#####transmit delay data#####"
        transmit_delay(cur,conn,wireless_n)
    if sys.argv[1] == "2":
        print "##### match the wireless part #####"
        transmit_wireless_delay(cur,conn,wireless_n)
    if sys.argv[1] == "3":
        print "#####transmit wifi data#####"
    cur.close()     
    conn.close()

