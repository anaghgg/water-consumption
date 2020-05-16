#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 15 16:44:46 2020

@author: anagh
"""
import pandas as pd
from sklearn.ensemble import RandomForestRegressor



class Future:
    def getPredictions(self,df):

        df=df.tail(25)
        df['amt']=df['amt'].astype(int)

        try:
            monthList=[]
            x=list(df['month'])
            for item in x:
                sp=item.split("-")
                it=int(sp[1])
                monthList.append(it)

            d=pd.DataFrame(list(zip(monthList,list(df['amt']))))
            d.columns=['Month','Amount']
            xTrain=d.iloc[:,0]
            yTrain=d.iloc[:,1]

            
            df['month']=pd.to_datetime(df['month'],infer_datetime_format=True)
            start=list(df['month'])
            
            y=str(start[len(start)-1])
            y=y.split(" ")[0]
            dnew=pd.date_range(y,periods=2,freq='M')
            dnew=dnew[1:]
            month=""
            listTest=[]
            for item in dnew:
                item=str(item)
                item=item.split("-")
                m=int(item[1])
                month=item[0]+"-"+item[1]
                listTest.append(m)
            
            dTest=pd.DataFrame(listTest)
            dTest.columns=['Month']
            xTest=dTest.iloc[:,0]

            x=[]
            for item in xTrain:
                it=[]
                it.append(item)
                x.append(it)
                
            y=[]
            for item in yTrain:
                it=[]
                it.append(item)
                y.append(it)
                
            reg=RandomForestRegressor(n_estimators=100,random_state=0)
            reg.fit(x,y)
            
            xt=[]
            for item in xTest:
                it=[]
                it.append(item)
                xt.append(it)
                

            ypred=reg.predict(xt)
            pred=str(int(ypred[0]))
            
            ans=[]
            ans.append(month)
            ans.append(pred)
            return ans
        except:
            return None
            

        
