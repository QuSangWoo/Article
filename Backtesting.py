# -*- coding: utf-8 -*-
"""
Created on Wed Jun 27 21:06:43 2018

@author: user
"""
import pandas as pd
import numpy as np

#--------------------------Portfolio Return Backtest Function
def ReturnPortfolio(R, weights):
    if R.isnull().values.any() :
        print("NA's detected: filling NA's with zeros")
        R[np.isnan(R)] = 0

    if R.shape[1] != weights.shape[1] :
        print("Columns of Return and Weight is not same")        ## Check The Column Dimension
               
    if R.index[-1] < weights.index[0] + pd.DateOffset(days=1) :
        print("Last date in series occurs before beginning of first rebalancing period")
           
    if R.index[0] < weights.index[0] :
        R = R.loc[R.index >= weights.index[0] + pd.DateOffset(days=1)]   ## Subset the Return object if the first rebalance date is after the first date 
     
    bop_value = pd.DataFrame(data = np.zeros(shape = (R.shape[0], R.shape[1])), index = R.index, columns = [R.columns])
    eop_value = pd.DataFrame(data = np.zeros(shape = (R.shape[0], R.shape[1])), index = R.index, columns = [R.columns])
    bop_weights = pd.DataFrame(data = np.zeros(shape = (R.shape[0], R.shape[1])), index = R.index, columns = [R.columns])
    eop_weights = pd.DataFrame(data = np.zeros(shape = (R.shape[0], R.shape[1])), index = R.index, columns = [R.columns])
    
    bop_value_total = pd.DataFrame(data = np.zeros(shape = R.shape[0]), index = R.index)
    eop_value_total = pd.DataFrame(data = np.zeros(shape = R.shape[0]), index = R.index)
    ret = pd.DataFrame(data = np.zeros(shape = R.shape[0]), index = R.index)
                       
    end_value = 1   # The end_value is the end of period total value from the prior period
    
    k = 0
    
    for i in range(0 , len(weights) -1 ) :
        fm = weights.index[i] + pd.DateOffset(days=1)
        to = weights.index[i + 1]            
        returns = R.loc[fm : to, ]

        jj = 0
        
        for j in range(0 , len(returns) ) :
            if jj == 0 :
                bop_value.iloc[k, :] = (end_value * weights.iloc[i, :].values)
            else :
                bop_value.iloc[k, :] = eop_value.iloc[k-1, :]
            
            bop_value_total.iloc[k] = bop_value.iloc[k, :].sum()
                        
            # Compute end of period values
            eop_value.iloc[k, :] = (1 + returns.iloc[j, :]).values * bop_value.iloc[k, :].values
            eop_value_total.iloc[k] = eop_value.iloc[k, :].sum()
            
            # Compute portfolio returns
            ret.iloc[k] = eop_value_total.iloc[k] / end_value - 1
            end_value = float(eop_value_total.iloc[k])
            
            # Compute BOP and EOP weights
            bop_weights.iloc[k, :] = bop_value.iloc[k, :] / float(bop_value_total.iloc[k])
            eop_weights.iloc[k, :] = eop_value.iloc[k, :] / float(eop_value_total.iloc[k])
    
            jj += 1
            k += 1
    
    result = {'ret' : ret, 'bop_weights' : bop_weights, 'eop_weights' : eop_weights}
    return(result)

#--- Calculate Cumulative Return ---#
def ReturnCumulative(R) :
    R[np.isnan(R)] = 0
    
    temp = (1+R).cumprod()-1
    print("Total Return: ", round(temp.iloc[-1, :], 4)) 
    return(temp)


#--- Calculate Drawdown ---#
def drawdown(R) :
    dd = pd.DataFrame(data = np.zeros(shape = (R.shape[0], R.shape[1])), index = R.index, columns = [R.columns])
    R[np.isnan(R)] = 0
    
    for j in range(0, R.shape[1]):
        
        if (R.iloc[0, j] > 0) :
            dd.iloc[0, j] = 0
        else :
            dd.iloc[0, j] = R.iloc[0, j]
            
        for i in range(1 , len(R)):
            temp_dd = (1+dd.iloc[i-1, j]) * (1+R.iloc[i, j]) - 1
            if (temp_dd > 0) :
                dd.iloc[i, j] = 0
            else:
                dd.iloc[i, j] = temp_dd
    
    return(dd)

#--- Daily Return Frequency To Yearly Return Frequency ---#
def apply_yearly(R) :
    
    s = pd.Series(np.arange(R.shape[0]), index=R.index)
    ep = s.resample("A").max()
    temp = pd.DataFrame(data = np.zeros(shape = (ep.shape[0], R.shape[1])), index = ep.index.year, columns = [R.columns])

    for i in range(0 , len(ep)) :
        if (i == 0) :
            sub_ret = R.iloc[ 0 : ep[i] + 1, :]
        else :
            sub_ret = R.iloc[ ep[i-1]+1 : ep[i] + 1, :]
        temp.iloc[i, ] = ((1 + sub_ret).prod() - 1).values
    
    return(temp)
