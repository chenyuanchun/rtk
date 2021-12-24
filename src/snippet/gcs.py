import os
import re

gcloud_config = {
    "proxy": 'http://googleapis-proxy:<port>',
    'credential': 'gserviceaccount.com.json'
}


def init(config=None):
    if config:
        gcloud_config.update(config)
    os.environ['https_proxy'] = gcloud_config['proxy']


def create_storage_client():
    import google.cloud.storage
    return google.cloud.storage.Client.from_service_account_json(gcloud_config['credential'])


def _resolve_gcs_url(url):
    m = re.match('gs://([a-z0-9\-]+)/(.*)', url)
    if not m or len(m.groups()) != 2:
        raise FileNotFoundError(f'URL: {url} is invalid')
    return m.groups()


def list_all(client, bucket_name, prefix):
    bucket = client.bucket(bucket_name)
    if not bucket:
        raise FileExistsError(f'Bucket {bucket} not found')
    return client.list_blobs(bucket_name, prefix=prefix)


def list_files(client, bucket_name, prefix, dir_only=False, recursive=True):
    blobs = list_all(client, bucket_name, prefix)
    if dir_only:
        return [b.name for b in blobs if b.name[-1] == '/']
    else:
        return [b.name for b in blobs]


def download(client, bucket_name: str, file_path: str, to: str):
    bucket = client.bucket(bucket_name)
    if not bucket:
        raise FileExistsError(f'Bucket {bucket} not found')

    blob = bucket.blob(file_path)
    if not blob:
        raise FileNotFoundError(f'File {file_path} not found on GCS')
    with open(to, 'wb') as f:
        blob.download_to_file(f)


def download_url(client, gcs_url, to):
    bucket_name, file_path = _resolve_gcs_url(gcs_url)
    download(client, bucket_name, file_path, to)


if __name__ == '__main__':
    init()
    _client = create_storage_client()
    for _bucket in _client.list_buckets():
        print(_bucket)

