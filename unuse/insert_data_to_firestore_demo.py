# 引用套件
from google.cloud import firestore

# 啟動客戶端
db = firestore.Client()

# 指定要操作的資料表，輸入特定資料的key
doc_ref = db.collection(u'cxcxc-user').document(u'Ada2')

# 對那個key，增加資料
doc_ref.set({
     u'first': u'Ada2',
     u'last': u'Lovelace',
     u'born': 1815
})