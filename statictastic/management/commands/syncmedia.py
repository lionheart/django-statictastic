import gzip
import json
from io import BytesIO
from hashlib import md5
from optparse import make_option

from django.core.management.base import BaseCommand
from django.contrib.staticfiles import finders, storage
from django.core.files.base import ContentFile

from boto.exception import S3ResponseError

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--ignore', dest='ignore', help="Ignore paths that match this regex."),
    )

    def handle(self, *args, **kwargs):
        staticstorage = storage.staticfiles_storage
        try:
            with staticstorage.open("checksums") as checksum_file:
                checksums = json.load(checksum_file)
        except IOError:
            checksums = {}
        except S3ResponseError:
            checksums = {}

        ignore = kwargs['ignore']

        num_updated = 0
        for finder in finders.get_finders():
            for path, localstorage in finder.list(['CVS', '.*', '*~']):
                if path.startswith("bundled"):
                    continue

                if ignore and path.startswith(ignore):
                    continue

                with localstorage.open(path) as source_file:
                    computed_md5 = md5(source_file.read()).hexdigest()
                    existing_md5 = checksums.get(path)
                    if computed_md5 != existing_md5:
                        checksums[path] = computed_md5
                        source_file.open()
                        if localstorage.prefix:
                            prefixed_path = localstorage.prefix + path
                        else:
                            prefixed_path = path

                        staticstorage.save(prefixed_path, source_file)
                        num_updated += 1
                        print "Updated", prefixed_path

        print "{} file{} updated".format(num_updated, '' if num_updated == 1 else 's')

        staticstorage.save("checksums", ContentFile(json.dumps(checksums)))
        if hasattr(staticstorage, 'post_process'):
            processor = staticstorage.post_process(files)

