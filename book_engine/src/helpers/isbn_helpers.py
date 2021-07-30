#!/usr/bin/python3
'''
Functions for repairing ISBNs
Functions for looking up on Google API - use isbn_safe_lookup - it does extra check if the API is working
'''

import logging


logger = logging.getLogger("book_engine")


def isbn_strip_non_digits(isbn: str) -> str:
    '''
    Some ISBNs include '-', remove all non-digits, except "X" and "x", which might be part of ISBN
    '''
    import re
    return re.sub('[^0-9X]','', isbn.upper())


def isbn_add_leading_zeroes(isbn: str) -> str:
    '''
    Leading zeroes might get lost in "str" -> "int" conversion
    '''
    len_isbn = len(isbn)
    if len_isbn < 10:
        return "0"*(10-len_isbn)+isbn # add leading zeroes
    elif 10 < len_isbn < 13:
        return "0"*(13-len_isbn)+isbn # add leading zeroes
    return isbn


def isbn_prepare(isbn: str) -> str:
    '''
    Strip non digits -> add leading zeroes, if necessary
    '''
    return isbn_add_leading_zeroes(isbn_strip_non_digits(isbn))


def isbn_lookup(isbn: str, api_key: str=None) -> tuple:
    '''
    Function that takes ISBN and check if it is in Google database, return book title and author
    '''
    import urllib.request
    import urllib.error
    import json

    base_api_link = "https://www.googleapis.com/books/v1/volumes?q=isbn:"
    
    # Try to fix corrupted ISBN
    isbn = isbn_prepare(isbn)


    # Add api_key if we have it
    if api_key:
        api_key_interface = "&key="
        api_link = base_api_link + isbn + api_key_interface + api_key
    else:
        api_link = base_api_link + isbn
    

    # Fetch JSON from Google API
    try:
        with urllib.request.urlopen(api_link) as f:
            text = f.read()
        decoded_text = text.decode("utf-8")
        obj = json.loads(decoded_text) # deserializes decoded_text to a Python object
        volume_info = obj["items"][0]
        title = volume_info["volumeInfo"]["title"]
        authors = ",".join(obj["items"][0]["volumeInfo"]["authors"])
        try:
            return title, authors
        except TypeError:
            logger.critical('Title, authors not found...')
            raise ConnectionError


    except urllib.error.HTTPError:
        logger.critical('HTTP error, retrying...')
        raise ConnectionError

    except urllib.error.ContentTooShortError:
        logger.critical('Error: truncated data, retrying...')
        raise ConnectionError

    # Base exception
    except urllib.error.URLError:
        logger.critical('URLError error, retrying...')
        raise ConnectionError

    except UnboundLocalError:
        logger.critical('UnboundLocalError error, retrying...')
        raise ConnectionError

    # ISBN not found
    except KeyError:
        logger.critical('ISBN not found...')
        raise ConnectionError


def isbn_safe_lookup(isbn: str, api_key: str=None) -> tuple:
    '''
    Does regular isbn_lookup, if it fails, it keeps trying to fetch book that is known to exist as confirmation
    '''

    try:
        # ISBN found - no problem, pass it over
        return isbn_lookup(isbn, api_key)
    
    
    except ConnectionError:

        # isbn_lookup threw exception, lets see if book, that we know exists can be found via API
        correct_isbn = "0345417623"
        correct_response = ('Timeline', 'Michael Crichton')
        correct_isbn_result = isbn_lookup(correct_isbn, api_key)

        # isbn_lookup found the test book, high chance of wrong ISBN
        if correct_isbn_result == correct_response:
            logger.critical("Looks like API works, but the ISBN is wrong")
            raise LookupError

        # isbn_lookup did NOT found the test book, API is broken, keep trying until it works
        else:
            while True:
                logger.critical("Trying to establish API connection...")
                correct_isbn_result = isbn_lookup(correct_isbn, api_key)
                if correct_isbn_result == correct_response:
                    return isbn_lookup(isbn, api_key)
