Welcome in Book-Recommendation engine.   
   
Book engine has several stages:
-download = Downloads raw dataset into "book_engine/data/external/"
-unzip = Unzips into "book_engine/data/raw/"
-prune =    -takes BX-Book_Ratings.csv
            -extracts all ISBNs
            -sorts them by number of ratings
            -keeps only top ${your_input} of top books
            (example: book_engine prune 20 - keeps only top20 books)
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



Project Organization (not literal)

------------

    ├── LICENSE
    ├── Makefile           <- Makefile with commands like `make data` or `make train`
    ├── README.md          <- The top-level README for developers using this project.
    ├── data
    │   ├── external       <- Data from third party sources.
    │   ├── interim        <- Intermediate data that has been transformed.
    │   ├── processed      <- The final, canonical data sets for modeling.
    │   └── raw            <- The original, immutable data dump.
    │
    ├── docs               <- A default Sphinx project; see sphinx-doc.org for details
    │
    ├── models             <- Trained and serialized models, model predictions, or model summaries
    │
    ├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
    │                         the creator's initials, and a short `-` delimited description, e.g.
    │                         `1.0-jqp-initial-data-exploration`.
    │
    ├── references         <- Data dictionaries, manuals, and all other explanatory materials.
    │
    ├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
    │   └── figures        <- Generated graphics and figures to be used in reporting
    │
    ├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
    │                         generated with `pip freeze > requirements.txt`
    │
    ├── setup.py           <- makes project pip installable (pip install -e .) so src can be imported
    ├── src                <- Source code for use in this project.
    │   ├── __init__.py    <- Makes src a Python module
    │   │
    │   ├── data           <- Scripts to download or generate data
    │   │   └── make_dataset.py
    │   │
    │   ├── features       <- Scripts to turn raw data into features for modeling
    │   │   └── build_features.py
    │   │
    │   ├── models         <- Scripts to train models and then use trained models to make
    │   │   │                 predictions
    │   │   ├── predict_model.py
    │   │   └── train_model.py
    │   │
    │   └── visualization  <- Scripts to create exploratory and results oriented visualizations
    │       └── visualize.py
    │
    └── tox.ini            <- tox file with settings for running tox; see tox.readthedocs.io


--------

<p><small>Project based on the <a target="_blank" href="https://drivendata.github.io/cookiecutter-data-science/">cookiecutter data science project template</a>. #cookiecutterdatascience</small></p>
