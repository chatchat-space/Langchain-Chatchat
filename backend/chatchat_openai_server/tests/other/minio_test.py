from minio import Minio
from minio.error import S3Error

# Initialize the MinIO client
client = Minio(
    "127.0.0.1:9000",  # Replace with your MinIO server URL
    access_key="minioadmin",  # Replace with your access key
    secret_key="minioadmin",  # Replace with your secret key
    secure=False
)

# Create a bucket if it doesn't already exist
bucket_name = "test-bucket"
if not client.bucket_exists(bucket_name):
    client.make_bucket(bucket_name)
    print(f"Bucket '{bucket_name}' created.")
else:
    print(f"Bucket '{bucket_name}' already exists.")

# Upload a file
file_path = r"D:\job\kaiyuan\Langchain-Chatchat\backend\chatchat_openai_server\app\uploads\znet.yaml"
object_name = "file.txt"
client.fput_object(bucket_name, object_name, file_path)
print(f"File '{file_path}' uploaded as '{object_name}'.")

# List objects in the bucket
objects = client.list_objects(bucket_name)
print("Objects in bucket:")
for obj in objects:
    print(obj.object_name)

# Download a file
download_path = "path/to/download/file.txt"
client.fget_object(bucket_name, object_name, download_path)
print(f"File '{object_name}' downloaded to '{download_path}'.")

# Remove an object
client.remove_object(bucket_name, object_name)
print(f"File '{object_name}' removed from bucket.")
