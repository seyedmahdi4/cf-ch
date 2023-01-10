from requests import Session, ConnectTimeout
from threading import Thread, Event
from queue import Queue
from math import floor
from sys import exit
import random

TIMEOUT = 1
MAX_THREAD = 20
HOST = "your_server_address"
PATH = "graphql"
TOP_RANK = 10
RESULT_FILE_PATH = "./result.txt"
IPS_FILE_PATH = "./ips.txt"


def main():
    try:
        exit_event = Event()
        ips = read_ip_list(IPS_FILE_PATH)
        random.shuffle(ips)
        entry_queue = Queue(maxsize=len(ips))
        print_queue = Queue(maxsize=len(ips))
        result_queue = Queue(maxsize=len(ips))
        for ip in ips:
            entry_queue.put(ip)
        print_thread = Thread(target=print_thread_handle,
                              args=(print_queue, result_queue, exit_event))
        print_thread.start()
        for _ in range(MAX_THREAD):
            thread = Thread(target=thread_handle,
                            args=(entry_queue, print_queue, exit_event))
            thread.daemon = True
            thread.start()
        entry_queue.join()
        print('Sorting results....')
        sorted_results = sort_results(list(result_queue.queue))
        print(f'Top {TOP_RANK} result:')
        print_top_results(sorted_results, TOP_RANK)
        print(f'Writing results in {RESULT_FILE_PATH}')
        write_results_to_file(sorted_results, RESULT_FILE_PATH)
        print('Done')
    except KeyboardInterrupt:
        exit_event.set()
        print('\nInterrupted!')
        exit(1)


class test_ip_result:
    def __init__(self, address: str, elapsed_time: float):
        self.address = address
        self.elapsed_time = elapsed_time


def test_ip(address: str) -> test_ip_result:
    try:
        result = Session().get(
            f'http://{address}/{PATH}', headers={"Host": HOST}, timeout=TIMEOUT)
    except ConnectTimeout:
        return test_ip_result(address, -1)
    except:
        return test_ip_result(address, -2)

    if result.status_code == 400:
        return test_ip_result(address, result.elapsed.total_seconds())

    return test_ip_result(address, -1)


def read_ip_list(path: str) -> list:
    ip_list = []
    with open(path, "r") as file:
        for line in file.readlines():
            ip_list.append(line.strip())
    return ip_list


def sort_results(result_list: list[test_ip_result]) -> list[test_ip_result]:
    return sorted(result_list, key=lambda x: x.elapsed_time)


def write_results_to_file(sorted_result_list: list[test_ip_result], file_path: str) -> None:
    with open(file_path, "w") as file:
        for result in sorted_result_list:
            file.write(
                f"{result.address} -- Latency:{result.elapsed_time}ms\n")


def print_top_results(sorted_results: list[test_ip_result], top_rank: int):
    for i in range(0, top_rank-1):
        result = sorted_results[i]
        print_result(result.address, result.elapsed_time)


def thread_handle(entry_queue: Queue, output_queue: Queue, exit_event: Event):
    while not exit_event.is_set():
        try:
            ip = entry_queue.get_nowait()
        except:
            break
        result = test_ip(ip)
        output_queue.put(result)
        entry_queue.task_done()


def print_result(address: str, response_time_in_millisecond: int) -> None:
    print(f"{address} -- Latency:{response_time_in_millisecond}ms")


def print_thread_handle(print_queue: Queue, result_queue: Queue, exit_event: Event):
    for _ in range(print_queue.maxsize):

        if exit_event.is_set():
            break

        result: test_ip_result = print_queue.get()

        if result.elapsed_time > 0:
            # Convert second to millisecond
            result.elapsed_time = floor(result.elapsed_time*1000)
            print_result(result.address, result.elapsed_time)
            result_queue.put_nowait(result)


if __name__ == "__main__":
    main()

