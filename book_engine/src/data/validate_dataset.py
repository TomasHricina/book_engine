#!/usr/bin/python3
import os
import csv
import pandas as pd
from tqdm import tqdm
from book_engine.src.helpers.path_helpers import child_path
from book_engine.src.helpers.isbn_helpers import isbn_safe_lookup
import logging

logger = logging.getLogger("book_engine")

# Output seperator
_sep = '^' 

# Column names
_id = 'ID'
_isbn = 'ISBN'
_title = 'Book-Title'
_authors = 'Book-Author'


# Paths to datasets - "interim" means intermediate step
redownloaded_dataset_path = child_path('data', 'processed' , 'redownloaded_dataset.csv')
failed_isbn_dataset_path = child_path('data', 'processed', 'failed_isbn_dataset.csv')
prunned_books_dataset_path = child_path('data', 'interim', 'BX-Books.csv') 
# raw_books_dataset_path = child_path('data', 'raw', 'BX-Books.csv') # then try raw dataset


def prepare_one_dataset(dataset_path: str, columns: tuple):
    '''
    Function that looks at the dataset and decides, if it should continue downloading or if the dataset format is right.
    The actual downloading does not happen here, only preparation of files, cleanup and $_dataset_last_id determination.
    '''

    # First assume redownloading should start from beginning
    _dataset_last_id = -1

    # If dataset not found or if its empty, creates file with header, that contains $columns that you chosed
    if not os.path.isfile(dataset_path) or os.stat(dataset_path).st_size == 0:
        
        # Write header (column names)
        with open(dataset_path, 'w') as dataset:
            csv_header_cols = columns
            csv_header = _sep.join([col for col in csv_header_cols])+'\n'
            dataset.write(csv_header)

    # File exists and its not empty
    else:
        # Try reading csv in the format, we expect
        try:
            df_books = pd.read_csv(dataset_path, sep=_sep)

            # Checks if the csv has right columns
            assert tuple(df_books.columns) == columns

            try:
                # Detect where we left of, prevents redownloading same data after unexpected failure
                _last_id = df_books[_id].iloc[-1]
                if _last_id >= -1:
                    _dataset_last_id = _last_id

            # File only has header, thats fine, proceed as normal
            except IndexError:
                pass

        # File has wrong columns, prompt user
        except AssertionError:    
            logger.fatal('File has wrong columns. Do you want to delete it and start over ? yes/no')
            
            user_input = input().strip().lower()
            if user_input in ('yes', 'y'):

                # User wants to delete file
                try:
                    os.remove(dataset_path)

                    # Start over 
                    prepare_one_dataset(dataset_path, columns)
                
                # If file does not exists, we dont need to do anything
                except FileNotFoundError:
                    pass

    return _dataset_last_id


def prepare_datasets():
    '''
    Redownloaded dataset - dataset with valid ISBNs that has been confirmed via API
    Failed dataset - dataset, where the invalid ISBNs are stored
    '''

    # Prepare datasets, return value is id, when they left off
    redownloaded_dataset_id = prepare_one_dataset(redownloaded_dataset_path, columns=(_id, _isbn, _title, _authors))
    failed_dataset_id = prepare_one_dataset(failed_isbn_dataset_path, columns=(_id, _isbn))

    # This id allowes script to start, where it left off - useful if dataset grew or the downloading was not ended gracefully
    _datasets_last_id = max(redownloaded_dataset_id, failed_dataset_id)

    # Inform user, where the redownloading of dataset starts off 
    if _datasets_last_id == -1:
        logger.info("Dataset will start redownloading from beginning")
    else:
        logger.info("Dataset will start redownloading from row number: " + str(_datasets_last_id))

    return _datasets_last_id


def validate_datasets(book_dataset_path: str=prunned_books_dataset_path ,api_key: str=None):
    '''
    Can throw FileNotFoundError - if there is no file
    '''

    # Prepare datasets, get id, where we left off (because last time the program may not finished or new data appeared)
    datasets_last_id = prepare_datasets()

    books = pd.read_csv(book_dataset_path
    ,encoding='cp1251'
    ,sep=';'
    ,usecols = [_isbn]
    ,dtype={_isbn: 'string'}
    ,error_bad_lines=False
    ,warn_bad_lines=False
    )

    # Get the original dataset row_count
    books_rows_count = books.shape[0]

    # Add ID of original dataset, so we can recover, if program ends abruptly
    books.insert(0, 'ID', range(books_rows_count))

    if datasets_last_id+1 == books_rows_count:
        logger.info('There is nothing more to download')
        return

    # Iterate over every row, in original dataset and download data via API (using ISBN)
    for row_number in tqdm(range(datasets_last_id+1, books_rows_count)):
        row = books.iloc[[row_number]]
        isbn = row[_isbn].to_string(index=False, header=False).strip()

        try:
            lookup = isbn_safe_lookup(isbn, api_key=api_key)

            try:
                title, authors = lookup
                csv_tuple = row_number, isbn, title, authors
                success_or_failed_dataset_path = redownloaded_dataset_path
            except TypeError:
                # Data got corrupted
                csv_tuple = row_number, isbn
                success_or_failed_dataset_path = failed_isbn_dataset_path

        except LookupError:
            # Google API does not have this book - with high confidence
            csv_tuple = row_number, isbn
            success_or_failed_dataset_path = failed_isbn_dataset_path


        # Write into dataset, variable $success_or_failed_dataset_path - determines where the data is written
        with open(success_or_failed_dataset_path, 'a') as file: 
            write = csv.writer(file, delimiter=_sep, quotechar = "x") 
            write.writerow(csv_tuple) 

# validate_datasets("AIzaSyDtj14VT1olEHSv8fJvvac1X0n4EPcsjOo")