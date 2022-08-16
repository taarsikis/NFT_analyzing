import time
from datetime import datetime

from plotly.subplots import make_subplots

import google_sheet_data as gs
from matplotlib import pyplot as plt
import pandas as pd
import plotly.graph_objects as go


def calculate_strd_prices(nft_slug, plot = True):
    def create_candlestick(df1,type):
        df1['Date1'] = df1['Date'].apply(lambda x : datetime.strptime(x, "%Y-%m-%d %H:%M:%S").timestamp())

        if type == 'hour':
            data = df1.groupby(df1['Date'].apply(lambda x : x.split(':')[0]))['Price'].agg(['mean','min','max'])
            date_min_max = df1.groupby(df1['Date'].apply(lambda x : x.split(':')[0]))['Date1'].agg(['min','max'])
        elif type == 'day':
            data = df1.groupby(df1['Date'].apply(lambda x: x.split(' ')[0]))['Price'].agg(['mean','min','max'])
            date_min_max = df1.groupby(df1['Date'].apply(lambda x : x.split(' ')[0]))['Date1'].agg(['min','max'])
        elif type == 'minute':
            data = df1.groupby(df1['Date'].apply(lambda x: x.split(':')[0]+":"+x.split(':')[1]))['Price'].agg(['mean','min','max'])
            date_min_max = df1.groupby(df1['Date'].apply(lambda x : x.split(':')[0]+":"+x.split(':')[1]))['Date1'].agg(['min','max'])

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
        data['Higher'] = [max(opens[i],closes[i]) for i in range(len(opens))]
        data['max'] = (data['max'] - data['Higher'])/5 + data['Higher']

        # fig = make_subplots(specs=[[{"secondary_y": True}]])

        fig = go.Figure(data=[go.Candlestick(x=data.index.get_level_values(0),
                        open=data['Open'],
                        high=data['max'],
                        low=data['min'],
                        close=data['Close'])])

        fig.update_yaxes(fixedrange=False)
        fig.show()
        fig.write_html('plot.html')


    def find_standard_price(nft_slug):
        data_with_EMA = gs.read_spreadsheet_as_df(nft_slug + '-EMA')
        data_with_EMA = data_with_EMA.drop_duplicates()
        data_with_EMA['Date1'] = data_with_EMA['Date'].apply(
            lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S").timestamp())
        data_with_EMA = data_with_EMA.sort_values(by='Date1')

        prices = data_with_EMA[data_with_EMA['Type'] == 'successful'].sort_values(by='Date')
        prices['Date1'] = prices['Date'].apply(lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S").timestamp())
        prices = prices.sort_values(by='Date1')
        bids = data_with_EMA[data_with_EMA['Type'] == 'bid_entered'].sort_values(by='Date')
        bids['Date1'] = bids['Date'].apply(lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S").timestamp())
        bids = bids.sort_values(by='Date1')
        listings = data_with_EMA[data_with_EMA['Type'] == 'created'].sort_values(by='Date')
        listings['Date1'] = listings['Date'].apply(lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S").timestamp())
        listings = listings.sort_values(by='Date1')

        prices_times = prices['Date']
        prices_EMAs = prices['EMA'].apply(float)

        bids_times = bids['Date']
        bids_EMAs = bids['EMA'].apply(float)

        listings_times = listings['Date']
        listings_EMAs = listings['EMA'].apply(float)
        print(listings_EMAs)
        last_price_EMA = list(prices_EMAs)[0]
        print(last_price_EMA, 'first sales')

        last_bids_EMA = list(bids_EMAs)[0]
        print(last_bids_EMA, 'first bids')

        last_listings_EMA = list(listings_EMAs)[0]  # sum(listings_EMAs)/len(listings_EMAs)
        print(last_listings_EMA, 'first listing')

        strd_values = []
        strd_values_times = []

        a_coef = 0.5
        b_coef = 0.3
        c_coef = 0.2

        for idx, row in data_with_EMA.iterrows():
            trans_type = row['Type']
            trans_date = row['Date']
            trans_EMA = row['EMA']

            if trans_type == 'created':
                last_listings_EMA = float(trans_EMA)
            elif trans_type == 'successful':
                last_price_EMA = float(trans_EMA)
            elif trans_type == 'bid_entered':
                last_bids_EMA = float(trans_EMA)

            strd_price = a_coef * last_price_EMA + b_coef * last_bids_EMA + c_coef * last_listings_EMA

            strd_values.append(strd_price)
            strd_values_times.append(trans_date)
            # print(strd_price)
            # print(row['Type'], row['Date'], row['EMA'])

        strd_prices = pd.DataFrame()
        strd_prices['Date'] = pd.to_datetime(strd_values_times)
        strd_prices['Price'] = strd_values

        # strd_prices = strd_prices[strd_prices['Price'] < strd_prices['Price'].mean() + 2*strd_prices['Price'].std()]
        #
        #                                      |
        #                                     \ /
        #                                      .
        strd_prices = strd_prices[strd_prices['Price'] < strd_prices['Price'].quantile(0.98)]


        # strd_prices = strd_prices[strd_prices['Price'] > strd_prices['Price'].mean() - 2*strd_prices['Price'].std()]

        strd_prices.groupby([strd_prices["Date"].dt.month, strd_prices["Date"].dt.day, strd_prices["Date"].dt.hour,
                             strd_prices["Date"].dt.minute, strd_prices["Date"].dt.second])["Price"].mean().plot(
            kind='line', rot=0
        )

        # print(strd_prices)
        strd_prices.to_csv(f'strd_prices/{nft_slug}_strd_prices.csv')

        if plot:
            plt.show()
            df = pd.read_csv(f'strd_prices/{nft_slug}_strd_prices.csv')
            create_candlestick(df, 'day')



    find_standard_price(nft_slug)


if __name__ =="__main__":
    calculate_strd_prices('azuki', True)