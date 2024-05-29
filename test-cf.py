import ipaddress
import os
import sys
import operator
import requests
import random
import queue
import threading

n_thread = 5
n_test = 2
timeout = 0.7
path = "/"
host = "www.cloudflare.com"
shuffle = Truu


def test_ip(ip):
    try:
        res_list = []
        for i in range(n_test):
            result = session.get(
                f"http://{ip}/{path}", headers={"Host": host}, timeout=timeout)
            res_list.append(result.status_code)
            if i == n_test-1:
                print(
                    f"{ip}, Status: {ok if result.status_code == 200 else bad}, Elapsed-Time: {result.elapsed.total_seconds()}")

        if len(list(set(res_list))) == 1 and res_list[0] == 200:
            ip_dict.update({ip: int(result.elapsed.total_seconds()*1000)})
            with open("tested-ip.txt", 'a') as f:
                f.write(
                    f"{ip} Latency: {int(result.elapsed.total_seconds()*1000)}\n")
    except KeyboardInterrupt:
        print("Interrupted!")
        sys.exit()
    except Exception as e:
        print(f"IP {ip} {filtered} or {bad_ping}!")


def Sort_late_time():
    with open("Sorted-IP.txt", 'w') as sorted_file:
        for i in sorted(ip_dict.items(), key=operator.itemgetter(1)):
            sorted_file.write(f"{i[0]} -- Latency:{i[1]}ms\n")


def The_Best_Ips():
    print("\nThe 10 Best IP (Lower Latency)\n")
    os.system("bash -c 'head Sorted-IP.txt'")
    print()


def cidr_to_range(cidr):
    network = ipaddress.ip_network(cidr)
    start_ip = network.network_address
    end_ip = network.broadcast_address
    ip_range = list(ipaddress.ip_network(network).hosts())
    return [str(ip) for ip in ip_range]


def worker(q):
    while True:
        try:
            ip = q.get(block=False)
        except queue.Empty:
            break
        test_ip(ip)
        q.task_done()


ok = "\033[1;32mok\033[0m"
bad = "\033[1;31mbad\033[0m"
filtered = "\033[1;35mfiltered\033[0m"
bad_ping = "\033[1;35mbad ping\033[0m"
ip_dict = {}
ips0 = []
threads = []

q = queue.Queue()
session = requests.Session()


with open("ips.txt", "r") as ip_file:
    for ip in ip_file.readlines():
        if "/" in ip:
            ips0 += cidr_to_range(ip.strip())
        else:
            ips0.append(ip.strip())

if shuffle:
    random.shuffle(ips0)


for ip in ips0:
    q.put(ip)

for i in range(n_thread):
    t = threading.Thread(target=worker, args=(q,))
    threads.append(t)

for t in threads:
    t.start()

q.join()


Sort_late_time()
The_Best_Ips()
