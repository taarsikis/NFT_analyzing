import sys
from datetime import datetime

import cryptocompare

from get_data import get_all_data
from get_top import get_top_10
from EMA_calculation import calculate_EMA
from google_sheet_data import get_list_files_from_folder
from standard_price_calculation import calculate_strd_prices
import google_sheet_data as gs
import pandas as pd
import json
import plotly.graph_objects as go



def create_candlestick(df1, type):
    df1['Date1'] = df1['Date'].apply(lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S").timestamp())
    df1['Price'] = df1['Price'].apply(float)
    if type == 'hour':
        data = df1.groupby(df1['Date'].apply(lambda x: x.split(':')[0]))['Price'].agg(['mean', 'min', 'max'])
        date_min_max = df1.groupby(df1['Date'].apply(lambda x: x.split(':')[0]))['Date1'].agg(['min', 'max'])
    elif type == 'day':
        df1["Date"] = df1["Date"].astype(str)
        data = df1.groupby(df1['Date'].apply(lambda x: x.split(' ')[0]))['Price'].agg(['mean', 'min', 'max'])
        date_min_max = df1.groupby(df1['Date'].apply(lambda x: x.split(' ')[0]))['Date1'].agg(['min', 'max'])
    elif type == 'minute':
        data = df1.groupby(df1['Date'].apply(lambda x: x.split(':')[0] + ":" + x.split(':')[1]))['Price'].agg(
            ['mean', 'min', 'max'])
        date_min_max = df1.groupby(df1['Date'].apply(lambda x: x.split(':')[0] + ":" + x.split(':')[1]))['Date1'].agg(
            ['min', 'max'])

    # print(pd.DataFrame([datetime.fromtimestamp(x) for x in date_min_max['min']],[datetime.fromtimestamp(x) for x in date_min_max['max']]))

    opens = []

    for x in date_min_max['min']:
        price = list(df1[df1['Date1'] == x]['Price'])[0]
        opens.append(price)

    closes = []

    for x in date_min_max['max']:
        price = list(df1[df1['Date1'] == x]['Price'])[-1]
        closes.append(price)

    data['Open'] = opens
    data['Close'] = closes
    data['Higher'] = [max(opens[i], closes[i]) for i in range(len(opens))]
    data['Lower'] = [min(opens[i], closes[i]) for i in range(len(opens))]

    data['max'] = (data['max'] - data['Higher']) / 5 + data['Higher']
    data['min'] = data['Lower'] - (data['Lower']-data['min'])/5


    # fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig = go.Figure(data=[go.Candlestick(x=data.index.get_level_values(0),
                                         open=data['Open'],
                                         high=data['max'],
                                         low=data['min'],
                                         close=data['Close'])])

    fig.update_yaxes(fixedrange=False)
    fig.show()
    fig.write_html('plot.html')

def prepare_data():
    print(get_list_files_from_folder())
    f = open('NFT_slugs.json')
    slugs = json.loads(f.read())
    top = get_top_10()

    print(top)
    #
    print('DATA UPDATING - START')
    print('DATA UPDATING - START')
    print('DATA UPDATING - START')

    n = 1
    for project in top:
        if n == 11:
            break
        try:
            nft_slug = slugs[project[1]]
        except:
            print("We have no nft_slug for", project[1], ". Add its NFT slug to the file and rerun the code.")
            sys.exit()
        print(nft_slug)
        if nft_slug == "":
            print("We have no nft_slug for",project[1], ". Add its NFT slug to the file and rerun the code.")
            sys.exit()

        if nft_slug == "art-blocks":
            continue
        try:
            get_all_data(nft_slug)
        except KeyboardInterrupt:
            print('You skipped scrapping!')
        n += 1

    print('DATA UPDATING - END')
    print('DATA UPDATING - END')
    print('DATA UPDATING - END')


    print('EMA RECALCULATING - START')
    print('EMA RECALCULATING - START')
    print('EMA RECALCULATING - START')

    n = 1
    for project in top:
        if n == 11:
            break
        try:
            nft_slug = slugs[project[1]]
        except:
            print("We have no nft_slug for", project[1], ". Add its NFT slug to the file and rerun the code.")
            sys.exit()
        print('Calculating EMA for :',nft_slug)
        if nft_slug == "":
            print("We have no nft_slug for",project[1], ". Add its NFT slug to the file and rerun the code.")
            sys.exit()
        if nft_slug == "art-blocks":
            continue
        try:
            calculate_EMA(nft_slug)
        except KeyboardInterrupt:
            print('You skipped calculating!')
        n += 1


    print('EMA RECALCULATING - END')
    print('EMA RECALCULATING - END')
    print('EMA RECALCULATING - END')

    print('STANDARD PRICE CALCULATION - START')
    print('STANDARD PRICE CALCULATION - START')
    print('STANDARD PRICE CALCULATION - START')

    n = 1
    for project in top:
        if n == 11:
            break
        nft_slug = slugs[project[1]]
        print('Calculating STRD_prices for :',nft_slug)
        if nft_slug == "":
            print("We have no nft_slug for",project[1], ". Add its NFT slug to the file and rerun the code.")
        if nft_slug == "art-blocks":
            continue
        try:
            calculate_strd_prices(nft_slug,False)
        except KeyboardInterrupt:
            print('You skipped calculating!')
        n += 1

    print('STANDARD PRICE CALCULATION - END')
    print('STANDARD PRICE CALCULATION - END')
    print('STANDARD PRICE CALCULATION - END')

def calculate_index():
    # print(get_list_files_from_folder())
    sol_coef = cryptocompare.get_price(['SOL', 'ETH'], ['EUR', 'GBP'])["ETH"]['EUR'] / \
               cryptocompare.get_price(['SOL', 'ETH'], ['EUR', 'GBP'])['SOL']['EUR']
    f = open('NFT_slugs.json')
    slugs = json.loads(f.read())
    top = get_top_10()
    # print(top)
    def get_projects_coefficients(top):
        n = 1
        total_cap = 0
        projects = []
        for pr in top:
            if n == 11:
                break
            if pr[1] == 'Art Blocks':
                continue

            total_cap += pr[2]
            projects.append((slugs[pr[1]][0],pr[2],slugs[pr[1]][1]))


            n+=1

        projects = [(x[0], x[1]/total_cap, pd.read_csv(f"strd_prices/{x[0]}_strd_prices.csv"), x[2]) for x in projects]
        for x in projects:
            x[2]['project'] = x[0]
        return projects



    projects = get_projects_coefficients(top)
    curr_val = {}
    coefficients = {}
    n = 0
    for project in projects:
        curr_val[project[0]] = list(project[2]['Price'])[0]
        coefficients[project[0]] = project[1]
        if project[3] == 'SOL':
            print(project[2])
            project[2]["Price"] = project[2]["Price"] * sol_coef
            print(project[2])
        if n == 0:
            prices = project[2]
            n+= 1
        else:
            prices = prices.append(project[2])


    # print(coefficients)
    # print(curr_val)
    prices['Date1'] = prices['Date'].apply(lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S").timestamp())
    prices = prices.sort_values(by='Date1')
    # print(prices)
    price_list = []
    time_list = []
    for line in list(prices.values):

        # print(line)
        curr_val[line[3]] = line[2]
        price = 0
        for key in curr_val.keys():
            # print(key, curr_val[key], coefficients[key])
            price += curr_val[key] * coefficients[key]
        price_list.append(price)
        time_list.append(line[1])


    new_prices = pd.DataFrame()
    new_prices['Price'] = price_list
    new_prices['Date'] = time_list

    sheets = gs.get_list_files_from_folder()
    print(sheets)
    if "NFT_index" not in sheets:
        gs.create_spreadsheet("NFT_index")
        last = max([project[2]['Date'].apply(lambda x : datetime.strptime(x, "%Y-%m-%d %H:%M:%S").timestamp()).min() for project in projects])
        new_prices = new_prices[new_prices['Date'].apply(lambda x : datetime.strptime(x, "%Y-%m-%d %H:%M:%S").timestamp()) > last]
        gs.overwrite_file_with_dataframe("NFT_index", new_prices)

        df = new_prices
        print('file was created')

    else:
        print('used existed file')
        df = gs.read_spreadsheet_as_df("NFT_index")
        last = gs.get_last_timestamp_in("NFT_index")
        print(last)
        new_prices = new_prices[new_prices['Date'].apply(lambda x : datetime.strptime(x, "%Y-%m-%d %H:%M:%S").timestamp()) > last]
        df = df.append(new_prices)
        gs.overwrite_file_with_dataframe("NFT_index", df)
        print('File was updated')
        print('Deleting of dublicates....')
        gs.delete_duplicates_from_file("NFT_index")
        print('Dublicates were removed')

    print('Building a chart...')
    print(df)
    create_candlestick(df, 'day')


if __name__ == '__main__':
    # prepare_data()
    calculate_index()