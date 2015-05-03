
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
frequent_path = "."
frequent_path_wire = "."
throughput_path = "/tmp/bismark-uploads/passive-throughput"
frequent_url = "http://" + ip + "/netgear/frequence.php?monitorap={0}&data={1}"
throughput_url = "http://" + ip + "/netgear/throughput.php?monitorap={0}&data={1}"
packet_url = "http://" + ip + "/netgear/packet.php?monitorap={0}&data={1}"
packet_url_wire = "http://" + ip + "/netgear/packet_wire.php?monitorap={0}&data={1}"
mac_url = "http://" + ip + "/netgear/macip.php?mac={0}&ip={1}"
monitorap = ''
DATA_STEP = 100
RAW_DATA_DIR = "/home/pch/delay_data"
# transmit mac and ip address to server
def transmit_mac_ip_address():
    (status, output) = commands.getstatusoutput("ifconfig wlan0 | grep HWaddr | awk '{print $5}'|sed 's/://g'")
    mac = output
    (status, output) = commands.getstatusoutput("ifconfig eth1 | grep 'inet addr:' | awk '{print $2}'|sed 's/'addr:'//g'")
    ip = output
    print "mac: "+ mac + "  ip: " + ip  
    page = urllib.urlopen(mac_url.format(mac , ip))
#transmit packet info to server
def transmit_packet(cur,conn,table_name):
    try:
        print RAW_DATA_DIR
        aps = os.listdir(RAW_DATA_DIR)
        print aps
        for ap in aps:
                print ap
                branch = os.listdir(RAW_DATA_DIR+"/"+ ap)
                for data_type in branch:        
                    print data_type
                    if data_type != "inf_data":
                        continue
                    dataset = os.listdir(RAW_DATA_DIR+"/"+ap+"/"+data_type)
                    #dataset.sort(key= lambda x:int(x[24:]))
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
                            #print line
                            items = line.strip('\n').split(',')
                            if len(items) != 6:#here 1
                                continue
                            else:
                                sql_insert = "insert into %s (btime,etime,monitor_ap,smac,dmac,inf,type) values('%s','%s','%s','%s','%s','%s','%s')" \
                                %(table_name,items[1],items[2],monitorap,items[3],items[4],items[5],items[0],)
                                print sql_insert
                                count_insert = cur.execute(sql_insert)

                        conn.commit()
                        fp.close()
                        #os.remove(frequent_path + "/" + file)
                    
    except:
    	traceback.print_exc()                                                                   
    	return 1
    


if __name__ == "__main__":
    conn=MySQLdb.connect(host='localhost',user='root',passwd='pch',port=3306)
    cur=conn.cursor()
    conn.select_db('wifiunion')
    wireless_n = "ing"
    if len(sys.argv)!=2:
        print "input transmit data  type : 1 packet,2 throughput 3 mac"
        sys.exit(0)
#    print "#####transmit frequence data#####"
#    transmit_frequence()
    
    if sys.argv[1] == "1":
        print "#####transmit packet data#####"
        transmit_packet(cur,conn,wireless_n)
    
    cur.close()     
    conn.close()

