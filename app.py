# 引用flask套件
from flask import Flask, request, abort

# 引用Line套件
from linebot import (
    LineBotApi, WebhookHandler
)

# 驗證消息用的套件
from linebot.exceptions import (
    InvalidSignatureError
)

# Button 設定模板消息，設定其參數細節。 引入按鍵模板
from linebot.models.template import(
    ButtonsTemplate
)

# 引入所需要的消息與模板消息
from linebot.models import (
    MessageEvent, FollowEvent, PostbackEvent, TextMessage, ImageMessage, TextSendMessage, ImageSendMessage, TemplateSendMessage, ButtonsTemplate, ImageCarouselTemplate, ImageCarouselColumn, PostbackAction, DatetimePickerAction
)

#2021.10.30_測試新功能 quickreply
from linebot.models import (
    MessageAction, QuickReply, QuickReplyButton, LocationAction
)

from google.cloud import storage
from google.cloud import firestore

# 圖片下載與上傳專用, json文字處理
import urllib.request
import os
import json

# 建立日誌紀錄設定檔 https://googleapis.dev/python/logging/latest/stdlib-usage.html
import logging
import google.cloud.logging
from google.cloud.logging.handlers import CloudLoggingHandler


# 啟用log的客戶端
client = google.cloud.logging.Client()

# 建立line event log，用來記錄line event
bot_event_handler = CloudLoggingHandler(client,name="homework_bot_event")
bot_event_logger=logging.getLogger('homework_bot_event')
bot_event_logger.setLevel(logging.INFO)
bot_event_logger.addHandler(bot_event_handler)

# 準備app
app = Flask(__name__)

#填入LINE Bot 資訊
line_bot_api = LineBotApi("") # Channel access token
handler = WebhookHandler("")  # Channel secret

# 設定機器人訪問入口, http的入口, 給Line傳消息用的 叫callback
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    print(body)
    # 消息整個交給bot_event_logger，請它傳回GCP
    bot_event_logger.info(body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


# 用戶發出文字消息時， 按條件內容, 回傳文字消息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if(event.message.text.find('訂購旅遊套裝')!= -1):
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="請選擇出發時間。", quick_reply=quick_picktime),
        )
        # TextSendMessage(text="請選擇出發地點", quick_reply=quick_picklocation),
    elif(event.message.text.find('訂購票券')!= -1):
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="功能開發中~。", quick_reply=quick_getback),
        )
    elif(event.message.text.find('聯繫在地嚮導')!= -1):
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="功能開發中~。", quick_reply=quick_getback),
        )
    elif(event.message.text.find('@')!= -1):
        line_bot_api.reply_message(
        event.reply_token,
        template_message_dict.get(event.message.text)
        )
    else:
        line_bot_api.reply_message(
        event.reply_token,
        quick_reply_go2main_send_message,
        )


@handler.add(FollowEvent)
def handle_follow_event(event):
    #取個資
    line_user_profile= line_bot_api.get_profile(event.source.user_id)
    
    # 跟line 取回照片，並放置在本地端 把用戶的大頭照取回本地端
    file_name = line_user_profile.user_id+'.jpg'
    # 下載大頭照
    urllib.request.urlretrieve(line_user_profile.picture_url, file_name)

    # 把用戶的大頭照上傳到cloud storage
    # 建立客戶端
    storage_client = storage.Client()

    #指定桶子名
    bucket_name="homework-user-info"

    #依照用戶的id當資料夾, 大頭照名字為user_pic.png
    destination_blob_name=f"{line_user_profile.user_id}/user_pic.png"
    source_file_name=file_name
        
    # 進行上傳
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)
    
    # 把用戶的資料變成dict, 設定用戶資料json
    user_dict={
        "user_id":line_user_profile.user_id,
        "picture_url": f"https://storage.googleapis.com/{bucket_name}/destination_blob_name",
        "display_name": line_user_profile.display_name,
        "status_message": line_user_profile.status_message
    }

    # 插入firestore, 建立客戶端
    db = firestore.Client()

    # 插入line-user表格, 資料主鍵為user_id
    doc_ref = db.collection(u'line-user').document(user_dict.get("user_id"))

    # 插入整筆資料
    doc_ref.set(user_dict)

    # 請line_bot_api 傳消息回去給用戶
    line_bot_api.reply_message(
        event.reply_token,
        # TextSendMessage(text="您好~這裡是旅行小秘書~請輸入以下指令: @main")),
        TextSendMessage(text='您好~歡迎來到旅行小秘書~到主選單可選擇您喜愛的旅遊套裝', quick_reply=quick_getback)
        )        


# 創建QuickReplyButton
quick_reply=QuickReply(
    items=[
        QuickReplyButton(action=MessageAction(label="旅遊套裝", text="訂購旅遊套裝")),
        QuickReplyButton(action=MessageAction(label="在地導遊", text="聯繫在地嚮導")),
        QuickReplyButton(action=MessageAction(label="訂購票券", text="訂購票券")),
        QuickReplyButton(action=MessageAction(label="回主選單", text="@main")),
        # QuickReplyButton(action=LocationAction(label="到府服務(測試定位功能)")), #單純想玩定位功能
    ]
)

#生成一個快速回主選單的按鈕
quick_getback=QuickReply(
    items=[
        QuickReplyButton(action=MessageAction(label="到主選單", text="@main")),
    ]
)
#生成一個選擇時間的按鈕
quick_picktime=QuickReply(
    items=[
        QuickReplyButton(action=DatetimePickerAction(label="出發時間", mode="date", data="timepicked" ))
    ]
)
#生成一個選擇地點的按鈕
quick_picklocation=QuickReply(
    items=[
        QuickReplyButton(action=LocationAction(label="出發地點"))
    ]
)

# 將quickReplyList 塞入TextSendMessage 中, 變成一個 TextsendMessage物件
quick_reply_text_send_message = TextSendMessage(text='請選擇您要的服務', quick_reply=quick_reply)
quick_reply_go2main_send_message = TextSendMessage(text='需要回主選單嗎?', quick_reply=quick_getback)

#主選單內容 <用戶輸入@main會出現以下選項>
buttons_template_message = TemplateSendMessage(
    alt_text='Buttons template',
    template=ButtonsTemplate(
        thumbnail_image_url="https://p.kindpng.com/picc/s/5-56911_meios-de-transporte-desenho-hd-png-download.png",
        title='請選擇你的喜好',
        text='點擊下方按鈕獲得更多幫助',
        actions=[
            {
                "type": "postback",
                "label": "水上活動",
                "text": "@水上活動",
                "data": "待補"
            },
            {
                "type": "postback",
                "label": "山間探險",
                "text": "@山間探險",
                "data": "待補"
            },
            # {
            #     "type": "postback",
            #     "label": "海景",
            #     "text": "@海景",
            #     "data": "待補"
            # },
            {
                "type": "postback",
                "label": "城市探索",
                "text": "@城市探索",
                "data": "待補"
            },
            {
                "type": "postback",
                "label": "熱門慶典",
                "text": "@熱門慶典",
                "data": "待補"
            },
        ],
    )
)

#城市探索圖文輪播
city_template_message = TemplateSendMessage(
    alt_text='Image Carousel Template',
    template=ImageCarouselTemplate(
        columns=[
            ImageCarouselColumn(
                image_url='https://cdn.tatlerasia.com/asiatatler/i/tw/2020/01/17233319-taipei-101_cover_1920x1282.jpg',
                action=PostbackAction(
                    label='選我',
                    display_text='台北101',
                    data='Data3'
                    )
            ),
            ImageCarouselColumn(
                image_url='https://res2.pubu.tw/news/1777/64961/zVDCpj_xl.jpg',
                action=PostbackAction(
                    label='選我',
                    display_text='三峽老街',
                    data='Data3'
                    )
            ),
            ImageCarouselColumn(
                image_url='https://www.jumpman.tw/wp-content/uploads/2019/12/20191207-DSC07609.jpg',
                action=PostbackAction(
                    label='選我',
                    display_text='板橋林家花園',
                    data='Data3'
                    )
            ),
        ]
    )
)

#水上活動圖文輪播
water_template_message = TemplateSendMessage(
    alt_text='Image Carousel Template',
    template=ImageCarouselTemplate(
        columns=[
            ImageCarouselColumn(
                image_url='https://images.squarespace-cdn.com/content/v1/596d96639f74561878f35d5a/1584340814138-30Q762J18WRBZ9ZOFS8P/long_dong_taiwan_snorkeling_ocean_yilan-e1510249481689.jpg',
                action=PostbackAction(
                    label='選我',
                    display_text='水上活動-浮潛',
                    data='Data3'
                    )
            ),
            ImageCarouselColumn(
                image_url='https://im.marieclaire.com.tw/s805c452h100b0/assets/mc/202007/5F15CF844C9481595264900.jpeg',
                action=PostbackAction(
                    label='選我',
                    display_text='水上活動-獨木舟',
                    data='Data3'
                    )
            ),
            ImageCarouselColumn(
                image_url='https://www.yellowstoneraft.com/wp-content/uploads/2019/09/IMG_7225-1024x683.jpg',
                action=PostbackAction(
                    label='選我',
                    display_text='水上活動-溯溪',
                    data='Data3'
                    )
            ),
        ]
    )
)

#海景圖文輪播
seaview_template_message = TemplateSendMessage(
    alt_text='Image Carousel Template',
    template=ImageCarouselTemplate(
        columns=[
            ImageCarouselColumn(
                image_url='https://halkiseahouse.com/wp-content/uploads/2018/02/3.Veranda-1-Breakfast-2.jpg',
                action=PostbackAction(
                    label='選我',
                    display_text='某地',
                    data='Data3'
                    )
            ),
            ImageCarouselColumn(
                image_url='https://halkiseahouse.com/wp-content/uploads/2018/02/3.Veranda-1-Breakfast-2.jpg',
                action=PostbackAction(
                    label='選我',
                    display_text='某地',
                    data='Data3'
                    )
            ),
        ]
    )
)

#山間探險圖文輪播
hiking_template_message = TemplateSendMessage(
    alt_text='Image Carousel Template',
    template=ImageCarouselTemplate(
        columns=[
            ImageCarouselColumn(
                image_url='https://img.traveltriangle.com/blog/wp-content/tr:w-700,h-400/uploads/2018/09/swiss-alps.jpg',
                action=PostbackAction(
                    label='選我',
                    display_text='某地',
                    data='Data3'
                    )
            ),
            ImageCarouselColumn(
                image_url='https://assetsv4.tripmoment.com/system/redactor_assets/pictures/25133/content_38742ea0-93ae-411f-a549-76c7f79e3302.jpg',
                action=PostbackAction(
                    label='選我',
                    display_text='南投武嶺',
                    data='Data3'
                    )
            ),
            ImageCarouselColumn(
                image_url='https://www.roadaffair.com/wp-content/uploads/2017/12/everest-base-camp-trek-nepal-shutterstock_583073020.jpg',
                action=PostbackAction(
                    label='選我',
                    display_text='美國大峽谷Rim-to-Rim',
                    data='Data3'
                    )
            ),
            ImageCarouselColumn(
                image_url='https://www.roadaffair.com/wp-content/uploads/2017/09/yosemite-national-park-usa-shutterstock_124360591.jpg',
                action=PostbackAction(
                    label='選我',
                    display_text='祕魯約旦',
                    data='Data3'
                    )
            ),         
        ]
    )
)

#熱門慶典圖文輪播
festival_template_message = TemplateSendMessage(
    alt_text='Image Carousel Template',
    template=ImageCarouselTemplate(
        columns=[
            ImageCarouselColumn(
                image_url='https://static3.thetravelimages.com/wordpress/wp-content/uploads/2018/09/Medoc-Via-La-Cit%C3%A9-du-Vin-2.jpg',
                action=PostbackAction(
                    label='選我',
                    display_text='紅酒馬拉松',
                    data='Data3'
                    )
            ),
            ImageCarouselColumn(
                image_url='https://cdn.metropop.com.hk/750/pop/5b867a0eeee7b_08.jpg',
                action=PostbackAction(
                    label='選我',
                    display_text='墨西哥熱氣球節',
                    data='Data3'
                    )
            ),
            ImageCarouselColumn(
                image_url='https://cdn.bella.tw/files/%E5%9B%9B%E6%9C%88.jpeg',
                action=PostbackAction(
                    label='選我',
                    display_text='荷蘭國王節',
                    data='Data3'
                    )
            ),
            ImageCarouselColumn(
                image_url='https://cdn.bella.tw/files/%E5%8D%81%E4%BA%8C%E6%9C%88.jpeg',
                action=PostbackAction(
                    label='選我',
                    display_text='俄羅斯冬日文化節',
                    data='Data3'
                    )
            ),
        ]
    )
)


# 設計一個字典 當用戶輸入相應文字消息時，系統會從此挑揀消息
# 將消息模型，文字收取消息與文字寄發消息 引入
# 根據自定義菜單四張故事線的圖，設定相對應image
template_message_dict = {
  #主選單
  "@main":buttons_template_message,
  
  #喜好活動選單---啟動圖文輪播
  "@城市探索": city_template_message,
  "@水上活動": water_template_message, 
#   "@海景": seaview_template_message,
  "@山間探險": hiking_template_message,
  "@熱門慶典": festival_template_message,
  }


#用戶點擊button後，觸發postback event，對其回傳做相對應處理
@handler.add(PostbackEvent)
def handle_post_message(event):
    user_profile = line_bot_api.get_profile(event.source.user_id)
    if (event.postback.data.find('Data1')== 0):
        with open("user_profile_business.txt", "a") as myfile:
            myfile.write(json.dumps(vars(user_profile),sort_keys=True))
            myfile.write('\n')
            line_bot_api.reply_message(
            event.reply_token,
            TextMessage(text='功能開發中~'),
            quick_reply_go2main_send_message,
            )
    elif (event.postback.data.find('Data2') == 0):
        with open("user_profile_tutorial.txt", "a") as myfile:
            myfile.write(json.dumps(vars(user_profile),sort_keys=True))
            myfile.write('\n')
            line_bot_api.reply_message(
            event.reply_token,
            TextMessage(text='功能開發中~'),
            quick_reply_go2main_send_message,
            )
    elif (event.postback.data.find('Data3') == 0):
        with open("user_profile_tutorial.txt", "a") as myfile:
            myfile.write(json.dumps(vars(user_profile),sort_keys=True))
            myfile.write('\n')
            line_bot_api.reply_message(
            event.reply_token,
            quick_reply_text_send_message
            )
    elif (event.postback.data.find('timepicked') == 0):
        depatime = event.postback.params['date'], #資料待處理好看
        line_bot_api.reply_message(
            event.reply_token,
            TextMessage(text=f'您選擇的出發時間為: {depatime}~ 填寫資料功能開發中~輸入 @main 回主選單'),     
            )
    else:
        pass


# 選擇性追加程式碼
# 2021.11.10測試
# import numpy as np
# from PIL import Image, ImageOps
# import tensorflow.keras
# model = tensorflow.keras.models.load_model('converted_savedmodel/model.savedmodel')


from linebot.models import ImageMessage
@handler.add(MessageEvent, message=ImageMessage)
def handle_image_message(event):
    # 取出照片
    image_blob = line_bot_api.get_message_content(event.message.id)
    temp_file_path=f"""{event.message.id}.png"""

    with open(temp_file_path, 'wb') as fd:
        for chunk in image_blob.iter_content():
            fd.write(chunk)

    # 上傳至cloud storage
    storage_client = storage.Client()
    bucket_name = "homework-user-info"
    destination_blob_name = f'{event.source.user_id}/image/{event.message.id}.png'
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(temp_file_path)
    #2021.11.10新增
    # photo_url = f'https://storage.cloud.google.com/{bucket_name}/{event.source.user_id}/image/{event.message.id}.png'
    # 未來放ai功能
    # 回應用戶
    line_bot_api.reply_message(
        event.reply_token,
        # ImageSendMessage(original_content_url=photo_url, preview_image_url=photo_url), #測試從storage抓用戶傳送的圖片網址~並回傳給用戶#因此網址為非公開 所以無法顯示
        TextSendMessage(f"""圖片已上傳，請期待未來的AI服務！""")
        )

    # # 2021.11.11 追加測試辨識圖片
    # # 載入模型Label
    # '''
    # 載入類別列表
    # '''
    # class_dict = {}
    # with open('converted_savedmodel/labels.txt') as f:
    #     for line in f:
    #         (key, val) = line.split()
    #         class_dict[int(key)] = val

    # # 載入模型
    # # Disable scientific notation for clarity
    # np.set_printoptions(suppress=True)

    # # Load the model
    # # model = tensorflow.keras.models.load_model('converted_savedmodel/model.savedmodel')
    
    # # 圖片預測
    # data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
    # image = Image.open(temp_file_path)
    # size = (224, 224)
    # image = ImageOps.fit(image, size, Image.ANTIALIAS)
    # image_array = np.asarray(image)
    # # Normalize the image
    # normalized_image_array = (image_array.astype(np.float32) / 127.0 - 1 )

    # # Load the image into the array
    # data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
    # data[0]= normalized_image_array[0:224,0:224,0:3]

    # # run the inference
    # prediction = model.predict(data)
    
    # # 取得預測值
    # max_probability_item_index = np.argmax(prediction[0])

    
    # # 將預測值拿去尋找line_message
    # # 並依照該line_message，進行消息回覆
    # if prediction.max() > 0.6:
    #     result_message_array = detect_json_array_to_new_message_array("line_message_json/"+class_dict.get(max_probability_item_index)+".json")
    #     cls.line_bot_api.reply_message(
    #         event.reply_token,
    #         result_message_array
    #     )
    # else:
    #     cls.line_bot_api.reply_message(
    #         event.reply_token,
    #         TextSendMessage(f"""圖片無法辨認，圖片已上傳，請期待未來的AI服務！""")
    #     )
        
    # # 移除本地檔案
    # os.remove(temp_file_path)




# 運行伺服器 自動運行在8080port
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))