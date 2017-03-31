# -*- coding: utf-8 -*-
"""
Created on Fri Dec 18 21:51:41 2015

@author: SW274998
"""
from nsepy.commons import *
import ast
import json
from bs4 import BeautifulSoup
from nsepy.liveurls import *



def get_quote(symbol, series='EQ', instrument=None, expiry=None, option_type=None, strike=None):
    """
    1. Underlying security (stock symbol or index name)
    2. instrument (FUTSTK, OPTSTK, FUTIDX, OPTIDX)
    3. expiry (ddMMMyyyy)
    4. type (CE/PE for options, - for futures
    5. strike (strike price upto two decimal places
    """
    if instrument == 'FUTSTK' or instrument == 'FUTIDX':
        expiry_str = expiry.strftime("%d%b%Y").upper()
        res = quote_derivative_url(symbol, instrument, expiry_str, option_type, strike)
    else:
        res = quote_eq_url(symbol.replace("&", "%26"), series)

    return json.loads(res.text)['data'][0]


def get_option_chain(symbol, series='EQ', instrument=None, expiry=None):
    """
    1. Underlying security (stock symbol or index name)
    2. instrument (OPTSTK, OPTIDX)
    3. expiry (ddMMMyyyy)
    """
    OPTION_SCHEMA = [str, int, int, int, float, float, float,
                    int, float, float, int, float,
                    int, float, float, int, float,
                    float, float, int, int, int, str]
    OPTION_HEADERS = ['Chart', 'OI CE', 'Chng in OI CE', 'Volume CE', 'IV CE',
                  'LTP CE', 'Net Chng CE', 'Bid Qty CE', 'Bid Price CE',
                  'Ask Price CE', 'Ask Qty CE', 'Strike Price', 'Bid Qty PE', 'Bid Price PE',
                  'Ask Price PE', 'Ask Qty PE', 'Net Chng PE', 'LTP PE', 'IV PE',
                  'Volume PE', 'Chng in OI PE', 'OI PE', 'Chart PE']
    if instrument == 'OPTSTK' or instrument == 'OPTIDX':
        res = option_chain_url(symbol.replace("&", "%26"), instrument, expiry.strftime("%-d%b%Y").upper())
        bs = BeautifulSoup(res.text, 'html.parser')
        tp = ParseTables(soup=bs,
                     schema=OPTION_SCHEMA,
                     headers=OPTION_HEADERS, index="Strike Price")
        df = tp.get_df()
        return df.drop(['Chart', 'Chart PE'], axis=1)



def get_index_quote(symbol):
    res = quote_index_url()
    data = json.loads(res.text)['data']
    if symbol == 'NIFTY':
        return data[1]
    elif symbol == 'BANKNIFTY':
        return data[4]
    elif symbol == 'INDIAVIX':
        return data[5]


def get_option_chain_cds(expiry):
    """
    1. expiry (ddMMMyyyy)
    """
    OPTION_SCHEMA = [str, int, int, int, float, float,
                    int, float, float, int, float,
                    int, float, float, int,
                    float, float, int, int, int, str]
    OPTION_HEADERS = ['Chart', 'OI CE', 'Chng in OI CE', 'Volume CE', 'IV CE',
                  'LTP CE', 'Bid Qty CE', 'Bid Price CE',
                  'Ask Price CE', 'Ask Qty CE', 'Strike Price', 'Bid Qty PE', 'Bid Price PE',
                  'Ask Price PE', 'Ask Qty PE', 'LTP PE', 'IV PE',
                  'Volume PE', 'Chng in OI PE', 'OI PE', 'Chart PE']
    res = option_chain_cds_url(expiry.strftime("%-d%b%Y").upper())
    bs = BeautifulSoup(res.text, 'html.parser')
    tp = ParseTables(soup=bs,
                 schema=OPTION_SCHEMA,
                 headers=OPTION_HEADERS, index="Strike Price")
    df = tp.get_df()
    return df.drop(['Chart', 'Chart PE'], axis=1)


def get_fx_spot_reference_rate(symbol):
    bs = BeautifulSoup(quote_fx_reference_rate_url().text, 'html.parser')
    rows = bs.find_all('td')
    if symbol == 'USDINR':
        return float(rows[5].get_text().strip())
    elif symbol == 'GBPINR':
        return float(rows[7].get_text().strip())
    elif symbol == 'EURINR':
        return float(rows[9].get_text().strip())
    elif symbol == 'JPYINR':
        return float(rows[11].get_text().strip())



# q = get_quote(symbol='NIFTY', instrument='FUTIDX', expiry=datetime.date(2017,02,23))
# q = get_option_chain(symbol='SBIN', instrument='OPTSTK', expiry=datetime.date(2017,02,23))
# print(q)
