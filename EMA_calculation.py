from datetime import datetime

import googleapiclient

import google_sheet_data as gs
import matplotlib.pyplot as plt
import Spreadsheet_deletion as sd


def calculate_EMA(nft_slug):
    def create_EMA_column(df):
        price_list = [float(x) for x in df['Price']]
        # print(price_list)
        # price_list.insert(0,sum(price_list)/len(price_list))
        ema_list = [sum(price_list[:20])/len(price_list[:20])]

        for idx,x in enumerate(price_list[1:]):
            curr_EMA = ema_list[idx]*0.8 + 0.2*float(x)
            ema_list.append(curr_EMA)

        df['EMA'] = ema_list

        return df




    def find_EMA_for_data(nft_slug):
        data = gs.read_spreadsheet_as_df(nft_slug)
        data = data[data['Date'].apply(lambda x : len(x.split('.'))) != 2]
        data['Date1'] = data['Date'].apply(lambda x : x.replace("T"," "))

        data['Date1'] = data['Date'].apply(lambda x : datetime.strptime(x, "%Y-%m-%d %H:%M:%S").timestamp())
        data = data.sort_values(by='Date1')
        # print(data)
        data['Price'] = data['Price'].apply(lambda x : x.replace(',','.'))
        data = data[data['Price'].apply(lambda x : len(x.split('.'))) < 3]
        data['Price'] = data['Price'].apply(float)



        # print(data)
        data_lists = data[data['Type'] == 'created']
        # print(data_lists['Price'].mean(),data_lists['Price'].std(), 'created')
        data_lists = data_lists[data_lists['Price'] < data_lists['Price'].quantile(0.98)]#.mean() + 3*data_lists['Price'].std()]
        data_lists = data_lists[data_lists['Price'] > data_lists['Price'].quantile(0.02)]#.mean() - 3*data_lists['Price'].std()]

        data_sales = data[data['Type'] == 'successful']
        # print(data_sales['Price'].mean(), data_sales['Price'].std(),'successful')
        data_sales = data_sales[data_sales['Price'] < data_sales['Price'].quantile(0.98)]#.mean() + 3*data_sales['Price'].std()]
        data_sales = data_sales[data_sales['Price'] > data_sales['Price'].quantile(0.02)]#.mean() - 3*data_sales['Price'].std()]

        data_bids = data[data['Type'] == 'bid_entered']
        # print(data_bids['Price'].mean(),data_bids['Price'].std(), 'bid_entered')
        data_bids = data_bids[data_bids['Price'] < data_bids['Price'].quantile(0.98)]#.mean() + 3*data_bids['Price'].std()]
        data_bids = data_bids[data_bids['Price'] > data_bids['Price'].quantile(0.02)]#.mean() - 3*data_bids['Price'].std()]

        # print(data_lists)
        data_lists = create_EMA_column(data_lists)
        # print(data_lists)
        # data_lists = data_lists[data_lists['EMA'] < data_lists['EMA'].mean() + 2*data_lists['EMA'].std()]
        # data_lists = data_lists[data_lists['EMA'] > data_lists['EMA'].mean() - 2*data_lists['EMA'].std()]

        data_bids = create_EMA_column(data_bids)
        # data_bids = data_bids[data_bids['EMA'] < data_bids['EMA'].mean() + 2*data_bids['EMA'].std()]
        # data_bids = data_bids[data_bids['EMA'] > data_bids['EMA'].mean() - 2*data_bids['EMA'].std()]
        data_sales = create_EMA_column(data_sales)
        # data_sales = data_sales[data_sales['EMA'] < data_sales['EMA'].mean() + 2*data_sales['EMA'].std()]
        # data_sales = data_sales[data_sales['EMA'] > data_sales['EMA'].mean() - 2*data_sales['EMA'].std()]

        result = data_lists.append(data_bids)
        result = result.append(data_sales)
        # print(result.sort_values(by='Date'))
        return result

    def update_EMA_data(collection_slug, info):
        collection_slug += '-EMA'
        sheets = gs.get_list_files_from_folder()
        # print(sheets)

        if collection_slug not in sheets:
            gs.create_spreadsheet(collection_slug)

            gs.overwrite_file_with_dataframe(collection_slug, info)
            print('file was created')

        else:
            print('used existed file')
            gs.overwrite_file_with_dataframe(collection_slug,info)
            print('File was updated')
            print('Deleting of dublicates....')
            gs.delete_duplicates_from_file(collection_slug)
            print('Dublicates were removed')


    nft_slug = nft_slug
    # try:
    #     sd.delete_spreadheet(nft_slug + '-EMA')
    # except:
    #     pass
    new_df = find_EMA_for_data(nft_slug)
    try:
        update_EMA_data(nft_slug, new_df[['Type',"Date","NFT","Price",'EMA']])
    except googleapiclient.errors.HttpError as x:
        print(x)
        print('Error__________________________________________________\n'*10)
        print("DATA WAS NOT SAVED")
        print(f"YOU SHOULD ADD MORE ROWS IN THE '{nft_slug}-EMA' file")
        print('Error____________________________________________\n'*10)


if __name__ == '__main__':
    calculate_EMA('veefriends')