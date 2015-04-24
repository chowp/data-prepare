
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
        frequent = os.listdir(frequent_path)
        print " packet file num: " +str(len(frequent))
        count = 0
        for file in frequent:
            count +=1
            print "deal with  file num" + str(file) 
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
    
                                                                                                
def transmit_packet_wire(cur,conn,table_name):
    try:
        frequent = os.listdir(frequent_path_wire)
        print " packet file num: " +str(len(frequent))
        count = 0
        for file in frequent:
            count +=1
            print "deal with  file num" + str(count) 
            items = file.split('-') 
            if len(items) != 3:   
                continue 
            else:
                monitorap = items[0]
            fp = open(frequent_path_wire + "/" + file)
            #lines = fp.readlines() 
            #fp.close()
            #os.remove(frequent_path_wire + "/" + file)
            step = DATA_STEP
            data = ""
            for line in fp:
                items = line.strip('\n').split(',')
                if len(items) != 3:#here 1
                    continue
                else:
                    sql_insert = "insert into %s (time,monitor_ap,digest,size) values('%s','%s','%s','%d') ON DUPLICATE KEY UPDATE digest=VALUES(digest)" \
                    %(table_name,items[0],monitorap,items[2],int(items[1]),)
                    #print sql_insert
                   # count_insert = cur.execute(sql_insert)
            conn.commit()
            fp.close()
            os.remove(frequent_path + "/" + file)       
            if data != "":
                page = urllib.urlopen(packet_url_wire.format(monitorap, data[:-1]))
    except:
    	traceback.print_exc()                                                                   
    	return 1
def transmit_frequence():
    try:
        frequent = os.listdir(frequent_path)
        print " packet file total num: " +str(len(frequent))
        count = 0
        for file in frequent:
            count +=1
            print "deal with  file num" + str(count) 
            items = file.split('-')
            if len(items) != 3:
                continue
            else:
                monitorap = items[0]
            fp = open(frequent_path + "/" + file)
            lines = fp.readlines()
            fp.close()
            os.remove(frequent_path + "/" + file)
            if len(lines) < 2:
                continue
            else:
                column = lines[0].strip('\n')
                aps = column.split(',')
                if len(aps) < 2:
                    continue
                aps_mac = aps[1:]
                data = ""
                step = DATA_STEP
                for line in lines[1:]:
                    content = line.strip('\n').split(',')
                    if len(content) < 2:
                        continue
                    time = content[0]
                    content = content[1:]
                    for i in range(len(content)):
                        if content[i] != "0":
                            step -=1
                            data += time + "," + aps_mac[i] + "," + content[i] + "|"
                            if step == 0:
                                page = urllib.urlopen(frequent_url.format(monitorap, data[:-1]))
                              #  print frequent_url.format(monitorap, data[:-1])
                                data = ""
                                step = 300
            if data != "":
                page = urllib.urlopen(frequent_url.format(monitorap,data))
               # print frequent_url.format(monitorap, data[:-1])
    except Exception:
        traceback.print_exc()
        return 1
# transmit throughput info to server
def transmit_throughput():
    try:
        throughput = os.listdir(throughput_path)
        print "throughput file total num: " + str(len(throughput))
        count = 0
        for file in throughput:
            count += 1
            print "deal with file num: " + str(count)
            items = file.split('-')
            if len(items) != 3:
                continue
            else:
                monitorap = items[0]
            fp = open(throughput_path + "/" + file)
            lines = fp.readlines()
            fp.close()
            os.remove(throughput_path + "/" + file)
            if len(lines) < 2:
                continue
            else:
                step = DATA_STEP
                data = ""
                for line in lines:
                    if line[0] == '-':
                        continue
                    items = line.strip('\n').split(',')
                    if len(items)!= 4:
                        continue
                    time = int(items[0])*1.0+int(items[1])/1000000.0
                    packet_size = items[2]
                    packet_time = items[3]
                    step -=1
                    data += str(time) + ","+ packet_size + "," + packet_time + "|"
                    if step ==0:
                        page = urllib.urlopen(throughput_url.format(monitorap, data[:-1]))
                      #  print throughput_url.format(monitorap, data[:-1])
                        data = ""
                        step = DATA_STEP
            if data != "":
                page = urllib.urlopen(throughput_url.format(monitorap,data[:-1]))
             #   print throughput_url.format(monitorap, data[:-1])
    except Exception:
        traceback.print_exc()
        return 2

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

