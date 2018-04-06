import time
import requests
import threading
from queue import Queue

MIN_BUFFER_LEN = 4

FIFO_FILE = None

QUEUE = Queue(10)


class DataThread(threading.Thread):
    def __init__(self, queue):
        super(DataThread, self).__init__()
        self.queue = queue
        self.last_four = []

    def run(self):
        while True:
            for url in self.get_urls():
                self.get_new_data(url, self.last_four)
            time.sleep(1)

    def buffer_data(self, url):
        body = requests.get(url).content
        self.queue.put(body)

    def get_new_data(self, url, last_four):
        if url in last_four:
            return
        if len(last_four) == 4:
            last_four.pop(0)
        last_four.append(url)
        self.buffer_data(url)

    def get_urls(self):
        resp = requests.get("http://tv.eenet.ee/hls/merikotkas.m3u8")
        text = resp.text
        urls = []
        for line in text.split("\n"):
            if "#" in line:
                continue
            urls.append("http://tv.eenet.ee/hls/"+line)
        return urls


def open_fifo(name):
    global FIFO_FILE
    FIFO_FILE = open(name, "wb")


def write_buffer():
    data = QUEUE.get()
    FIFO_FILE.write(data)
    QUEUE.task_done()


def main(filename):
    open_fifo(filename)

    th = DataThread(QUEUE)
    th.start()

    while QUEUE.unfinished_tasks < MIN_BUFFER_LEN:
        time.sleep(1)

    while True:
        write_buffer()


if __name__ == "__main__":
    import sys
    main(sys.argv[1])
