from storages.backends.s3boto3 import S3Boto3Storage

class StaticStorage(S3Boto3Storage):
    location = 'static/static'  # This forces the 'static/' prefix
    file_overwrite = False

class MediaStorage(S3Boto3Storage):
    location = 'media/media'  # This forces the 'media/' prefix
    file_overwrite = False
    