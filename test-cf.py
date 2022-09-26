import operator
import requests
s=requests.Session()
ips = []
d = {}
with open("ips.txt","r") as f:
   for i in f:
       ips.append(i.strip())

for ip in ips:
    try:
        r=s.get("http://"+ip+"/ray", headers={"Host":"localhoster.ml"},timeout=0.4)
        print(r,r.elapsed.total_seconds())
        if r.status_code==400:
            d.update({ip:int(r.elapsed.total_seconds()*1000)})
            with open("tested-ip.txt",'a') as f:
                f.write(f"{ip},{int(r.elapsed.total_seconds()*1000)}\n")
    except:
        pass
with open("test-ip.txt",'w') as f:
    for i in sorted(d.items(), key=operator.itemgetter(1)):
        print(f"{i[0]},{i[1]}ms")
        f.write(f"{i[0]},{i[1]}ms\n")
