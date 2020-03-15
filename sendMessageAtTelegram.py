#!/usr/bin/env python
# coding: utf-8

from getInfoFromAPIwithGeo import makeSendMessage
import telegram
from apscheduler.schedulers.blocking import BlockingScheduler   

def sendStockStateMessage():
    lat = 37.513489
    lng = 126.941986
    m = 1000

    bot = telegram.Bot(token="token Value")

    recent_message = []

    get_id_flag = False

    for i in bot.getUpdates():
        if get_id_flag == False:
            recent_message = i.message
        else:
            break
        
    message_user_id = recent_message.chat['id']
    print("user_id : ", message_user_id)
    
    bot.sendMessage(chat_id=message_user_id, text=makeSendMessage(lat, lng, m))

print("Start")
sendStockStateMessage()
sched = BlockingScheduler({'apscheduler.timezone':'UTC'})
sched.add_job(sendStockStateMessage, 'interval', seconds=600)
sched.start()