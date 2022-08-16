import json
import time
from datetime import datetime
import google_sheet_data as gs
import requests
import pandas as pd


def get_all_data(nft_slug):
    def get_data(collection_slug : str , before_date = False , after_date = False):
        error = False
        types1 = ['created','successful','bid_entered']
        types = []
        dates = []
        names = []
        prices = []
        for tp in types1:
            # print(tp)
            url = "https://api.opensea.io/api/v1/events?collection_slug=" + collection_slug +f'&event_type={tp}'

            if after_date:
                url += '&occurred_after=' + after_date

            if before_date:
                url += '&occurred_before=' + before_date



            print(url)

            headers = {
                "Accept": "application/json",
                "X-API-KEY": "ad13590917534b71ab775e21a9949e66"
            }
            next = True

            try:
                while next:

                    if isinstance(next,str):
                        url +=  '&cursor='+ next
                    response = requests.get(url, headers=headers)

                    result_dict = response.json()#json.loads(response.text)
                    # print(result_dict)
                    next = result_dict['next']
                    if next:
                        next = next.replace('=','%3D')

                    assets = result_dict['asset_events']

                    for i in range(len(assets)):
                        curr_event = assets[i]
                        # print(i)
                        # print(curr_event)

                        if not curr_event['asset']:
                            continue

                        event_type = curr_event['event_type']
                        event_time = curr_event['event_timestamp']
                        NFT_name = curr_event['asset']['name']
                        if curr_event['event_type'] == 'created':

                            types.append(event_type)
                            dates.append(event_time)
                            names.append(NFT_name)
                            prices.append(int(curr_event['ending_price'])/1000000000000000000)
                            print(nft_slug + " :",curr_event['event_type'], curr_event['event_timestamp'],curr_event['asset']['name'],int(curr_event['ending_price'])/1000000000000000000)


                        if curr_event['event_type'] == 'successful':

                            types.append(event_type)
                            dates.append(event_time)
                            names.append(NFT_name)
                            prices.append(int(curr_event['total_price'])/1000000000000000000)

                            print(nft_slug + " :",curr_event['event_type'], curr_event['event_timestamp'],curr_event['asset']['name'],int(curr_event['total_price'])/1000000000000000000)

                        if curr_event['event_type'] == 'bid_entered':

                            types.append(event_type)
                            dates.append(event_time)
                            names.append(NFT_name)
                            prices.append(int(curr_event['bid_amount'])/1000000000000000000)

                            print(nft_slug + " :",curr_event['event_type'], curr_event['event_timestamp'],curr_event['asset']['name'],int(curr_event['bid_amount'])/1000000000000000000)
            except Exception as x:
                print('error occurred')
                print('error occurred')
                print('error occurred')
                print(x)
                error = x


        res = pd.DataFrame()
        res['Type'] = types
        res['Date'] = dates
        res['NFT'] = names
        res['Price'] = prices

        return res , error

    def get_collection_start_date(collection_slug):
        import requests

        url = f"https://api.opensea.io/api/v1/collection/{collection_slug}"

        response = requests.get(url)

        info = json.loads(response.text)

        return info['collection']['created_date']

    def update_NFT_data(collection_slug, info):
        sheets = gs.get_list_files_from_folder()
        print(sheets)
        if collection_slug  not in sheets:
            gs.create_spreadsheet(collection_slug)

            gs.overwrite_file_with_dataframe(collection_slug, info)
            print('file was created')

        else:
            print('used existed file')
            df = gs.read_spreadsheet_as_df(collection_slug)
            df = df.append(info)
            gs.overwrite_file_with_dataframe(collection_slug,df)
            print('File was updated')
            print('Deleting of dublicates....')
            gs.delete_duplicates_from_file(collection_slug)
            print('Dublicates were removed')



    def get_data_starting_from_1week_per_updating(start_time, nft_slug):
        error = False
        current_time = time.time()
        skip_time = 86400#604800 # 1 week
        while start_time < current_time:
            try:
                if error:
                    if res['Date'].max():
                        last_date = res['Date'].max()

                        if str(last_date) != "nan":
                            start_time = int(datetime.strptime(last_date.split('.')[0], "%Y-%m-%dT%H:%M:%S").timestamp())
                        else:
                            res = pd.DataFrame()
                            res['Type'] = []
                            res['Date'] = []
                            res['NFT'] = []
                            res['Price'] = []
                            # start_time = start_time + skip_time/4
                            start_time = gs.get_last_timestamp_in(nft_slug) + 20000


                    else:
                        start_time = gs.get_last_timestamp_in(nft_slug)
                    error = False
                    print('changed start time')
                    print('changed start time')
                    print('changed start time')
                    print('changed start time')

                res, error = get_data(nft_slug, after_date=str(start_time), before_date=str(start_time + skip_time))
                update_NFT_data(nft_slug, res)

                print("--------------------------------------------------------------------")
                print("--------------------------------------------------------------------")
                print('PROJECT: '+nft_slug)
                print(f"DATA WAS COLLECTED FROM {datetime.fromtimestamp(start_time)} TO {datetime.fromtimestamp(start_time + skip_time)}")
                print("--------------------------------------------------------------------")
                print("--------------------------------------------------------------------")
                start_time += skip_time
            except Exception as x:
                for _ in range(10):
                    print("WAS ERROR")
                print(x)
                start_time += skip_time/4




    nft_slug = nft_slug
    one_month_in_seconds = 2678400

    creation_time = get_collection_start_date(nft_slug)
    normal_time = creation_time.split("T")[0].split('-')

    creation_timestamp = int(datetime.strptime('/'.join(normal_time), "%Y/%m/%d").timestamp())

    if nft_slug not in gs.get_list_files_from_folder():
        print("Its new in our list")
        print("STARTED FROM CREATION")

        get_data_starting_from_1week_per_updating(creation_timestamp, nft_slug)
    else:
        last_date = gs.get_last_timestamp_in(nft_slug)
        print(nft_slug)
        print(f'COLLECTING STARTED FROM {datetime.fromtimestamp(last_date)}')
        get_data_starting_from_1week_per_updating(last_date, nft_slug)

if __name__ == '__main__':
    get_all_data('bored-ape-kennel-club')
