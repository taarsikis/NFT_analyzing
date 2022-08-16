from lxml import html
import requests
import json
# Request the page

def get_top_10():
    page = requests.get('https://coinmarketcap.com/ru/nft/collections/')
    results = str(page.content).split('"collections":')[1].split(',"blockChains":')[0].replace("\'s","s").replace("\s","s").replace('false',"False").replace('"popular":False','"popular":"False"')
    results = json.loads(results)
    collections = []
    for collection in results:
        collections.append([collection['rank'],collection['name'], collection['marketCapUsd']])

    collections = sorted(collections,key=lambda x:x[2],reverse=True)
    for i in range(1,len(collections)+1):
        collections[i-1][0] = i

    return [tuple(x) for x in collections][:15]

if __name__ == '__main__':
    print(get_top_10())