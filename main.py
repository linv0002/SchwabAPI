
import credentials
import schwabapi
from datetime import datetime, timedelta
from time import sleep

from schwabapi import get_account_orders, get_order_details, cancel_order, get_quotes, get_options_chain, \
    print_options_side_by_side, print_expiration_summary, print_iv_extremes, print_volume_oi_heatmap, \
    print_delta_theta_analysis, print_itm_otm_analysis, get_expiration_chain, get_price_history, print_price_history, \
    save_price_history, plot_candlestick_data, get_movers, print_market_moves, \
    get_fundamental_info, print_fundamental_info, get_market_hours, print_market_hours

appKey = credentials.app_key
appSecret = credentials.app_secret
callback_url = 'https://127.0.0.1'

def main():
    # create client
    client = schwabapi.create_client(appKey, appSecret, callback_url)

    # print("\n\nAccounts and Trading - Accounts.")
    #
    # # get account number and hashes for linked accounts
    # print("|\n|client.account_linked().json()", end="\n|")
    linked_accounts = schwabapi.get_linked_accounts(client)
    # print(linked_accounts)
    # # this will get the first linked account
    # main_account_number = linked_accounts[0].get('accountNumber')
    main_account_hash = linked_accounts[0].get('hashValue')
    #
    # ira_account_number = linked_accounts[1].get('accountNumber')
    # ira_account_hash = linked_accounts[1].get('hashValue')
    #
    # atlanta_account_number = linked_accounts[2].get('accountNumber')
    # atlanta_account_hash = linked_accounts[2].get('hashValue')
    #
    # kmom_account_number = linked_accounts[3].get('accountNumber')
    # kmom_account_hash = linked_accounts[3].get('hashValue')
    #
    # print("Accounts:")
    # print(f"Main Account: {main_account_number} Hash: {main_account_hash}")
    # print(f"IRA Account: {ira_account_number} Hash: {ira_account_hash}")
    # print(f"Atlanta Account: {atlanta_account_number} Hash: {atlanta_account_hash}")
    # print(f"Kmom Account: {kmom_account_number} Hash: {kmom_account_hash}")
    sleep(3)

    # get specific account positions
    # print("\n\nAccounts and Trading - Positions.")
    # print("Main Account Positions:")
    # main_account_details = get_account_details(client, main_account_hash)
    # print(main_account_details)
    #
    # main_positions = get_account_positions(client, main_account_hash)
    # for position in main_positions:
    #     print(f"Symbol: {position['instrument']['symbol']}, Quantity: {position['longQuantity']}, Market Value: {position['marketValue']}") ")
    # print()
    # sleep(3)
    #
    # # get specific account orders
    # print("\n\nAccounts and Trading - Orders.")
    # # Main Orders
    # print("Main Account Orders:")
    # main_orders = get_account_orders(client, main_account_hash, datetime.utcnow() - timedelta(days=1), datetime.utcnow())
    # for order in main_orders:
    #     print(f"Symbol: {order['orderLegCollection'][0]['instrument']['symbol']}, Quantity: {order['orderLegCollection'][0]['quantity']}, Price: {order['price']}, Order Type: {order['orderType']}")
    #
    # print()
    # sleep(3)

    # # place a stock order, get the details, the cancel it
    # order = {"orderType": "LIMIT", "session": "NORMAL", "duration": "DAY", "orderStrategyType": "SINGLE",
    #          "price": '9.00',
    #          "orderLegCollection": [
    #              {"instruction": "BUY", "quantity": 1000, "instrument": {"symbol": "WBA", "assetType": "EQUITY"}}]}
    # resp, order_id = place_order(client, main_account_hash, order)
    # print(resp)
    # print(f"Order id: {order_id}")
    # sleep(3)
    #
    # # get specific order details
    # print("Order details")
    #order_details = get_order_details(client, main_account_hash, order_id)
    # print(order_details)
    # sleep(300)
    #
    # # cancel specific order
    # print("Cancel order")
    # print(cancel_order(client, main_account_hash, order_id))
    # sleep(3)

    """

    # replace specific order (no demo implemented)
    # print("|\n|client.order_replace(account_hash, order_id, order)")
    # print(replace_order(client, main_account_hash, order_id, order))
    """

    # place an options order to sell to open
    # Symbol format: Underlying Symbol(6 chars including spaces) + Expiration(YYMMDD, 6 chars) +
    # Call / Put(1 char) + Strike Price(5 + 3 = 8 chars)
    # same for buy except we use BUY_TO_OPEN

    # order = {'orderType': 'LIMIT',
    #          'session': 'NORMAL',
    #          'price': 0.15,
    #          'duration': 'GOOD_TILL_CANCEL',
    #          'orderStrategyType': 'SINGLE',
    #          'complexOrderStrategyType': 'NONE',
    #          'orderLegCollection': [
    #              {'instruction': 'SELL_TO_OPEN',
    #               'quantity': 10,
    #               'instrument': {'symbol': 'WBA   240906P00009000',
    #                              'assetType': 'OPTION'
    #                              }
    #               }
    #          ]
    #          }
    #
    # resp, order_id = place_order(client, main_account_hash, order)
    # print(resp)
    # print(f"Order id: {order_id}")
    # sleep(3)
    #
    # # get specific order details
    # print("Order details")
    # order_details = get_order_details(client, main_account_hash, order_id)
    # print(order_details)
    # sleep(300)
    #
    # # cancel specific order
    # print("Cancel order")
    # print(cancel_order(client, main_account_hash, order_id))
    # sleep(3)

    # # Buy an options call spread
    # order = {
    #     "orderType": "NET_DEBIT",
    #     "session": "NORMAL",
    #     "price": "0.15",
    #     "duration": "DAY",
    #     "orderStrategyType": "SINGLE",
    #     "orderLegCollection": [
    #         {
    #             "instruction": "BUY_TO_OPEN",
    #             "quantity": 30,
    #             "instrument": {
    #                 "symbol": "KSS   240830P00017500",
    #                 "assetType": "OPTION"
    #             }
    #         },
    #         {
    #             "instruction": "SELL_TO_OPEN",
    #             "quantity": 30,
    #             "instrument": {
    #                 "symbol": "KSS   240830P00016500",
    #                 "assetType": "OPTION"
    #             }
    #         }
    #     ]
    # }
    #
    # resp, order_id = place_order(client, main_account_hash, order)
    # print(resp)
    # print(f"Order id: {order_id}")
    # sleep(3)
    #
    # # get specific order details
    # print("Order details")
    # order_details = get_order_details(client, main_account_hash, order_id)
    # print(order_details)
    # sleep(300)
    #
    # # cancel specific order
    # print("Cancel order")
    # print(cancel_order(client, main_account_hash, order_id))
    # sleep(3)

    # # get mulitple quotes
    # my_quotes = (get_quotes(client,['KSS', 'WBA']))
    # for key in my_quotes:
    #     print(f"Symbol: {key}, Price: {my_quotes[key]['quote']['lastPrice']}, pct_change: {my_quotes[key]['quote']['netPercentChange']}, volume: {my_quotes[key]['quote']['totalVolume']}, high: {my_quotes[key]['quote']['highPrice']}, low: {my_quotes[key]['quote']['lowPrice']}")
    # sleep(3)

    # # get single quote
    # intc_quote = get_quotes(client, 'INTC')
    # print(f"Symbol: INTC, Price: {intc_quote['INTC']['quote']['lastPrice']}, pct_change: {intc_quote['INTC']['quote']['netPercentChange']}, volume: {intc_quote['INTC']['quote']['totalVolume']}, high: {intc_quote['INTC']['quote']['highPrice']}, low: {intc_quote['INTC']['quote']['lowPrice']}")
    # sleep(3)

    # # get options chain
    # kss_options_chain = get_options_chain(client, 'KSS')
    # sleep(3)
    #
    # # Example usage:
    # # Specify the number of strike prices centered around delta = 0.5
    # num_strikes = 14
    #
    # # Specify the expiration dates to include (default is to include all)
    # expiration_dates = ['2024-08-30:2', '2024-09-06:2']  # Add more dates as needed
    #
    # # Call the functions to analyze the options chain
    # print("Options Chain for KSS")
    # print_options_side_by_side(kss_options_chain, num_strikes=num_strikes, exp_dates=expiration_dates)
    #
    # print("Expiration Summary")
    # print_expiration_summary(kss_options_chain)
    #
    # print("IV Extremes")
    # print_iv_extremes(kss_options_chain, expiration_dates)
    #
    # print("Volume and Open Interest Heatmap")
    # print_volume_oi_heatmap(kss_options_chain, expiration_dates)
    #
    # print("Delta and Theta Analysis")
    # print_delta_theta_analysis(kss_options_chain, expiration_dates)
    #
    # print("ITM and OTM Analysis")
    # kss_quote = get_quotes(client, 'KSS')
    # price = kss_quote['KSS']['quote']['lastPrice']
    # print_itm_otm_analysis(kss_options_chain, expiration_dates, price)

    # print(get_expiration_chain(client,"KSS"))

    # kss_1_year_price_history = get_price_history(client, "KSS", "year", frequencyType="daily", frequency=1)
    # print(kss_1_year_price_history)
    # print_price_history(kss_1_year_price_history)
    # save_price_history(kss_1_year_price_history, 'KSS_1_year_price_history.csv')
    # plot_candlestick_data(kss_1_year_price_history)

    # market_movers = get_movers(client, "$COMPX", sort="VOLUME")
    # print_market_moves(market_movers)

    # kss_fundamentals = get_fundamental_info(client, "KSS")
    # print_fundamental_info(kss_fundamentals)

    # get date for next week in YYYY-MM-DD format
    to_date = datetime.now() + timedelta(days=1)  # see times for market tommrrow
    to_date = to_date.strftime("%Y-%m-%d")

    market_hours = get_market_hours(client, ["equity", "option"], to_date)
    # market_hours = get_market_hours(client, ["future"], to_date)
    print_market_hours(market_hours)

if __name__ == '__main__':
    main()



