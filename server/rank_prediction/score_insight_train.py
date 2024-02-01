from transformers import pipeline
from transformers import AutoTokenizer
from transformers import AutoModelForSequenceClassification
from fastapi.responses import JSONResponse
from fastapi import Body, Request

import numpy as np
from scipy import stats
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import math
from sklearn import preprocessing, model_selection, svm
from sklearn.linear_model import LinearRegression
from matplotlib.collections import LineCollection
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import train_test_split

from matplotlib.font_manager import FontManager

matplotlib.rcParams['font.sans-serif'] =  ['Heiti TC']
matplotlib.rcParams['font.serif'] =  ['Heiti TC']
matplotlib.rcParams['axes.unicode_minus'] = False

from sklearn.metrics import mean_squared_error

import time



# 对校考成绩序列做一个加权平均，越后面的成绩权重越大，
def weighted_average_score(score_list):
  score_list = np.array(score_list)
  # 权重按照2的幂次递增，长度为score_list的长度
  weights = np.array([2**i for i in range(len(score_list))])
  # print("weights=",weights)
  # print("score_list=",score_list) 
  # print("score_list * weights=",score_list * weights)
  # print("np.sum(score_list * weights)=",np.sum(score_list * weights))
  return np.sum(score_list * weights) / np.sum(weights)

def score_insight_train(
  school_name: str = Body(..., examples=["双十中学"]),
  data: list = Body([], examples=[
    [
      [
        {
          "高考排名": 50
        },
        {
          "高考排名": 3000
        },
        {
          "高考排名": 21000
        },
        {
          "高考排名": 66000
        },
        {
          "高考排名": 121000
        },
      ],
      [
        {
          "高考排名": 60
        },
        {
          "高考排名": 21000
        },
        {
          "高考排名": 24000
        },
        {
          "高考排名": 121000
        },
      ],
      
      
  ]])
):
  
  data_dfs = []
  
  # 将data下每个dict根据keys转换为df, 并做数据处理
  for i in range(len(data)):
    temp = pd.DataFrame(data[i])
    # 读取高考排名，降序排序，根据降序排序的index，生成新的列"校排名"
    temp["校排名"] = temp["高考排名"].rank(ascending=True)

    # 校排名做min-max归一化，形成新的列“归一化校排名”
    min_max_scaler = preprocessing.MinMaxScaler()
    temp["归一化校排名"] = min_max_scaler.fit_transform(np.array(temp["校排名"]).reshape(-1,1))
    
    data_dfs.append(temp)
    
  # 生成训练数据
  X = []
  y = []

  # 汇总data_dfs下的所有df, 归一化校排名为X，高考排名为y
  for i in range(len(data_dfs)):
    X += list(data_dfs[i]["归一化校排名"])
    y += list(data_dfs[i]["高考排名"])

  # 检查模型维度
  X, y = np.array(X).reshape(-1,1), np.array(y).reshape(-1,1)
  print("X=",X.shape, "y=",y.shape)

  # 把X,y合并成一个dataframe, 形成最终训练数据
  df_train_all = pd.DataFrame(X, columns=['X'])
  df_train_all['y'] = y
  split_data = []
  # 分段训练数据，根据X每0.1分一段, 分成10段
  for i in range(10):
    split_data.append(df_train_all[(df_train_all['X'] >= i * 0.1) & (df_train_all['X'] < (i + 1) * 0.1)])
  # 最终训练的模型
  models =[]
  
  # 分段模型方差
  sigmas = []

  for index, data in enumerate(split_data):
  # 前n-1段数据线性回归拟合
    if index < len(split_data) - 2:
      X=data[['X']].values
      Y=data[['y']].values
      print("X",X.shape, "Y",Y.shape)
      # 划分训练集和测试集
      X_train, X_test, y_train, y_test = train_test_split(X,Y, test_size=0.1)
      # 构建模型
      clf = LinearRegression()
      # 训练模型
      model = clf.fit(X_train,  y_train)
      # 用测试集测试训练结果,返回给定的测试数据的平均正确率
      confidence = clf.score(X_test, y_test)
      print("置信度",confidence, "斜率", model.coef_, "截距", model.intercept_)
      models.append(clf)
      # 模型在预测集上的表现
      y_pred = models[-1].predict(X)
      
      # 计算误差标准差
      sigma = np.sqrt(mean_squared_error(Y, y_pred)) 
      sigmas.append(sigma)
      # 计算95%置信区间
      conf_interval = stats.norm.interval(0.95, loc=y_pred, scale=sigma)
      # 取区间上下限
      lower, upper = conf_interval
      print("标准差",sigma)
      
      err_now=np.sqrt((Y-y_pred)**2).mean()
      print("模型",index,"均方误差",err_now)
      y_pred=y_pred.reshape(len(y_pred),1)
  
    # 最后一段用指数拟合
    else:
      # 最后尾部0.2用多项式拟合
      X=data['X'].values
      Y=data['y'].values
      z1 = np.polyfit(X, Y, 5) # 用3次多项式拟合
      p1 = np.poly1d(z1)
      print(p1) # 在屏幕上打印拟合多项式
      models.append(p1)
      y_pred=models[-1](X)
      y_pred=y_pred.reshape(len(y_pred),1)
      # 平方误差
      err_now=np.sqrt((Y-y_pred)**2).mean()
      print("模型",index,"均方误差",err_now)
      sigma = np.sqrt(mean_squared_error(Y, y_pred)) 
      sigmas.append(sigma)
      X=X.reshape(len(X),1)
      Y=Y.reshape(len(Y),1)
    
  

  # 生成测试数据, 1000个样本
  X = np.linspace(0, 1, 10001).reshape(-1, 1)
  # 将X按照模型分段预测
  y = []
  for i in range(len(models)):
    if i < len(models) - 2:
      y += list(models[i].predict(X[(X >= i*0.1) & (X < (i+1)*0.1)].reshape(-1,1)))
    else:
      y += list(models[i](X[(X >= i*0.1) & (X <= (i+1)*0.1)].reshape(-1,1)))

  y = y[:len(X)]
  
  
  # 根据X生成一个X_sigma, 当X<0.1, sigma为1，当X在0.1和0.2之间,sigma为2，以此类推
  X_sigma = []
  for i in range(len(X)):
    if X[i] < 0.1:
      X_sigma.append(sigmas[0])
    elif X[i] < 0.2:
      X_sigma.append(sigmas[1])
    elif X[i] < 0.3:
      X_sigma.append(sigmas[2])
    elif X[i] < 0.4:
      X_sigma.append(sigmas[3])
    elif X[i] < 0.5:
      X_sigma.append(sigmas[4])
    elif X[i] < 0.6:
      X_sigma.append(sigmas[5])
    elif X[i] < 0.7:
      X_sigma.append(sigmas[6])
    elif X[i] < 0.8:
      X_sigma.append(sigmas[7])
    elif X[i] < 0.9:
      X_sigma.append(sigmas[8])
    else:
      X_sigma.append(sigmas[9])

  # 将X，Y变成一个df, X列叫归一化校排名，Y列叫预测省排名
  df = pd.DataFrame(np.concatenate((X, y), axis=1), columns=['归一化校排名', '预测省排名'])
  print(df)
  
  # 预测省排名变成int
  df['预测省排名'] = df['预测省排名'].astype(int)

  # 预测省排名如果小于0，就等于50, 如果大于50，就加50
  df.loc[df['预测省排名'] > 0, '预测省排名'] = df.loc[df['预测省排名'] > 0, '预测省排名'] + 50
  df.loc[df['预测省排名'] <= 0, '预测省排名'] = 50

  # 将X_sigma并入df, 叫做区间标准差
  df['区间标准差'] = X_sigma
  # 区间标准差变为int
  df['区间标准差'] = df['区间标准差'].astype(int)

  # df新增两列，叫做预测上限和下限，预测上限等于预测省排名减区间标准差，预测下限等于预测省排名加区间标准差
  df['预测省排名95区间上限'] = df['预测省排名'] - df['区间标准差'] * 1.96
  df['预测省排名95区间下限'] = df['预测省排名'] + df['区间标准差'] * 1.96

  df['预测省排名99区间上限'] = df['预测省排名'] - df['区间标准差'] * 2.58
  df['预测省排名99区间下限'] = df['预测省排名'] + df['区间标准差'] * 2.58

  # 上下限变int
  df['预测省排名95区间上限'] = df['预测省排名95区间上限'].astype(int)
  df['预测省排名95区间下限'] = df['预测省排名95区间下限'].astype(int)
  df['预测省排名99区间上限'] = df['预测省排名99区间上限'].astype(int)
  df['预测省排名99区间下限'] = df['预测省排名99区间下限'].astype(int)
  
  
  # 如果预测上限<50, 预测上限=1
  df.loc[df['预测省排名95区间上限'] < 50, '预测省排名95区间上限'] = 1
  df.loc[df['预测省排名99区间上限'] < 50, '预测省排名99区间上限'] = 1
  
  
  df['预测省排名95区间上下限'] = df[['预测省排名95区间上限', '预测省排名95区间下限']].values.tolist()
  df['预测省排名99区间上下限'] = df[['预测省排名99区间上限', '预测省排名99区间下限']].values.tolist()
  
  # 归一化校排名变成百分比,用%表示
  df['归一化校排名'] = df['归一化校排名'].apply(lambda x: '%.2f%%' % (x * 100))
  
  # 删除预测省排名上限1sigma, 预测省排名下限1sigma, 预测省排名上限1.5sigma, 预测省排名下限1.5sigma, 预测省排名上限2sigma, 预测省排名下限2sigma
  df = df.drop(['预测省排名95区间上限',	'预测省排名95区间下限','预测省排名99区间上限','预测省排名99区间下限'], axis=1)

  # 去除归一化校排名重复的行
  df = df.drop_duplicates(subset=['归一化校排名'], keep='first')
  
  
  ret = {
    "model_res": df.to_dict(orient='records')
  }
  
  return JSONResponse(ret)