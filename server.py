import socket
import threading
from bs4 import BeautifulSoup
import requests


class CustomThread(threading.Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None):
        threading.Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None
    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)
    def join(self, *args):
        threading.Thread.join(self, *args)
        return self._return

def getInfo(pagenum=1):
    url = f"https://knigomania.bg/new-books.html?p={pagenum}&product_list_mode=list"
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    info = soup.find_all("a")
    return info

def getBooksFromPage(info, books=20):
    res = [item.get_text().strip() for item in info if
           item.get("class") is not None and len(item.get("class")) == 1 and item.get("class")[
               0] == 'product-item-link']
    if books < 20:
        return [res[i] for i in range(0, books)]
    return res

def lastPage(info):
    res1 = 1
    for item in info:
        if item.get("class") == ["page","last"]:
            res1 = item.get_text().strip().split("\n")[1]
    res1 = int(res1)
    info = getInfo(res1)
    res2 = [item.get_text().strip() for item in info if
            item.get("class") is not None and len(item.get("class")) == 1 and item.get("class")[
                0] == 'product-item-link']
    return res1,len(res2)

host = '127.0.0.1'
port = 50000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host,port))
server.listen()


def clientFunc(client):
    try:
        msg = int(client.recv(1024).decode())
    except:
        client.send("Invalid input.".encode())
        client.close()
        return
    print(msg)
    if msg<0:
        client.send("Invalid input.".encode())
        client.close()
        return
    pages = msg // 20
    rest = msg % 20
    lp = lastPage(getInfo())
    all_pages = lp[0]
    last_page_books = lp[1]
    if pages + 1 > all_pages or (pages + 1 == all_pages and rest > last_page_books):
        client.send("Not enough results. Returning all available.".encode())
        pages = all_pages
        rest = 0
    for i in range(1,pages + 1):
        t = CustomThread(target=getBooksFromPage, args=(getInfo(i),))
        t.start()
        res = t.join()
        print(res)
        for book in res:
            client.send(book.encode())
            client.send("\n".encode())
    if rest>0:
        t = CustomThread(target=getBooksFromPage, args=(getInfo(pages + 1),rest))
        t.start()
        res = t.join()
        print(res)
        for book in res:
            client.send(book.encode())
            client.send("\n".encode())
    client.close()
    return

while True:
    client, address = server.accept()
    client.send("How many results to return?:".encode())

    thread = threading.Thread(target=clientFunc, args=(client,))

    thread.start()
