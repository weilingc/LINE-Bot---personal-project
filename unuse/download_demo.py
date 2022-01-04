# 引用套件
from google.cloud import storage

# 建立客戶端
storage_client = storage.Client()

# 指定桶子名
bucket_name="homework-user-info"

# 告知遠端物件的名字
source_blob_name="cxcxc.txt"

# 下載回本地端的名字
destination_file_name="cxcxc-ai.txt"

# 建立bucket 客戶端
bucket = storage_client.bucket(bucket_name)

# 建立遠端物件的客戶端
blob = bucket.blob(source_blob_name)

# 下載回本地端
blob.download_to_filename(destination_file_name)