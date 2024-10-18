import schwabdev
import os
import json
from datetime import datetime, timedelta
import csv
import matplotlib
matplotlib.use('qt5agg')  # Use the Qt5Agg backend to get plots in a separate window
import matplotlib.pyplot as plt
import mplfinance as mpf
import pandas as pd

def create_client(app_key, app_secret, callback_url):
    return schwabdev.Client(app_key, app_secret, callback_url, verbose=True)

def get_linked_accounts(client):
    return client.account_linked().json()

def get_account_details(client, account_hash):
    return client.account_details(account_hash).json()


def print_account_info(account_details):
    account_info = account_details.get("securitiesAccount", {})

    # Type
    account_type = account_info.get('type', 'N/A')
    print(f"Type: {account_type}")

    # Current Balances
    current_balances = account_info.get("currentBalances", {})
    cash_balance = current_balances.get("cashBalance", 'N/A')
    liquidation_value = current_balances.get("liquidationValue", 'N/A')
    buying_power = current_balances.get("buyingPower", 'N/A')
    margin_balance = current_balances.get("marginBalance", 'N/A')

    print(f"Cash: {cash_balance}")
    print(f"Liquidation Value: {liquidation_value}")
    print(f"Buying Power: {buying_power}")
    print(f"Margin Balance: {margin_balance}")

def get_account_positions(client, account_hash):
    account_details =  client.account_details(account_hash, fields='positions').json()
    return account_details['securitiesAccount']['positions']


def print_account_positions(main_positions):
    for position in main_positions:
        print(f"Symbol: {position['instrument']['symbol']}, Quantity: {position['longQuantity']}, Market Value: {position['marketValue']}")

def get_account_orders(client, account_hash, start_date, end_date):
    return client.account_orders(account_hash, start_date, end_date).json()


def print_account_orders(orders):
    for order in orders:
        print(f"Symbol: {order['orderLegCollection'][0]['instrument']['symbol']}, Quantity: {order['orderLegCollection'][0]['quantity']}, Price: {order['price']}, Order Type: {order['orderType']}")
        print(f"Order ID: {order['orderId']}, Status: {order['status']}, Filled Quantity: {order['filledQuantity']}, Remaining Quantity: {order['remainingQuantity']}")
        print("--------------------------------------------------")

def place_order(client, account_hash, order):
    resp = client.order_place(account_hash, order)
    order_id = resp.headers.get('location', '/').split('/')[-1]
    return resp, order_id

def get_order_details(client, account_hash, order_id):
    return client.order_details(account_hash, order_id).json()

def cancel_order(client, account_hash, order_id):
    return client.order_cancel(account_hash, order_id)

def replace_order(client, account_hash, order_id, order):
    resp = client.order_replace(account_hash, order_id, order)
    order_id = resp.headers.get('location', '/').split('/')[-1]
    return resp, order_id

def get_transactions(client, account_hash, start_date, end_date):
    return client.account_transactions(account_hash, start_date, end_date).json()

def get_user_preferences(client):
    return client.preferences().json()

def get_quotes(client, symbols):
    return client.quotes(symbols).json()

def print_quotes(quotes):
    for key, quote_data in quotes.items():
        quote_info = quote_data.get('quote', {})
        symbol = key
        price = quote_info.get('lastPrice', 'N/A')
        bid_price = quote_info.get('bidPrice', 'N/A')
        ask_price = quote_info.get('askPrice', 'N/A')
        pct_change = quote_info.get('netPercentChange', 'N/A')
        volume = quote_info.get('totalVolume', 'N/A')
        high = quote_info.get('highPrice', 'N/A')
        low = quote_info.get('lowPrice', 'N/A')

        print(f"Symbol: {symbol}, Price: {price}, Bid Price: {bid_price}, Ask Price: {ask_price}, "
              f"pct_change: {pct_change}, volume: {volume}, high: {high}, low: {low}")

def get_single_quote(client, symbol):
    return client.quote(symbol).json()

def get_options_chain(client, symbol):
    return client.option_chains(symbol).json()


# Function to find the closest strike to delta = 0.5
def find_closest_strike(strikes):
    closest_strike = min(strikes, key=lambda x: abs(strikes[x][0]['delta'] - 0.5))
    return float(closest_strike)


def print_options_side_by_side(options_chain, num_strikes=None, exp_dates=None):
    # Extract call and put expiration maps
    call_exp_map = options_chain.get('callExpDateMap', {})
    put_exp_map = options_chain.get('putExpDateMap', {})

    # Extract available expiration dates
    available_call_dates = list(call_exp_map.keys())
    available_put_dates = list(put_exp_map.keys())

    print(f"Available call expiration dates in the data: {available_call_dates}")
    print(f"Available put expiration dates in the data: {available_put_dates}")

    # If no expiration dates are provided, default to using all available expiration dates
    if exp_dates is None:
        exp_dates = available_call_dates

    # Create a mapping from stripped dates to full dates
    stripped_call_dates = {date.split(':')[0]: date for date in available_call_dates}
    stripped_put_dates = {date.split(':')[0]: date for date in available_put_dates}

    # Process each provided expiration date
    for exp_date in exp_dates:
        stripped_exp_date = exp_date.split(':')[0]
        call_key = stripped_call_dates.get(stripped_exp_date)
        put_key = stripped_put_dates.get(stripped_exp_date)

        if call_key and put_key:
            print(
                f"\nExpiration Date: {call_key} (Days to Expiration: {call_exp_map[call_key][list(call_exp_map[call_key].keys())[0]][0]['daysToExpiration']})")

            # Get the common strikes available in both calls and puts
            strikes = sorted(set(call_exp_map[call_key].keys()) & set(put_exp_map[put_key].keys()), key=float)

            # Limit the number of strikes if required
            if num_strikes:
                strikes = strikes[:int(num_strikes)]

            for strike in strikes:
                if strike in call_exp_map[call_key] and strike in put_exp_map[put_key]:
                    call_option = call_exp_map[call_key][strike][0]
                    put_option = put_exp_map[put_key][strike][0]

                    print(f"Strike Price: {strike}")
                    print(
                        f"Call: Bid = {call_option['bid']}, Ask = {call_option['ask']}, Volume = {call_option.get('totalVolume', 0)}, Open Interest = {call_option['openInterest']}, IV = {call_option['volatility']}, Delta = {call_option['delta']}, Theta = {call_option['theta']}")
                    print(
                        f"Put:  Bid = {put_option['bid']}, Ask = {put_option['ask']}, Volume = {put_option.get('totalVolume', 0)}, Open Interest = {put_option['openInterest']}, IV = {put_option['volatility']}, Delta = {put_option['delta']}, Theta = {put_option['theta']}")
                    print("--------------------------------------------------")
                else:
                    print(f"Strike {strike} is missing in one of the options maps (calls or puts). Skipping.")
        else:
            print(f"\nNo options found for the specified expiration date: {exp_date}.")


def print_expiration_summary(options_chain):
    call_exp_map = options_chain.get('callExpDateMap', {})
    put_exp_map = options_chain.get('putExpDateMap', {})

    print("Summary of Expiration Dates:")

    # Ensure there are call expirations to avoid errors
    if not call_exp_map:
        print("No call expiration dates available.")
        return

    for exp_date in call_exp_map.keys():
        num_strikes = len(call_exp_map[exp_date])
        days_to_exp = list(call_exp_map[exp_date].values())[0][0].get('daysToExpiration', 'N/A')
        print(f"Expiration Date: {exp_date} (Days to Expiration: {days_to_exp}), Number of Strikes: {num_strikes}")
    print("--------------------------------------------------")


def print_iv_extremes(options_chain, exp_dates=None):
    call_exp_map = options_chain.get('callExpDateMap', {})
    put_exp_map = options_chain.get('putExpDateMap', {})

    # Default to all available expiration dates if none are provided
    if exp_dates is None:
        exp_dates = list(call_exp_map.keys())

    for exp_date in exp_dates:
        call_key = call_exp_map.get(exp_date)
        if call_key:
            ivs = [(strike, call_option[0]['volatility']) for strike, call_option in call_key.items() if call_option]

            if ivs:
                highest_iv = max(ivs, key=lambda x: x[1])
                lowest_iv = min(ivs, key=lambda x: x[1])

                print(f"Expiration Date: {exp_date}")
                print(f"  Highest IV: Strike = {highest_iv[0]}, IV = {highest_iv[1]}")
                print(f"  Lowest IV: Strike = {lowest_iv[0]}, IV = {lowest_iv[1]}")
                print("--------------------------------------------------")
            else:
                print(f"No strikes found for expiration date: {exp_date}")


def print_volume_oi_heatmap(options_chain, exp_dates=None):
    call_exp_map = options_chain.get('callExpDateMap', {})
    put_exp_map = options_chain.get('putExpDateMap', {})

    # Default to all available expiration dates if none are provided
    if exp_dates is None:
        exp_dates = list(call_exp_map.keys())

    for exp_date in exp_dates:
        call_key = call_exp_map.get(exp_date)
        put_key = put_exp_map.get(exp_date)

        if call_key and put_key:
            print(f"Expiration Date: {exp_date}")
            print("Strike Price | Call Volume | Put Volume | Call Open Interest | Put Open Interest")
            for strike in call_key.keys():
                if strike in put_key:
                    call_option = call_key[strike][0]
                    put_option = put_key[strike][0]

                    print(f"{strike} | {call_option.get('totalVolume', 0)} | {put_option.get('totalVolume', 0)} "
                          f"| {call_option['openInterest']} | {put_option['openInterest']}")
            print("--------------------------------------------------")
        else:
            print(f"No options found for the expiration date: {exp_date}.")


def print_delta_theta_analysis(options_chain, exp_dates=None):
    call_exp_map = options_chain.get('callExpDateMap', {})
    put_exp_map = options_chain.get('putExpDateMap', {})

    # Default to all available expiration dates if none are provided
    if exp_dates is None:
        exp_dates = list(call_exp_map.keys())

    for exp_date in exp_dates:
        call_key = call_exp_map.get(exp_date)
        put_key = put_exp_map.get(exp_date)

        if call_key and put_key:
            deltas = []
            thetas = []
            for strike in call_key.keys():
                if strike in put_key:
                    call_option = call_key[strike][0]
                    deltas.append((strike, call_option['delta']))
                    thetas.append((strike, call_option['theta']))

            if deltas and thetas:
                highest_delta = max(deltas, key=lambda x: x[1])
                lowest_delta = min(deltas, key=lambda x: x[1])
                highest_theta = max(thetas, key=lambda x: x[1])
                lowest_theta = min(thetas, key=lambda x: x[1])

                print(f"Expiration Date: {exp_date}")
                print(f"  Highest Delta: Strike = {highest_delta[0]}, Delta = {highest_delta[1]}")
                print(f"  Lowest Delta: Strike = {lowest_delta[0]}, Delta = {lowest_delta[1]}")
                print(f"  Highest Theta: Strike = {highest_theta[0]}, Theta = {highest_theta[1]}")
                print(f"  Lowest Theta: Strike = {lowest_theta[0]}, Theta = {lowest_theta[1]}")
                print("--------------------------------------------------")


def print_itm_otm_analysis(options_chain, exp_dates=None, underlying_price=None):
    call_exp_map = options_chain.get('callExpDateMap', {})
    put_exp_map = options_chain.get('putExpDateMap', {})

    # Default to all available expiration dates if none are provided
    if exp_dates is None:
        exp_dates = list(call_exp_map.keys())

    for exp_date in exp_dates:
        call_key = call_exp_map.get(exp_date)
        put_key = put_exp_map.get(exp_date)

        if call_key and put_key:
            print(f"Expiration Date: {exp_date}")
            print("In-the-Money (ITM) Options:")
            for strike in call_key.keys():
                if float(strike) < underlying_price:
                    print(f"  Call Strike: {strike} is ITM")

            print("Out-of-the-Money (OTM) Options:")
            for strike in call_key.keys():
                if float(strike) > underlying_price:
                    print(f"  Call Strike: {strike} is OTM")
            print("--------------------------------------------------")


def get_expiration_chain(client, symbol):
    return client.option_expiration_chain(symbol).json()

def get_price_history(client, symbol, periodType, period=None, frequencyType=None, frequency=None):
    """

    periodType: The time span for the data, such as day, month, year.
    frequencyType: The frequency of the data points, such as daily, weekly, monthly.

    """

    return client.price_history(symbol, periodType, period, frequencyType, frequency).json()


def convert_timestamp(timestamp):
    return datetime.datetime.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%d')


# Function to print the data in a single line per day
def print_price_history(candle_data):
    print("Date and Time       | Open  | High  | Low   | Close | Volume")
    print("--------------------|-------|-------|-------|-------|----------")
    for candle in candle_data['candles']:
        dt = datetime.utcfromtimestamp(candle['datetime'] / 1000)
        formatted_date_time = dt.strftime('%Y-%m-%d %H:%M:%S')
        print(f"{formatted_date_time} | {candle['open']:5.2f} | {candle['high']:5.2f} | "
              f"{candle['low']:5.2f} | {candle['close']:5.2f} | {candle['volume']:10d}")


# Function to save the candles data to a CSV file
def save_price_history(data, filename='candles_data.csv'):
    # Define the CSV file headers
    headers = ['datetime', 'open', 'high', 'low', 'close', 'volume']

    # Open the CSV file for writing
    with open(filename, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=headers)

        # Write the header row
        writer.writeheader()

        # Write the candle data
        for candle in data['candles']:
            writer.writerow({
                'datetime': candle['datetime'],
                'open': candle['open'],
                'high': candle['high'],
                'low': candle['low'],
                'close': candle['close'],
                'volume': candle['volume']
            })

    print(f"Data has been saved to {filename}")

def plot_candlestick_data(data):
    # Convert the data to a pandas DataFrame
    df = pd.DataFrame(data['candles'])

    # Convert the 'datetime' from milliseconds since epoch to a readable date-time format
    df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')

    # Set the datetime as the index for the DataFrame
    df.set_index('datetime', inplace=True)

    # Ensure the columns are correctly named for mplfinance
    df.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume'},
              inplace=True)

    # Plot the candlestick chart using mplfinance
    mpf.plot(df, type='candle', style='charles', title='Candlestick Plot', ylabel='Price', volume=True,
             ylabel_lower='Volume', datetime_format='%Y-%m-%d %H:%M:%S')

    # Show the plot
    plt.show()

def get_movers(client, index, sort=None):
    """
    :param client
    :param index: $DJI, $COMPX, $SPX, NYSE, NASDAQ, OTCBB, INDEX_ALL, EQUITY_ALL, OPTION_ALL, OPTION_PUT, OPTION_CALL
    :sort: VOLUME, TRADES, PERCENT_CHANGE_UP, PERCENT_CHANGE_DOWN
    """
    return client.movers(index, sort).json()

def print_market_movers(market_data):
    # Extract the screeners list from the provided data
    screeners = market_data.get('screeners', [])

    # Print header for better readability
    print(f"{'Symbol':<10}{'Description':<30}{'Last Price':<12}{'Net Change':<12}{'Net % Change':<14}{'Volume':<15}{'Market Share (%)':<20}{'Trades':<10}")

    # Print a line to separate the header from the data
    print("=" * 115)

    # Iterate through each screener in the list and print the relevant information
    for screener in screeners:
        symbol = screener.get('symbol', 'N/A')
        description = screener.get('description', 'N/A')
        last_price = screener.get('lastPrice', 'N/A')
        net_change = screener.get('netChange', 'N/A')
        net_percent_change = screener.get('netPercentChange', 'N/A')
        volume = screener.get('volume', 'N/A')
        market_share = screener.get('marketShare', 'N/A')
        trades = screener.get('trades', 'N/A')

        print(f"{symbol:<10}{description:<30}{last_price:<12.2f}{net_change:<12.2f}{net_percent_change:<14.2f}{volume:<15}{market_share:<20.2f}{trades:<10}")

def get_fundamental_info(client, symbol):
    return client.instruments(symbol, "fundamental").json()


def print_fundamental_info(data):
    # Extract the fundamental information from the data
    instruments = data.get('instruments', [])

    if not instruments:
        print("No fundamental information available.")
        return

    for instrument in instruments:
        fundamental = instrument.get('fundamental', {})

        # Extract values with a default value of 'N/A' if not found
        symbol = fundamental.get('symbol', 'N/A')
        description = instrument.get('description', 'N/A')
        exchange = instrument.get('exchange', 'N/A')
        high52 = fundamental.get('high52', 'N/A')
        low52 = fundamental.get('low52', 'N/A')
        dividend_amount = fundamental.get('dividendAmount', 'N/A')
        dividend_yield = fundamental.get('dividendYield', 'N/A')
        dividend_date = fundamental.get('dividendDate', 'N/A')
        pe_ratio = fundamental.get('peRatio', 'N/A')
        peg_ratio = fundamental.get('pegRatio', 'N/A')
        pb_ratio = fundamental.get('pbRatio', 'N/A')
        pr_ratio = fundamental.get('prRatio', 'N/A')
        pcf_ratio = fundamental.get('pcfRatio', 'N/A')
        gross_margin_ttm = fundamental.get('grossMarginTTM', 'N/A')
        gross_margin_mrq = fundamental.get('grossMarginMRQ', 'N/A')
        net_profit_margin_ttm = fundamental.get('netProfitMarginTTM', 'N/A')
        net_profit_margin_mrq = fundamental.get('netProfitMarginMRQ', 'N/A')
        operating_margin_ttm = fundamental.get('operatingMarginTTM', 'N/A')
        operating_margin_mrq = fundamental.get('operatingMarginMRQ', 'N/A')
        return_on_equity = fundamental.get('returnOnEquity', 'N/A')
        return_on_assets = fundamental.get('returnOnAssets', 'N/A')
        return_on_investment = fundamental.get('returnOnInvestment', 'N/A')
        quick_ratio = fundamental.get('quickRatio', 'N/A')
        current_ratio = fundamental.get('currentRatio', 'N/A')
        interest_coverage = fundamental.get('interestCoverage', 'N/A')
        total_debt_to_capital = fundamental.get('totalDebtToCapital', 'N/A')
        lt_debt_to_equity = fundamental.get('ltDebtToEquity', 'N/A')
        total_debt_to_equity = fundamental.get('totalDebtToEquity', 'N/A')
        eps_ttm = fundamental.get('epsTTM', 'N/A')
        eps_change_percent_ttm = fundamental.get('epsChangePercentTTM', 'N/A')
        shares_outstanding = fundamental.get('sharesOutstanding', 'N/A')
        market_cap = fundamental.get('marketCap', 'N/A')
        book_value_per_share = fundamental.get('bookValuePerShare', 'N/A')
        beta = fundamental.get('beta', 'N/A')
        avg10_days_volume = fundamental.get('avg10DaysVolume', 'N/A')
        avg3_month_volume = fundamental.get('avg3MonthVolume', 'N/A')
        declaration_date = fundamental.get('declarationDate', 'N/A')
        next_dividend_date = fundamental.get('nextDividendDate', 'N/A')
        next_dividend_pay_date = fundamental.get('nextDividendPayDate', 'N/A')

        # Print the information in a formatted manner
        print(f"Fundamental Information for {description} ({symbol})")
        print(f"Exchange: {exchange}")
        print(f"------------------------------------------")
        print(f"52-Week High: {high52}")
        print(f"52-Week Low: {low52}")
        print(f"Dividend Amount: {dividend_amount}")
        print(f"Dividend Yield: {dividend_yield}%")
        print(f"Dividend Date: {dividend_date}")
        print(f"PE Ratio: {pe_ratio}")
        print(f"PEG Ratio: {peg_ratio}")
        print(f"PB Ratio: {pb_ratio}")
        print(f"PR Ratio: {pr_ratio}")
        print(f"PCF Ratio: {pcf_ratio}")
        print(f"Gross Margin (TTM): {gross_margin_ttm}%")
        print(f"Gross Margin (MRQ): {gross_margin_mrq}%")
        print(f"Net Profit Margin (TTM): {net_profit_margin_ttm}%")
        print(f"Net Profit Margin (MRQ): {net_profit_margin_mrq}%")
        print(f"Operating Margin (TTM): {operating_margin_ttm}%")
        print(f"Operating Margin (MRQ): {operating_margin_mrq}%")
        print(f"Return on Equity: {return_on_equity}%")
        print(f"Return on Assets: {return_on_assets}%")
        print(f"Return on Investment: {return_on_investment}%")
        print(f"Quick Ratio: {quick_ratio}")
        print(f"Current Ratio: {current_ratio}")
        print(f"Interest Coverage: {interest_coverage}")
        print(f"Total Debt to Capital: {total_debt_to_capital}%")
        print(f"Long-Term Debt to Equity: {lt_debt_to_equity}%")
        print(f"Total Debt to Equity: {total_debt_to_equity}%")
        print(f"EPS (TTM): {eps_ttm}")
        print(f"EPS Change Percent (TTM): {eps_change_percent_ttm}%")
        print(f"Shares Outstanding: {shares_outstanding}")
        print(f"Market Cap: {market_cap}")
        print(f"Book Value per Share: {book_value_per_share}")
        print(f"Beta: {beta}")
        print(f"Average 10 Days Volume: {avg10_days_volume}")
        print(f"Average 3 Months Volume: {avg3_month_volume}")
        print(f"Declaration Date: {declaration_date}")
        print(f"Next Dividend Date: {next_dividend_date}")
        print(f"Next Dividend Pay Date: {next_dividend_pay_date}")
        print(f"------------------------------------------\n")

def get_market_hours(client, market_list, date=None):
    """

    :param client:
    :param market_list: list of markets to get hours for - equity, option, bond, future, forex
    :param date: date to get hours for in YYYY-MM-DD format.  Defaults to current day if not entered.
    :return: market hours for the specified markets on the specified date in json format
    """
    # make a comma separated string of market_list
    markets = ','.join(market_list)

    return client.market_hours(markets, date).json()

def print_market_hours(market_data):

    for category, products in market_data.items():
        print(f"Category: {category.upper()}")
        print("-" * 50)
        for product_code, details in products.items():
            print(f"Product Code: {product_code}")
            print(f"Date: {details['date']}")
            print(f"Market Type: {details['marketType']}")
            print(f"Product Name: {details['productName']}")
            print(f"Is Open: {details['isOpen']}")

            print("Session Hours:")
            for session, times in details['sessionHours'].items():
                print(f"  {session.capitalize()}:")
                for time in times:
                    print(f"    Start: {time['start']}")
                    print(f"    End: {time['end']}")
            print("-" * 50)
        print("=" * 50)

def start_equity_stream(client, symbol_list=None, field_list = None, handler=None):
    stream_name = client.stream
    if handler is None:
        stream_name.start()
    else:
        stream_name.start(handler)

    if symbol_list is not None:
        # turn sybmol list into a comma separated string
        symbols = ','.join(symbol_list)
    else:
        symbols = 'SPY'  # default to SPY

    if field_list is not None:
        fields = ','.join(map(str, field_list))
    else:
        fields = "0, 3"   # default to symbol and last price

    stream_name.send(stream_name.level_one_equities(symbols, fields))

    return stream_name

def start_futures_stream(client, symbol_list=None, field_list = None, handler=None):
    stream_name = client.stream
    if handler is None:
        stream_name.start()
    else:
        stream_name.start(handler)

    if symbol_list is not None:
        # turn sybmol list into a comma separated string
        symbols = ','.join(symbol_list)
    else:
        symbols = '/ES'  # default to /ES

    if field_list is not None:
        fields = ','.join(map(str, field_list))
    else:
        fields = "0, 4"   # default to symbol and last price

    stream_name.send(stream_name.level_one_futures(symbols, fields))

    return stream_name

def start_options_stream(client, option_list, field_list = None, handler=None):
    stream_name = client.stream
    if handler is None:
        stream_name.start()
    else:
        stream_name.start(handler)

    if option_list is not None:
        # turn option list into a comma separated string
        symbols = ','.join(option_list)

    if field_list is not None:
        fields = ','.join(map(str, field_list))
    else:
        fields = "0, 4"   # default to symbol and last price

    stream_name.send(stream_name.level_one_options(symbols, fields))

    return stream_name

def add_to_stream(stream_name, symbol_list, field_list=None, stream_type='equities'):

    if field_list is not None:
        fields = ','.join(map(str, field_list))
    else:
        if stream_type == 'equities':
            fields = "0, 3"     # default to symbol and last price
        elif stream_type == 'futures' or stream_type == 'options':
            fields = "0, 4"  # default to symbol and last price
        elif stream_type == 'chart_equity':
            fields = "0, 1, 2, 3, 4, 5, 6, 7, 8"

    symbols = ','.join(symbol_list)

    if stream_type == 'equities':
        stream_name.send(stream_name.level_one_equities(symbols, fields, command="ADD"))
    elif stream_type == 'futures':
        stream_name.send(stream_name.level_one_futures(symbols, fields, command="ADD"))
    elif stream_type == 'options':
        stream_name.send(stream_name.level_one_options(symbols, fields, command="ADD"))
    elif stream_type == 'chart_equity':
        stream_name.send(stream_name.chart_equity(symbols, fields, command="ADD"))
    else:
        print("Invalid stream type")

def substitute_stream(stream_name, symbol_list, field_list=None, stream_type='equities'):

    if field_list is not None:
        fields = ','.join(map(str, field_list))
    else:
        if stream_type == 'equities':
            fields = "0, 3"  # default to symbol and last price
        elif stream_type == 'futures' or stream_type == 'options':
            fields = "0, 4"  # default to symbol and last price
        elif stream_type == 'chart_equity':
            fields = "0, 1, 2, 3, 4, 5, 6, 7, 8"

    symbols = ','.join(symbol_list)

    if stream_type == 'equities':
        stream_name.send(stream_name.level_one_equities(symbols, fields, command="SUBS"))
    elif stream_type == 'futures':
        stream_name.send(stream_name.level_one_futures(symbols, fields, command="SUBS"))
    elif stream_type == 'options':
        stream_name.send(stream_name.level_one_options(symbols, fields, command="SUBS"))
    elif stream_type == 'chart_equity':
        stream_name.send(stream_name.chart_equity(symbols, fields, command="SUBS"))
    else:
        print("Invalid stream type")

def start_chart_equity_stream(client, symbol_list, field_list=[0,1,2,3,4,5,6,7,8], handler=None):
    stream_name = client.stream
    if handler is None:
        stream_name.start()
    else:
        stream_name.start(handler)

    # turn symbol list into a comma separated string
    symbols = ','.join(symbol_list)

    fields = ','.join(map(str, field_list))

    stream_name.send(stream_name.chart_equity(symbols, fields))

    return stream_name

def stop_stream(stream_name, clear_subscriptions=True):

    if clear_subscriptions:
        stream_name.stop()
    else:
        stream_name.stop(clear_subscriptions=False)











