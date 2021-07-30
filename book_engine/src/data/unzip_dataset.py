#!/usr/bin/env python3
from os import fspath
from os import path
from pathlib import Path
from shutil import copyfileobj
from zipfile import BadZipFile, ZipFile
from tqdm.auto import tqdm
from tqdm.utils import CallbackIOWrapper
from book_engine.src.helpers.path_helpers import child_path
import logging

logger = logging.getLogger("book_engine")


zip_path = child_path('data', 'external', 'dataset.zip')
unzip_path = child_path('data', 'raw')

def unzip_dataset(fzip=zip_path, dest=unzip_path, desc="Extracting"):
    """zipfile.Zipfile(fzip).extractall(dest) with progress"""

    def user_redownload_zip():
        user_input = input('Download the dataset ? yes/no  ').strip().lower()
        if user_input in ('yes', 'y'):
            from book_engine.src.data.download_dataset import download_dataset
            download_dataset()
        else:
            logger.fatal("There is nothing to unzip")


    if not path.isfile(zip_path):
        '''
        Check if there is file: "dataset.zip" to unzip, otherwise ask if user wants to download it
        '''
        logger.info("ZIP file - dataset.zip is not found")
        user_redownload_zip()

    # This adds progress bar to unzipping, code from library maintainer
    dest = Path(dest).expanduser()
    try:
        with ZipFile(fzip) as zipf, tqdm(
            desc=desc, unit="B", unit_scale=True, unit_divisor=1024,
            total=sum(getattr(i, "file_size", 0) for i in zipf.infolist()),
        ) as pbar:
            for i in zipf.infolist():
                if not getattr(i, "file_size", 0):  # directory
                    zipf.extract(i, fspath(dest))
                else:
                    with zipf.open(i) as fi, open(fspath(dest / i.filename), "wb") as fo:
                        copyfileobj(CallbackIOWrapper(pbar.update, fi), fo)
    except BadZipFile:
        logger.fatal('Bad Zip file - redownload it with ')
        user_redownload_zip()
    else:
        logger.info("Unzipped files reside at: " + str(unzip_path))