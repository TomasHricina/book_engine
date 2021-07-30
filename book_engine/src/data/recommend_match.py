
import logging
import pandas as pd
from book_engine.src.helpers.path_helpers import child_path
from nltk.metrics import edit_distance    


logger = logging.getLogger("book_engine")

pruned_books_path = child_path('data', 'interim', 'BX-Books.csv')

book_name = 'Fellowship of the ring'.lower()
book_author_last_name = 'Tolkien'.lower()



def match_book_name(_book_name: str, _book_author_last_name: str, number_of_results: int=5):

    # load pruned books
    books = pd.read_csv(pruned_books_path
    ,encoding='cp1251'
    ,sep=';'
    ,error_bad_lines=False
    ,usecols=['ISBN', 'Book-Title', 'Book-Author']
    ,dtype={'ISBN': 'string', 'Book-Title': 'string', 'Book-Author': 'string'}
    )

    _book_name = _book_name.lower()
    _book_author_last_name = _book_author_last_name.lower()

    _dataset_lowercase = books
    _dataset_lowercase[['Book-Title', 'Book-Author']] = books[['Book-Title', 'Book-Author']].apply(lambda col: col.str.lower())
    _books_with_same_author = _dataset_lowercase['Book-Author'].str.contains(_book_author_last_name)
    _same_author_books = _dataset_lowercase[['Book-Title', 'Book-Author']][_books_with_same_author]
    _same_author_books["book_search"] = _book_name
    _same_author_books["book_distance"] = _same_author_books.loc[:, ["Book-Title","book_search"]].apply(lambda x: edit_distance(*x), axis=1)
    _same_author_books.sort_values('book_distance', ascending = True, ignore_index=True, inplace=True)
    _same_author_books =_same_author_books.head(number_of_results)
    titles, authors = _same_author_books['Book-Title'].to_list(), _same_author_books['Book-Author'].to_list()
    
    results = tuple(zip(titles, authors))

    def remove_duplicates(k):
        newk = []
        for i in k:
            if i not in newk:
                newk.append(i)
        return newk

    return remove_duplicates(results)

