# 引用套件
from google.cloud import firestore

# 建立客戶端
db = firestore.Client()

# 指定表格內的資料 並告知直接刪除
db.collection(u'cxcxc-user').document(u'Ada').delete()