import requests

FIFO_FILE = None


def open_fifo(name):
    global FIFO_FILE
    FIFO_FILE = open(name, "wb")


LAST_FOUR = []


def pipe_data(url):
    body = requests.get(url).content
    FIFO_FILE.write(body)


def get_new_data(url):
    if url in LAST_FOUR:
        return
    if len(LAST_FOUR) == 4:
        LAST_FOUR.pop(0)
    LAST_FOUR.append(url)
    pipe_data(url)


def get_urls():
    resp = requests.get("http://tv.eenet.ee/hls/merikotkas.m3u8")
    text = resp.text
    urls = []
    for line in text.split("\n"):
        if "#" in line:
            continue
        urls.append("http://tv.eenet.ee/hls/"+line)
    return urls


def main(filename):
    open_fifo(filename)
    while True:
        for url in get_urls():
            get_new_data(url)
        time.sleep(1)

if __name__ == "__main__":
    import sys
    main(sys.argv[1])
