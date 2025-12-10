from bs4 import BeautifulSoup
import requests


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

    #if item.get("class") is not None and item.get("class")[0] == 'action' and item.get("class")[1] == 'next': #Next page
    #continue

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
#print(len(getBooksFromPage(3)))
#print(lastPage(209))
#print(lastPage2(209))