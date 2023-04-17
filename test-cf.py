import os
import sys
import operator
import requests
import random

timeout = 1
ips = []
ok = "\033[1;32mok\033[0m"
bad = "\033[1;31mbad\033[0m"
filtered = "\033[1;35mfiltered\033[0m"
bad_ping = "\033[1;35mbad ping\033[0m"
cfHost = os.environ.get('CF_HOST')
cfPath = os.environ.get('CF_PATH', '')


def test_ip():
    session = requests.Session()
    ip_dict = {}

    with open("ips.txt", "r") as ip_file:

        for ip in ip_file.readlines():
            ips.append(ip.strip())
    random.shuffle(ips)
    for ip in ips:
        try:
            result = session.get(
                f"http://{ip}/{cfPath}", headers={"Host": cfHost}, timeout=timeout)

            print(
                f"{ip}, Status: {ok if result.status_code == 400 else bad}, Elapsed-Time: {result.elapsed.total_seconds()}")

            if result.status_code == 400:
                ip_dict.update({ip: int(result.elapsed.total_seconds()*1000)})
                with open("/tmp/tested-ip.txt", 'a') as f:
                    f.write(
                        f"{ip} Latency: {int(result.elapsed.total_seconds()*1000)}\n")
        # Interrupt by User
        except KeyboardInterrupt:
            print("Interrupted!")
            sys.exit()
        # Any other Error Will be Ignored
        except:
            print(f"IP {ip} {filtered} or {bad_ping}!")
    return ip_dict


def Sort_late_time():
    d = test_ip()
    with open("/tmp/Sorted-IP.txt", 'w') as sorted_file:

        for i in sorted(d.items(), key=operator.itemgetter(1)):
            sorted_file.write(f"{i[0]} -- Latency:{i[1]}ms\n")


def The_Best_Ips():
    print("\nThe 10 Best IP (Lower Latency)\n")
    os.system("bash -c 'head /tmp/Sorted-IP.txt'")
    print()


Sort_late_time()
The_Best_Ips()
if os.environ.get('FOR_PASS') is True:
    os.system("tail -f")
