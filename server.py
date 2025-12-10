import socket
import threading
import scrape_funcs

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


def getBooksFromPage(pagenum, books=20):
    url = f"https://knigomania.bg/new-books.html?p={pagenum}&product_list_mode=list"
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    info = soup.find_all("a")
    res = [item.get_text().strip() for item in info if
           item.get("class") is not None and len(item.get("class")) == 1 and item.get("class")[
               0] == 'product-item-link']
    if books < 20:
        return [res[i] for i in range(0, books)]
    return res


def getFirstBookOnPage(pagenum):
    url = f"https://knigomania.bg/new-books.html?p={pagenum}&product_list_mode=list"
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    info = soup.find_all("a")
    for item in info:
        if item.get("class") is not None and len(item.get("class")) == 1 and item.get("class")[
               0] == 'product-item-link':
            print(item.get_text().strip())
            return item.get_text().strip()
    return

def lastPage(pagenum):
    url = f"https://knigomania.bg/new-books.html?p={pagenum}&product_list_mode=list"
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    info = soup.find_all("a")
    res = [item.get_text().strip() for item in info if
           item.get("class") is not None and len(item.get("class")) == 1 and item.get("class")[
               0] == 'product-item-link']
    if len(res) < 20:
        return True
    if res[0] == getBooksFromPage(pagenum + 1)[0]:
        return True
    return False

def lastPage2(pagenum):
    if getFirstBookOnPage(pagenum) == getFirstBookOnPage(pagenum + 1):
        return True
    return False

host = '127.0.0.1'
port = 50000 #9999
ThreadCount = 0

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host,port))
server.listen()


clients = []
#res = queue.Queue() #Kak da vyrna rezultatite na klienta???????
def clientFunc(client):
    msg = int(client.recv(1024))
    print(msg)
    pages = msg // 20
    rest = msg % 20
    for i in range(1,pages + 1):
        t = CustomThread(target=scrape_funcs.getBooksFromPage, args=(i,))
        t.start()
        res = t.join()
        print(res)
        for book in res:
            client.send(book.strip().encode())
            #client.send("\n".encode())

    t = CustomThread(target=scrape_funcs.getBooksFromPage, args=(pages + 1,rest))
    t.start()
    res = t.join()
    print(res)
    for book in res:
        client.send(book.encode())
    #client.send(str(t.join()).encode())
    client.send("DONE".encode())
    client.close()

while True:
    client, address = server.accept()
    clients.append(client)
    client.send("How many results to return?:".encode())
    #ans = client.recv(1024).decode()
    #print(ans)

    thread = threading.Thread(target=clientFunc, args=(client,))
    thread.start()