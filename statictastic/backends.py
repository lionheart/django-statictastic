from django.conf import settings
from django.core.files import storage as django_storage
from storages.backends import s3boto

STORAGE_BUCKET_NAME = getattr(settings, 'AWS_STATIC_STORAGE_BUCKET_NAME', getattr(settings, 'AWS_STORAGE_BUCKET_NAME', None))
STATIC_URL = getattr(settings, 'STATIC_URL', getattr(settings, 'MEDIA_URL', None))
STATIC_ROOT = getattr(settings, 'STATIC_ROOT', getattr(settings, 'MEDIA_ROOT', None))

class VersionedS3BotoStorage(s3boto.S3BotoStorage):
    def __init__(self, *args, **kwargs):
        super(VersionedS3BotoStorage, self).__init__(*args, **kwargs)
        self.bucket_name = STORAGE_BUCKET_NAME

    def url(self, name):
        if STATIC_URL is None:
            url = super(VersionedS3BotoStorage, self).url(name)
            return "{}?{}".format(url, settings.COMMIT_SHA)
        else:
            return "{}{}?{}".format(STATIC_URL, name, settings.COMMIT_SHA)


class VersionedFileSystemStorage(django_storage.FileSystemStorage):
    def __init__(self, *args, **kwargs):
        if 'base_url' not in kwargs:
            base_url = STATIC_URL
        if 'location' not in kwargs:
            location = STATIC_ROOT

        super(VersionedFileSystemStorage, self).__init__(base_url=base_url, location=location)

    def url(self, name):
        url = super(VersionedFileSystemStorage, self).url(name)
        return "{}?{}".format(url, settings.COMMIT_SHA)
