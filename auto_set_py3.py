# coding=utf-8
import json
import urllib.request
import re
import os

server_name = 'IP Address:'
url = 'http://isx.yt/'
# isx.yt
# isx.tn
code = 'utf-8'
headers = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'}  

req = urllib.request.Request(url=url,headers=headers)  
lines = urllib.request.urlopen(req).readlines() 

json_file_name='gui-config.json'
if not os.path.exists(json_file_name):
    with open(json_file_name,'w') as f:
        new_config=json.dumps({"configs":[]})
        f.write(new_config)

def find_pass(lines):
    result_list = []
    ok = 0
    passwd = 0
    port = 0
    host_name = ''
    for line in lines:
        line=line.decode('utf-8')#python3
        if not re.search(server_name, line) and ok == 0:
            continue
        if host_name == '':
            host_name = re.findall(':.*?>([\w\.]*)<', line)[0]

        ok = 1
        if 'Port:' in line:
            rst = re.findall(':.*?>(\d*)', line)

            port = rst[0]
            
        if 'Password:' in line:
            rst = re.findall(':.*?>(.*?)[<\r\n]', line)
            if (len(rst)==0 or not rst[0] or not port):
                if(len(rst)>0  and not rst[0]):
                    print(" get passwd failed, check regex")
                if( not port):
                    print(" get port failed, check regex")
                print("WARNING:the passwd \"%s\" is not set, please don't use it!"%host_name)
                ok = 0
                passwd = 0
                port = 0
                host_name = ''
                continue
            passwd = rst[0]
            
            
        if passwd and port:
            print("\nhost name:%s" % host_name)
            print('port:%s' % rst[0])
            print('passwd:%s' % rst[0])
            result_list.append((host_name, passwd, port))
            ok = 0
            passwd=0
            port=0
            host_name = ''
    return result_list

result_list = find_pass(lines)
print(result_list)
assert len(result_list) != 0, 'cannot get config'

f = open(json_file_name).read()
data = json.loads(f)
for host_name, passwd, port in result_list:
    is_init = 0
    for i in data['configs']:
        if i['server'] == host_name:
            is_init = 1
            i['password'] = passwd
            i['server_port'] = port

    if not is_init:
        new_conf = {'server': host_name,
                    'server_port': int(port),
                    'password': passwd,
                    'method': "aes-256-cfb",
                    }
        data['configs'].append(new_conf)
s = json.dumps(data,indent=3)
f = open(json_file_name, 'w')
f.write(s)
f.close()
os.system('start Shadowsocks.exe')
