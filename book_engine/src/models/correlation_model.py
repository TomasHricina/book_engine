# import
from os import dup
import pandas as pd
import numpy as np
import sys


from book_engine.src.helpers.path_helpers import child_path

# real dataset
book_ratings_path = child_path('data', 'raw', 'BX-Book-Ratings.csv')
books_path = child_path('data', 'raw', 'BX-Books.csv')
book_name = 'the fellowship of the ring (the lord of the rings, part 1)'
book_author_last_name = 'tolkien'

# # test dataset

book_ratings_path = child_path('data', 'test', 'test_ratings.csv')
books_path = child_path('data', 'test', 'test_books.csv')
# book_name = 'search'
# book_author_last_name = 'author'



num_ratings_threshold = 8

# load ratings
ratings = pd.read_csv(book_ratings_path
,encoding='cp1251'
,sep=';'
,usecols=['User-ID', 'ISBN', 'Book-Rating']
)

ratings = ratings[ratings['Book-Rating']!=0]

# load books
books = pd.read_csv(books_path
,encoding='cp1251'
,sep=';'
,error_bad_lines=False
,usecols=['ISBN', 'Book-Title', 'Book-Author']
)


#?? We should merge on 'inner', because we want only data, thas in both datasets
dataset = pd.merge(ratings, books, on=['ISBN'], how='inner')

#?? Apply lower only to selected columns, not to every column that is 'object' 
#?? - In the original code, even the URLs are getting lowercased, which can break the link, because URLs can be case sensitive
#?? - It actually breaks Amazon image links

#?? BAD - dataset_lowercase=dataset.apply(lambda x: x.str.lower() if(x.dtype == 'object') else x)
dataset_lowercase = dataset
dataset_lowercase[['Book-Title', 'Book-Author']] = dataset[['Book-Title', 'Book-Author']].apply(lambda col: col.str.lower())



print('dataset.shape', dataset.shape)
print('dataset_lowercase\n', dataset_lowercase)

books_with_same_name = dataset_lowercase['Book-Title']==book_name
books_with_same_author = dataset_lowercase['Book-Author'].str.contains(book_author_last_name)

same_author_readers = dataset_lowercase['User-ID'][books_with_same_name & books_with_same_author]

print('same_author_readers\n', same_author_readers)

same_author_readers = same_author_readers.tolist()
same_author_readers = np.unique(same_author_readers)
#print(tolkien_readers)

# sys.exit()


# final dataset
books_of_same_author_readers = dataset_lowercase[(dataset_lowercase['User-ID'].isin(same_author_readers))]
print('books_of_same_author_readers\n', books_of_same_author_readers)

# Number of ratings per other books in dataset
number_of_rating_per_book = books_of_same_author_readers.groupby(['Book-Title']).agg('count').reset_index()


#select only books which have actually higher number of ratings than threshold
threshold_mask = number_of_rating_per_book['User-ID'] >= num_ratings_threshold

books_to_compare = number_of_rating_per_book['Book-Title'][threshold_mask]
books_to_compare = books_to_compare.tolist()

isin_books = books_of_same_author_readers['Book-Title'].isin(books_to_compare)
ratings_data_raw = books_of_same_author_readers[['User-ID', 'Book-Rating', 'Book-Title']][isin_books]

# # duplicit votes
# reference_votes = []
# duplicit_votes = []
# for index, row in ratings_data_raw.iterrows():
#     _row = row['User-ID'], row['Book-Title']
#     if _row in reference_votes:
#         duplicit_votes.append(_row)
#     else:
#         reference_votes.append(_row)

# print('duplicit_votes: ', len(duplicit_votes))


print('raw', ratings_data_raw.shape)
print('ratings_data_raw\n', ratings_data_raw)

# df = ratings_data_raw
# data_groups = df.groupby(df.columns.tolist())
# size = data_groups.size().reset_index() 
# print('duplicates', size[size[0] > 1].shape)        # DATAFRAME OF DUPLICATES

# group by User and Book and compute mean
ratings_data_raw_nodup = ratings_data_raw.groupby(['User-ID', 'Book-Title'])['Book-Rating'].mean()
print('ratings_data_raw_nodup', ratings_data_raw_nodup.shape)


# reset index to see User-ID in every row
ratings_data_raw_nodup = ratings_data_raw_nodup.to_frame().reset_index()
# ratings_data_raw_nodup.reset_index()
print('ratings cols', ratings_data_raw_nodup.columns)
print('nodeup', ratings_data_raw_nodup.shape)

dataset_for_corr = ratings_data_raw_nodup.pivot(index='User-ID', columns='Book-Title', values='Book-Rating')

print('dataset_for_corr\n', dataset_for_corr)
print(dataset_for_corr.shape)

result_list = []
worst_list = []


#Take out the selected book from correlation dataframe
dataset_of_other_books = dataset_for_corr.copy(deep=False)

dataset_of_other_books.drop([book_name], axis=1, inplace=True)
    
# empty lists
book_titles = []
correlations = []
avgrating = []

# print('col_values', list(dataset_of_other_books.columns))
# corr computation
print("dataset_of_other_books.columns.values\n: ", dataset_of_other_books.columns.values)

for book_title in list(dataset_of_other_books.columns.values):
    book_titles.append(book_title)
    correlations.append(dataset_for_corr[book_name].corr(dataset_of_other_books[book_title]))
    tab=(ratings_data_raw[ratings_data_raw['Book-Title']==book_title].groupby(ratings_data_raw['Book-Title']).mean())
    avgrating.append(tab['Book-Rating'].min())
# final dataframe of all correlation of each book   
book_correlations = pd.DataFrame(list(zip(book_titles, correlations, avgrating)), columns=['book','corr','avg_rating'])
book_correlations.head()

# top 10 books with highest corr
result_list.append(book_correlations.sort_values('corr', ascending = False).head(10))

#worst 10 books
worst_list.append(book_correlations.sort_values('corr', ascending = False).tail(10))
    
print("Correlation for book:", book_name)
#print("Average rating of LOR:", ratings_data_raw[ratings_data_raw['Book-Title']=='the fellowship of the ring (the lord of the rings, part 1'].groupby(ratings_data_raw['Book-Title']).mean()))
rslt = result_list[0]

print("RESULT")
print(rslt)