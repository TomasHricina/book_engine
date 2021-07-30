#!/usr/bin/env python3
import pandas as pd
import numpy as np
from book_engine.src.helpers.path_helpers import child_path
import logging


logger = logging.getLogger("book_engine")


# # raw dataset
# book_ratings_path = child_path('data', 'raw', 'BX-Book-Ratings.csv')
# books_path = child_path('data', 'raw', 'BX-Books.csv')

# pruned dataset - comment if needed
book_ratings_path = child_path('data', 'interim', 'BX-Book-Ratings.csv')
books_path = child_path('data', 'interim', 'BX-Books.csv')

# default values
book_name = 'the fellowship of the ring (the lord of the rings, part 1)'
book_author_last_name = 'tolkien'
default_num_ratings_threshold = 11


def correlation_recommender_engine(book_name: str=book_name
             ,book_author_last_name: str=book_author_last_name
             ,num_ratings_threshold: int= default_num_ratings_threshold):

    book_name = book_name.lower()
    book_author_last_name = book_author_last_name.lower()

    #?? Specify columns that, you will work with, no need to load whole dataset
    #?? Specify dtypes, ISBN can be loaded as int, but that would cut leading zeroes
    # load ratings
    ratings = pd.read_csv(book_ratings_path
    ,encoding='cp1251'
    ,sep=';'
    ,error_bad_lines=False
    ,usecols=['User-ID', 'ISBN', 'Book-Rating']
    ,dtype={'User-ID': 'string', 'ISBN': 'string', 'Book-Rating': 'int'}
    )

    #?? This should be removed at dataset preprocessing
    ratings = ratings[ratings['Book-Rating']!=0]

    # load books
    books = pd.read_csv(books_path
    ,encoding='cp1251'
    ,sep=';'
    ,error_bad_lines=False
    ,usecols=['ISBN', 'Book-Title', 'Book-Author']
    ,dtype={'ISBN': 'string', 'Book-Title': 'string', 'Book-Author': 'string'}
    )

    #?? We should merge on 'inner', because we want only data, thas in both datasets
    dataset = pd.merge(ratings, books, on=['ISBN'], how='inner')
    

    #?? old - dataset_lowercase=dataset.apply(lambda x: x.str.lower() if(x.dtype == 'object') else x)
    #?? Apply lower only to selected columns, not to every column that is 'object' 
    #?? - In the original code, even the URLs are getting lowercased, which can break the link, because URLs can be case sensitive
    #?? - It actually breaks Amazon image links 

    dataset_lowercase = dataset
    dataset_lowercase[['Book-Title', 'Book-Author']] = dataset[['Book-Title', 'Book-Author']].apply(lambda col: col.str.lower())

    books_with_same_name = dataset_lowercase['Book-Title']==book_name
    
    # print(books_with_same_name.value_counts())


    # # print(books_with_same_name)
    # import re
    # books_with_same_name = dataset['Book-Title'].str.fullmatch(book_name, case=False, flags=re.IGNORECASE)

    # print(books_with_same_name.value_counts())

    # If there is no book with that name raise exception
    if not (True in books_with_same_name.value_counts().to_dict()):
        logger.critical('Book was not found')
        raise KeyError

    books_with_same_author = dataset_lowercase['Book-Author'].str.contains(book_author_last_name)

    same_author_readers = dataset_lowercase['User-ID'][books_with_same_name & books_with_same_author]


    same_author_readers = same_author_readers.tolist()
    same_author_readers = np.unique(same_author_readers)


    # final dataset
    books_of_same_author_readers = dataset_lowercase[(dataset_lowercase['User-ID'].isin(same_author_readers))]

    # Number of ratings per other books in dataset
    number_of_rating_per_book = books_of_same_author_readers.groupby(['Book-Title']).agg('count').reset_index()

    #?? put the threshold on top of the file 
    #?? break the long statements into shorter ones
    #select only books which have actually higher number of ratings than threshold
    threshold_mask = number_of_rating_per_book['User-ID'] >= num_ratings_threshold
    books_to_compare = number_of_rating_per_book['Book-Title'][threshold_mask]
    books_to_compare = books_to_compare.tolist()

    isin_books = books_of_same_author_readers['Book-Title'].isin(books_to_compare)
    ratings_data_raw = books_of_same_author_readers[['User-ID', 'Book-Rating', 'Book-Title']][isin_books]

    #?? This line also converts duplicate votes into mean, comment-worthy
    # group by User and Book and compute mean
    ratings_data_raw_nodup = ratings_data_raw.groupby(['User-ID', 'Book-Title'])['Book-Rating'].mean()

    # reset index to see User-ID in every row
    ratings_data_raw_nodup = ratings_data_raw_nodup.to_frame().reset_index()


    dataset_for_corr = ratings_data_raw_nodup.pivot(index='User-ID', columns='Book-Title', values='Book-Rating')

    result_list = []
    worst_list = []

    #Take out the selected book from correlation dataframe
    dataset_of_other_books = dataset_for_corr.copy(deep=False)
    dataset_of_other_books.drop([book_name], axis=1, inplace=True)
        
    # empty lists
    book_titles = []
    correlations = []
    avgrating = []

    for book_title in list(dataset_of_other_books.columns.values):
        book_titles.append(book_title)
        correlations.append(dataset_for_corr[book_name].corr(dataset_of_other_books[book_title]))
        tab=(ratings_data_raw[ratings_data_raw['Book-Title']==book_title].groupby(ratings_data_raw['Book-Title']).mean())
        avgrating.append(tab['Book-Rating'].min())


    # final dataframe of all correlation of each book   
    book_correlations = pd.DataFrame(list(zip(book_titles, correlations, avgrating)), columns=['Book-Title','corr','avg_rating'])
    
    #?? Discuss the model
    #?? added vote counts to prove a point - correlation might not be "the best" choice
    vote_counts = dataset_of_other_books.count()
    vote_counts.name = 'votes'
    book_correlations = book_correlations.join(vote_counts, on='Book-Title', how='inner')


    #?? Dont sort same dataset two times
    # top 10 books with highest corr
    sorted_books = book_correlations.sort_values('corr', ascending = False, ignore_index=True)


    #?? result_list.append(corr_fellowship.sort_values('corr', ascending = False).head(10))
    #?? worst_list.append(corr_fellowship.sort_values('corr', ascending = False).tail(10))

    result_list.append(sorted_books.head(10))
    worst_list.append(sorted_books.tail(10))
        

    #print("Average rating of LOR:", ratings_data_raw[ratings_data_raw['Book-Title']=='the fellowship of the ring (the lord of the rings, part 1'].groupby(ratings_data_raw['Book-Title']).mean()))
    rslt = result_list[0]


    return rslt['Book-Title'].tolist()

# print(correlation_recommender_engine())