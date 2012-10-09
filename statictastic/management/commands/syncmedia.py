import gzip
import json
from io import BytesIO
from hashlib import md5

from django.core.management.base import BaseCommand
from django.contrib.staticfiles import finders, storage
from django.conf import settings
from django.core.files.base import ContentFile

from statictastic.progress import SnakeIndicator

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        staticstorage = storage.staticfiles_storage
        try:
            with staticstorage.open("checksums") as checksum_file:
                checksums = json.load(checksum_file)
        except IOError:
            checksums = {}

        indicator = SnakeIndicator("%s", "%d files skipped, %d files updated")
        num_updated = 0
        for finder in finders.get_finders():
            for path, localstorage in finder.list(['CVS', '.*', '*~']):
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
                        print prefixed_path, computed_md5, existing_md5

                    indicator.write(path, indicator.index-num_updated, num_updated)
                    indicator.animate()

        indicator.flush()

        staticstorage.save("checksums", ContentFile(json.dumps(checksums)))
        if hasattr(staticstorage, 'post_process'):
            processor = staticstorage.post_process(files)

