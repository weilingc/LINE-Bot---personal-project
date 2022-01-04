# 引用套件
from google.cloud import firestore

# 建立資料庫的客戶端
db = firestore.Client()

# 指定要操作的資料 指定表格以及資料主鍵
doc_ref = db.collection(u'cxcxc-user').document(u'Ada2')

# 取得資料
doc = doc_ref.get()

# 若資料存在~打印出來 不存在就說沒有這個資料~
if doc.exists:
    print(f'Document data: {doc.to_dict()}')
else:
    print(u'No such document!')
doc.to_dict()