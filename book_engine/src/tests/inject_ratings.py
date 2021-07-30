import pandas as pd
import numpy as np
import csv
from book_engine.src.helpers.path_helpers import child_path

# real dataset
book_ratings_path = child_path('data', 'raw', 'BX-Book-Ratings.csv')
injected_book_ratings_path = child_path('data', 'injected', 'BX-Book-Ratings.csv')

ratings = pd.read_csv(book_ratings_path
,encoding='cp1251'
,sep=';'
,error_bad_lines=False
,usecols=['User-ID', 'ISBN', 'Book-Rating']
,dtype={'User-ID': 'string', 'ISBN': 'string', 'Book-Rating': 'int'}
)

"INJECTED_BOOK";"tolkien"

injected_count = 200
injected_isbn = "INJECTED"
injected_rating = 10
end_user_id = 500000

x = 0
for user_id in range(end_user_id-injected_count, end_user_id):
    ratings.loc[len(ratings.index)] = [str(user_id), injected_isbn, str(injected_rating)]

ratings.to_csv(injected_book_ratings_path, index=False, sep=';', quoting=csv.QUOTE_NONNUMERIC) 