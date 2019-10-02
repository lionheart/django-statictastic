# Copyright 2012-2017 Lionheart Software LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import gzip
import json
from io import BytesIO
from hashlib import md5
from optparse import make_option

from django.core.management.base import BaseCommand
from django.contrib.staticfiles import finders, storage
from django.core.files.base import ContentFile

from botocore.exceptions import ClientError

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--ignore', dest='ignore', help="Ignore paths that match this regex."),
        parser.add_argument('--force-sync', dest='force_sync', action='store_true', help="Update all files, regardless of whether or not they have already been synced."),

    def handle(self, *args, **kwargs):
        staticstorage = storage.staticfiles_storage
        try:
            with staticstorage.open("checksums") as checksum_file:
                checksum_data = checksum_file.read().decode("utf-8")
                checksums = json.loads(checksum_data)
        except IOError:
            checksums = {}
        except ClientError:
            checksums = {}

        ignore = kwargs['ignore']
        force_sync = kwargs['force_sync']

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
                    if computed_md5 != existing_md5 or force_sync:
                        checksums[path] = computed_md5
                        source_file.open()
                        try:
                            localstorage.prefix
                        except AttributeError:
                            prefixed_path = path
                        else:
                            if localstorage.prefix:
                                prefixed_path = localstorage.prefix + path
                            else:
                                prefixed_path = path

                        staticstorage.save(prefixed_path, source_file)
                        num_updated += 1
                        print("Updated", prefixed_path)

        print("{} file{} updated".format(num_updated, '' if num_updated == 1 else 's'))

        staticstorage.save("checksums", ContentFile(json.dumps(checksums).encode('utf-8')))
        if hasattr(staticstorage, 'post_process'):
            processor = staticstorage.post_process(files)

