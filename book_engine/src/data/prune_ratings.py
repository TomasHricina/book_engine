#!/usr/bin/env python3
from book_engine.src.helpers.path_helpers import child_path
import logging
import pandas as pd
import csv
from collections import Counter

logger = logging.getLogger("book_engine")


book_ratings_path = child_path('data', 'raw', 'BX-Book-Ratings.csv')
books_path = child_path('data', 'raw', 'BX-Books.csv')

pruned_ratings_path = child_path('data', 'interim', 'BX-Book-Ratings.csv')
pruned_books_path = child_path('data', 'interim', 'BX-Books.csv')


def prune(kept_top_books: int=None, kept_ratings_percentage: int=None, output_to_file: bool=True):
    '''
    Function that takes raw dataset of ratings, finds out which books are most rated.
    It keeps only the top N specified books - or top n% of ratings of books.
    Three options: -pass kept_top_books - passed "1000" means it keeps only top 1000 books
                   -pass kept_rating_percentage - passed "30" means it keeps 30% of top ratings (and only books that are top 30% rated)
                   -pass nothing - it keeps everything
    '''

    logger.info('Prunning started')

    # Load ratings dataset
    ratings = pd.read_csv(book_ratings_path
    ,encoding='cp1251'
    ,sep=';'
    ,usecols=['User-ID', 'ISBN', 'Book-Rating']
    ,dtype={'User-ID': 'string', 'ISBN': 'string', 'Book-Rating': 'int'}
    ,error_bad_lines=False
    ,warn_bad_lines=False
    )
    
    ratings_count = ratings.shape[0]
    logger.info('Number of book ratings is: ' + str(ratings_count))

    # Could be done with pandas.value_counts
    counter = Counter(ratings['ISBN'].tolist()).most_common()
    logger.info('Number of unique rated books is: ' + str(len(counter)))

    # Keep top N books
    if kept_top_books:
        result_count = kept_top_books

        # Find how many ratings do the Top N books contain
        sub_rating_total = 0
        for book_idx in range(result_count):
            sub_rating_total += counter[book_idx][1]


    # Keep certain percentage of ratings
    elif kept_ratings_percentage:
        kept_absolute = round(ratings_count *  (kept_ratings_percentage/100))
        rating_index = 0
        sub_rating_total = 0
        rating_result = []
        
        while sub_rating_total < kept_absolute:
            counter_row = counter[rating_index]
            rating_result.append(counter_row[0])
            sub_rating_total += counter_row[1]
            rating_index += 1

        result_count = rating_index
        kept_top_books = rating_index
    
        # if none of the options were chosen, assume we want all books and all ratings
    elif not kept_top_books and not kept_ratings_percentage:
        sub_rating_total = ratings_count
        result_count = ratings_count


    ratings_percentage_count = round((sub_rating_total/ratings_count*100), 2)

    logger.info('Number of post-pruned books is: ' + str(result_count))
    logger.info('Top'+str(kept_top_books)+' contain: '+str(ratings_percentage_count)+'% of ratings')
    logger.info('Percantage of pruned books to original dataset is: ' + str(round(((result_count/ratings_count)*100), 2)) + '%')

    counter = counter[:result_count+1]
    logger.info('Lowest amount of ratings: ' + str(counter[-1][1]))
    books = pd.DataFrame.from_records(counter, columns=['ISBN','ratings_count'])

    ## Update the datasets

    # load ratings
    original_ratings = ratings

    # load books
    original_books = pd.read_csv(books_path
    ,encoding='cp1251'
    ,sep=';'
    ,error_bad_lines=False
    ,usecols=['ISBN', 'Book-Title', 'Book-Author']
    ,dtype={'ISBN': 'string', 'Book-Title': 'string', 'Book-Author': 'string'}
    )

    new_ratings = pd.merge(original_ratings, books, on=['ISBN'], how='inner')
    new_books = pd.merge(original_books, books, on=['ISBN'], how='inner')

    new_ratings.sort_values('ratings_count', ascending=False, inplace=True, ignore_index=True)
    new_books.sort_values('ratings_count', ascending=False, inplace=True, ignore_index=True)
    
    ## /Update the datasets

    if output_to_file:
        new_ratings.drop('ratings_count', axis='columns', inplace=True)
        new_books.drop('ratings_count', axis='columns', inplace=True)
        new_ratings.to_csv(path_or_buf=pruned_ratings_path, index=False, sep=';', quoting=csv.QUOTE_NONNUMERIC, encoding='cp1251')
        new_books.to_csv(path_or_buf=pruned_books_path, index=False, sep=';', quoting=csv.QUOTE_NONNUMERIC, encoding='cp1251')
        logger.info('Prunning complete, datasets in /data/interim folder')
    else:
        return {'ratings': new_ratings, 'books': new_books}

# prune(kept_ratings_percentage=5, output_to_file=False)
# prune(kept_top_books=100, output_to_file=False)