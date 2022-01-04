# 引用套件
from google.cloud import storage

# 建立跟cloud storage 溝通的客戶端
storage_client = storage.Client()

# 桶子, 物件, 本地檔案事先指定好
bucket_name="homework-user-info"

# 上傳到桶子之後的名字
destination_blob_name="cxcxc.txt"

# 本地要上傳的檔案名
source_file_name="requirements.txt"

# 將本地端的requirements.txt 上傳到 homework-user-info 桶子, 並且檔名改為cxcxc.txt
# 正式上傳檔案至bucket內
bucket = storage_client.bucket(bucket_name)

# 指定桶子內的物件
blob = bucket.blob(destination_blob_name)

# 把本地檔案上傳
blob.upload_from_filename(source_file_name)