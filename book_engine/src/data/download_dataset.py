#!/usr/bin/python3
from book_engine.src.helpers.path_helpers import child_path
import logging

logger = logging.getLogger("book_engine")


database_link = r"http://www2.informatik.uni-freiburg.de/~cziegler/BX/BX-CSV-Dump.zip"

from tqdm import tqdm
class DownloadProgressBar(tqdm):
    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)


def download_dataset(url=database_link):
    import os
    import urllib.request

    raw_dataset_path = child_path('data', 'external')
    dataset_filename = 'dataset.zip'
    raw_dataset_path_with_filename = os.path.join(raw_dataset_path, dataset_filename)

    try:
        with DownloadProgressBar(unit='B', unit_scale=True, miniters=1, desc=url.split('/')[-1]) as t:
            urllib.request.urlretrieve(url, filename=raw_dataset_path_with_filename, reporthook=t.update_to)

        logger.info("Downloaded dataset resides at: " + str(raw_dataset_path_with_filename))

    except urllib.error.URLError:
        logger.fatal("Cannot download the file - check your connection or check database link: \n" + database_link)
