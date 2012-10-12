from django.conf import settings
from django.core.files import storage as django_storage
from storages.backends import s3boto

STORAGE_BUCKET_NAME = getattr(settings, 'AWS_STATIC_STORAGE_BUCKET_NAME', getattr(settings, 'AWS_STORAGE_BUCKET_NAME', None))

class VersionedS3BotoStorage(s3boto.S3BotoStorage):
    def __init__(self, *args, **kwargs):
        super(VersionedS3BotoStorage, self).__init__(*args, **kwargs)
        self.bucket_name = STORAGE_BUCKET_NAME

    def url(self, name):
        url = super(VersionedS3BotoStorage, self).url(name)
        return "{}?{}".format(url, settings.COMMIT_SHA[:5])


class VersionedFileSystemStorage(django_storage.FileSystemStorage):
    def url(self, name):
        url = super(VersionedFileSystemStorage, self).url(name)
        return "{}?{}".format(url, settings.COMMIT_SHA[:5])
