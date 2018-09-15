# -*- coding: utf-8 -*-
"""
Created on Sat Sep 15 12:14:19 2018

@author: user
"""

import pandas as pd
import numpy as np
import statsmodels.formula.api as smf ## For use linear regression model.


def get_stock_data_daily(file_name = r'C:/Users/user/Desktop/수정주가.xlsx'):
    xls = pd.ExcelFile(file_name)
    data = xls.parse(0, header=8, index_col=0)
    data = data.reindex(index = data.index[5:])
    return data

def get_stock_data_monthly(file_name = r'C:/Users/user/Desktop/수정주가 월간.xlsx'):
    xls = pd.ExcelFile(file_name)
    data = xls.parse(0, header=8, index_col=0)
    data = data.reindex(index = data.index[5:])
    return data   
    
adj_stock_data_daily = get_stock_data_daily()
adj_stock_data_monthly = get_stock_data_monthly()


def movingaverage(values, window):
    weights = np.repeat(1.0, window)/ window
    sma = np.convolve(values, weights, 'valid')
    return sma


def get_MA_signal(adj_stock_data_daily, adj_stock_data_monthly):
    daily = adj_stock_data_daily.copy()
    monthly = adj_stock_data_monthly.copy()
    monthly_re = monthly.pct_change()

    MA_signal = [3, 5, 10, 20, 50, 100, 200, 400, 600, 800, 1000]
    
    """ Start Date : 1985년 1월 """
    import datetime as dt
    from dateutil.relativedelta import relativedelta
    start_point = monthly.index[np.unique(monthly.index) == dt.datetime(1985, 1, 31)]
    ## 시작점의 위치를 기준으로 매달 MA_signal 계산하기
    start_point_position = list(monthly.index).index(start_point)
    ### 1985년 1월 31일부터 ~~ 끝까지 월별 인덱스 --> rebalancing_date
    rebalancing_date = list(monthly.index[start_point_position : -1])
    
    stock_beta_dic1 = {}
    stock_beta_dic2 = {}
    from collections import defaultdict
    stock_beta = defaultdict(list)
    for i in rebalancing_date:
        print(i)
        k = i - relativedelta(years=5)
        closing_price = daily.loc[k:i]
        aaa = closing_price.dropna(axis=1)  ### NaN 종목 제거
        stock_list = aaa.columns
        
        index_ = rebalancing_date.index(i)+1
        
        re = pd.DataFrame()
        for j in MA_signal:
            A = aaa.rolling(window = j).mean().loc[i]
            re = re.append(pd.DataFrame(A).T)
            norm_A = re/aaa.loc[i]
            
            """ To predict the monthly expected stock returns cross-sectionally,
            we use a two-step procedure. In the frist step, we run in each month t
            a cross-section regression of stock returns on observed normalized MA signals
            to obtian time series of the coefficients on the signals
            """
            
        for p in stock_list:
            df = pd.DataFrame()
            s = pd.DataFrame()
            stock_regression = norm_A[p]
                
            ### i+1 시점의 return이 필요하므로
            ret = monthly_re.loc[rebalancing_date[index_]][p]   
            ## To get monthly index data
            to_ind = pd.DataFrame(monthly_re.loc[rebalancing_date[index_]].T)
            df['y'] = [ret]
            df['b1'] = stock_regression.iloc[0]
            df['b2'] = stock_regression.iloc[1]
            df['b3'] = stock_regression.iloc[2]
            df['b4'] = stock_regression.iloc[3]
            df['b5'] = stock_regression.iloc[4]
            df['b6'] = stock_regression.iloc[5]
            df['b7'] = stock_regression.iloc[6]
            df['b8'] = stock_regression.iloc[7]
            df['b9'] = stock_regression.iloc[8]
            df['b10'] = stock_regression.iloc[9]
            df['b11'] = stock_regression.iloc[10]
            df.index = to_ind.columns
            lm=smf.ols(formula= 'y ~ b1+b2+b3+b4+b5+b6+b7+b8+b9+b10+b11', data=df).fit()
                
            s = s.append(pd.DataFrame(lm.params, columns = to_ind.columns).T)
        
            stock_beta[p].append(s)


                """ In the second step by Haugen and Baker,
                we estimate the expected return for month t+1 from below equation"""
                
                    
