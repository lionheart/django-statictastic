import gzip
import json
from io import BytesIO

from django.contrib.staticfiles import finders, storage

from slimit import minify as minify_js
from cssmin import cssmin as minify_css

def gzip_file(source):
    target = BytesIO()
    content = gzip.GzipFile(fileobj=target, mode='w', mtime=0)
    content.write(source.getvalue())
    content.close()
    return BytesIO(target.getvalue())

staticstorage = storage.staticfiles_storage
with storage.open("checksums") as checksum_file:
    checksums = json.load(checksum_file)

for finder in finders.get_finders():
    for path, storage in finder.list(['CVS', '.*', '*~']):
        with storage.open(path) as source_file:
            staticstorage.save(prefixed_path, source_file)

if hasattr(staticstorage, 'post_process'):
    processor = staticstorage.post_process(files)
