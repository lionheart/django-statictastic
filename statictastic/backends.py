from django.conf import settings
from storages.backends import s3boto

STORAGE_BUCKET_NAME = getattr(settings, 'AWS_STATIC_STORAGE_BUCKET_NAME', getattr(settings, 'AWS_STORAGE_BUCKET_NAME', None))

class PatchedS3BotoStorage(s3boto.S3BotoStorage):
    def __init__(self, *args, **kwargs):
        super(PatchedS3BotoStorage, self).__init__(*args, **kwargs)
        self.bucket_name = STORAGE_BUCKET_NAME

    def url(self, name):
        url = super(PatchedS3BotoStorage, self).url(name)
        return "{}?{}".format(url, settings.COMMIT_SHA[:5])

