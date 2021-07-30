#!/usr/bin/env python3
"""

Welcome in Book-Recommendation engine.

Book engine has several stages:

-download = Downloads raw dataset into "book_engine/data/external/"

-unzip = Unzips into "book_engine/data/raw/"

-prune =    -takes BX-Book_Ratings.csv
            -extracts all ISBNs
            -sorts them by number of ratings
            -keeps only top ${your_input} of books
            (example: book_engine prune 20 - keeps only 20% of the ratings )

-validate = -(optional)
            -reads every ISBN from Books dataset.
            -connects to Google API and redownloads the name of book and its authors
            -this process is long, but the engine will remember where you left off
                if you decide to stop it or if it fails temporarily
            -ISBNs that are found in Google are placed to: 
                -"book_engine/data/interim/redownloaded_dataset.csv"
            -ISBNs that are not found are placed to:
                -"book_engine/data/interim/failed_isbn_dataset.csv"

-recommend = -recommends list of top10 books, book_name must be exact match (case insensitive)

-recommend_match = -also recommends list of top10 books, but tries to match book_name 

Usage: 
        book_engine download
        book_engine unzip
        book_engine prune           //pass number, like 1000 for top1000 books
        book_engine validate        //pass API key with double quotes like this: "my-Api-key"
        book_engine recommend       //pass book name with double quotes, space, then last name of author with double quotes
        book_engine recommned_match //pass book name with double quotes, space, then last name of author with double quotes

"""

import sys
from book_engine.src.data.download_dataset import download_dataset
from book_engine.src.data.unzip_dataset import unzip_dataset
from book_engine.src.data.prune_ratings import prune
from book_engine.src.data.validate_dataset import validate_datasets
from book_engine.src.helpers.api_helper import get_api_credentials
from book_engine.src.models.production_correlation import correlation_recommender_engine
from book_engine.src.data.recommend_match import match_book_name
from book_engine.src.helpers.logger_func import create_logger

log_level = "INFO"
logger = create_logger(__package__)
logger.setLevel(log_level)


def main_entry_point():
    '''
    Dev comment:
    One could - and should - do more fancy parsing with library,
    the time was spend on the functionality of the commands.
    '''
    arguments = sys.argv

    # Print help if no arguments were passed
    if len(arguments) <= 1:
        logger.info(__doc__)
        return

    command = arguments[1]
    
    if len(arguments) > 2:
        parameters = arguments[2:]
        first_parameter = parameters[0]
    else:
        parameters = None


    if command == 'download':
        download_dataset() # Exception handled inside


    elif command == 'unzip':
        unzip_dataset() # Exception handled inside


    elif command == 'prune':
        if parameters:
            try:
                top_n_books = int(first_parameter)
            except ValueError:
                logger.error('Prune only accepts integers')
                return
        else:
            # no parameters => default
            top_n_books = 1000
        try:
            prune(kept_top_books=top_n_books, output_to_file=True)
        except FileNotFoundError:
            logger.critical('Raw dataset not found - run: book_engine download -> book_engine unzip')


    elif command == 'validate':
        if parameters:
            api = first_parameter
        else:
            api = get_api_credentials()
        
        try:
            validate_datasets(api_key=api)
        except FileNotFoundError:
            logger.critical('Pruned dataset not found')

            user_input = input('Do you want to execute validation on raw set ? (its very large!) - yes/no:  ').lower().strip()
            if user_input in ('y', 'yes'):
                try:
                    validate_datasets(api_key=api)
                except FileNotFoundError:
                    logger.fatal('Not even raw dataset is found - run: book_engine download -> book_engine unzip -> book_engine prune')                    
            else:
                return

    elif command == 'recommend':
        if not parameters or len(parameters) == 1:
            logger.error('Usage: book_engine recommend "BOOKNAME" "AUTHOR" (surrounding double quotes)')

        else:
            book_name = parameters[-2]
            author = parameters[-1]

            try:
                result = correlation_recommender_engine(book_name, author)
                logger.info('Book name:   ' + book_name)
                logger.info('Book author:   ' + author)
                logger.info('\n\nTop recommendations: ')
                for idx, val in enumerate(result):
                    logger.info(str(idx+1) + '. "' + str(val) + '"')
                
            except KeyError:
                logger.error('The book you entered is not in our database, try \'book_engine recommend_match "BOOKNAME" "AUTHOR"\' instead, it will try to match your book')

            except FileNotFoundError:
                logger.fatal('Datasets are not in place, run previous book_engine commands')


    elif command == 'recommend_match':
        if not parameters or len(parameters) == 1:
            logger.error('Usage: book_engine recommend_match "BOOKNAME" "AUTHOR" (surrounding double quotes)')
        else:
            book_name = parameters[-2]
            author = parameters[-1]

            try:
                matches = match_book_name(book_name, author)
                for idx, val in enumerate(matches):
                    logger.info(str(idx+1) + '. "' + str(val[0]) + '" ' + ' "' + str(val[1]) +'"')


                user_input = input('Write number of the book, that you want to base your recommendation: ').strip()
                
                try:
                    user_input = int(user_input)-1
                    assert user_input in range(len(matches))
                except (ValueError, AssertionError):
                    logger.fatal('User input invalid. Try again')
                    return

                matches_user_picked = matches[user_input]
                result = correlation_recommender_engine(matches_user_picked[0], matches_user_picked[1])
                logger.info('Book name:   ' + book_name)
                logger.info('Book author:   ' + author)
                logger.info('\n\nTop recommendations: ')
                for idx, val in enumerate(result):
                    logger.info(str(idx+1) + '. "' + str(val) + '"')
                else:
                    logger.info('There are none, book is too rare')
                
            except KeyError:
                logger.error('The book you entered is not in our database')

            except FileNotFoundError:
                logger.fatal('Datasets are not in place, run previous book_engine commands')



    else:
        logger.error('Unknown command: ' + command)
        logger.info(__doc__)


if __name__ == '__main__':
    main_entry_point()
