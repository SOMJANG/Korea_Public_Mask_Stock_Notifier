#!/usr/bin/env python
# coding: utf-8

import requests
import json
from tqdm import tqdm
import pandas as pd


def getNearMaskStoreInfoByGeo(lat, lng, dist):
    url ="https://8oi9s0nnth.apigw.ntruss.com/corona19-masks/v1/storesByGeo/json?lat=" + str(lat) + "&lng=" + str(lng) + "&m=" + str(dist)
    
    req = requests.get(url)
    
    json_data = req.json()
    store_data = json_data['stores']
    
    addrs = []
    codes = []
    latitudes = []
    longitudes = []
    names = []
    types = []
    created_ats = []
    remain_stats = []
    stock_ats = []
    
    for i in tqdm(range(len(store_data))):
        addrs.append(store_data[i]['addr'])
        codes.append(store_data[i]['code'])
        latitudes.append(store_data[i]['lat'])
        longitudes.append(store_data[i]['lng'])
        names.append(store_data[i]['name'])
        types.append(store_data[i]['type'])
        try:
            created_ats.append(store_data[i]['created_at'])
        except:
            created_ats.append("no_data")
        try:
            remain_stats.append(store_data[i]['remain_stat'])
        except:
            remain_stats.append("no_data")
        try:
            stock_ats.append(store_data[i]['stock_at'])
        except:
            stock_ats.append("no_data")
    
    mask_store_info_df = pd.DataFrame({"addr":addrs, "code":codes, "latitude":latitudes, "longitude":longitudes, "name":names, "type":types, "created_at":created_ats, "remain_stat":remain_stats, "stock_at":stock_ats})
    
    return mask_store_info_df


def getNoneEmptyStockStore(mask_store_info_by_geo):
    data_df = mask_store_info_by_geo.loc[:, ['name', 'addr', 'remain_stat', 'stock_at', 'created_at']]
    data_df_nan = data_df.dropna()
    data_df_nan = data_df_nan[data_df_nan['remain_stat'] != 'break']
    data_df_nan = data_df_nan[data_df_nan['remain_stat'] != 'empty']
    data_df_nan = data_df_nan[data_df_nan['remain_stat'] != 'no_data']

    data_df_nan = data_df_nan.sort_values(by=['stock_at'], axis=0, ascending=False)

    new_index = []
    for i in range(len(data_df_nan['name'])):
        new_index.append(i)
    data_df_nan.index = new_index
    
    return data_df_nan


def makeMaskStockMessage(mask_stock_info_df):
    
    remain_stat_kor = {'plenty':'100개 이상', 'some':'30개 이상', 'few':'2개이상 30개 미만'}
    
    text = ""
    if len(mask_stock_info_df) == 0:
        text = "주변 1km 반경 내의 공적판매처의 마스크 재고가 모두 소진되었습니다"
    else:
        name_list = list(mask_stock_info_df['name'])
        addr_list = list(mask_stock_info_df['addr'])
        remain_list = list(mask_stock_info_df['remain_stat'])
        stock_at_list = list(mask_stock_info_df['stock_at'])
        created_at_list = list(mask_stock_info_df['created_at'])
        
        for i in range(len(mask_stock_info_df['name'])):
            name = name_list[i]
            addr = addr_list[i]
            remain_stat = remain_list[i]
            stock_at = stock_at_list[i]
            created_at = created_at_list[i]
            
            text = text + "판매처명 : " + name + "\n" + "주소 : " + addr + "\n" + "재고상태 : " + remain_stat_kor[remain_stat] + "\n" + "재고 입고 시간 : " + stock_at + "\n" + "데이터 갱신 시간 : " + created_at + "\n" +"\n" 
            
    return text
            



def makeSendMessage(lat, lng, m):
    mask_store_info_by_geo = getNearMaskStoreInfoByGeo(lat, lng, m)
    mask_stock_info_df = getNoneEmptyStockStore(mask_store_info_by_geo)
    sendMessage = makeMaskStockMessage(mask_stock_info_df)
    return sendMessage

