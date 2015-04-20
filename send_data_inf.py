
__author__ = 'niexiaohui'
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
RAW_DATA_DIR = $HOME/delay_data
#transmit packet info to server
def transmit_packet(cur,conn,table_name):
    try:
        aps = os.listdir(RAW_DATA_DIR)
        print " packet file num: " +str(len(aps))
        count = 0
        for ap in aps:
		
            count +=1
            print "deal with  AP:" + str(file) 
            items = file.split('-') 
            if len(items) != 3:   
                continue 
            else:
                monitorap = items[0]
            fp = open(frequent_path + "/" + file)
            #lines = fp.readlines() 
            #if len(lines) == 0 :
            #	print "the file is empty,waiting for rsync!!"
           # 	continue
            #fp.close()
            #os.remove(frequent_path + "/" + file)
            step = DATA_STEP
            data = ""
            for line in fp:
                #print line
                items = line.strip('\n').split(',')
                if len(items) != 6:#here 1
                    continue
                else:
                    sql_insert = "insert into %s (btime,etime,monitor_ap,smac,dmac,inf,type) order by btime values('%s','%s','%s','%s','%s','%s','%s')" \
                    %(table_name,items[1],items[2],monitorap,items[3],items[4],items[5],items[0],)
                    print sql_insert
                    count_insert = cur.execute(sql_insert)
        #data += ','.join(items)+'|'
                    #step -= 1
                    #if step == 0:
                    #   page = urllib.urlopen(packet_url.format(monitorap, data[:-1]))
                    #   # print packet_url.format(monitorap, data[:-1])  
                    #    data = ""
                    #    step = DATA_STEP
            conn.commit()
            fp.close()
            os.remove(frequent_path + "/" + file)
            if data != "":
                page = urllib.urlopen(packet_url.format(monitorap, data[:-1]))
               # print packet_url.format(monitorap, data[:-1])
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
        print "input transmit data  type : 1 packet,2 throughput 3 mac"
        sys.exit(0)
#    print "#####transmit frequence data#####"
#    transmit_frequence()
    if sys.argv[1] == "2":
        print "#####transmit throughput data#####"
        transmit_throughput(cur)
    if sys.argv[1] == "1":
        print "#####transmit packet data#####"
        transmit_packet(cur,conn,wireless_n)
    if sys.argv[1] == "3":
        print "#####transmit packet data#####"
        transmit_mac_ip_address(cur)
    if sys.argv[1] == "4":
        print "#####transmit packet data#####"
        transmit_packet_wire(cur,conn,wire_n)
    cur.close()     
    conn.close()

