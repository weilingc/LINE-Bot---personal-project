# 引用套件
from google.cloud import storage

# 建立客戶端
storage_client = storage.Client()

#指定桶子的名字
bucket_name="homework-user-info"

#指定物件的名字
blob_name="cxcxc.txt"

# 建立bucket客戶端
bucket = storage_client.bucket(bucket_name)

# 建立物件的客戶
blob = bucket.blob(blob_name)

# 請刪除物件
blob.delete()