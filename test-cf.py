import os
import sys
import operator
import requests


def test_ip():
    session = requests.Session()
    ip_dict = {}

    with open("ips.txt", "r") as ip_file:

        for ip in ip_file.readlines():
            ip = ip.strip()

            try:
                result = session.get(
                    f"http://{ip}/ray", headers={"Host": "localhoster.ml"}, timeout=0.4)

                print(
                    f"{ip}, Status-Code: {result.status_code}, Elapsed-Time: {result.elapsed.total_seconds()}")

                if result.status_code == 400:
                    ip_dict.update({ip: int(result.elapsed.total_seconds()*1000)})
                    with open("tested-ip.txt", 'a') as f:
                        f.write(
                            f"{ip} Latency: {int(result.elapsed.total_seconds()*1000)}\n")
            # Interrupt by User
            except KeyboardInterrupt:
                print("Interrupted!")
                sys.exit()
            # Any other Error Will be Ignored
            except:
                pass

    return ip_dict


def Sort_late_time():
    d = test_ip()
    with open("Sorted-IP.txt", 'w') as sorted_file:

        for i in sorted(d.items(), key=operator.itemgetter(1)):
            sorted_file.write(f"{i[0]} -- Latency:{i[1]}ms\n")

def The_Best_Ips():
    print("\nThe 10 Best IP (Lower Latency)\n")
    os.system("bash -c 'head Sorted-IP.txt'")
    print()

Sort_late_time()
The_Best_Ips()
