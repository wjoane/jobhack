# Jockhack NLP Prediction Library

This library allows the training of a classification model based on text descriptions of job offers sraped from a recruiting website and automatically labeled using a simple fuzzy keyword serach. You can than use the model to predict if a job description in a certain URL corresponds to the class of jobs you are looking for.

## Installation
* Clone this repository with: `git clone https://github.com/wjoane/jobhack.git`
* Install pip requirements with: `pip install -r requiirements.txt`
* Modify the settings in config.ini after: `cp config.ini.example config.ini`
* Enjoy

## Usage

Just fill the program parameters in config.ini and run `train.py` to crawl through a website, train a model using the scraped and labeled data and save the pretrained model to a file. Run `predict.py` to get an evaluation of a job description page, after being prompted to enter the URL.

## Config
You can find an example of the config file in config.ini.example for the tanitjobs.com Website.

    [DATABASE]
    # Only mysql is supported now
    type     = mysql 
    # DB login creditentials
    host     = 
    user     = 
    password = 
    database = 

    [WEBSITE]
    # The URL of the job listing in the website to be crawled. The delimited <#> will be replaced by increasing pagination numbers
    site_url             = https://www.tanitjobs.com/jobs/?page=<#>
    # Yes to use simple curl requests to access the site contents. No will use a selenium headless browser to access websites that detect bot requests.
    basic_mode           = yes
    # Yes if the website uses relative links the link to intern pages
    relative_links       = no
    # Pagination start
    start_page           = 1
    # Pagination end
    max_pages            = 178
    # Website language, any different language will be ignored. The Classifier now only supports fr
    language             = fr
    # CSS Selector to access the container of single page links
    item_selector        = article.listing-item__jobs
    # CSS Selector to access the links 
    link_selector        = div.listing-item__title a
    # CSS Selector to access the job descriptions, leaving this empty will evaluate the whole pages
    description_selector = div.detail-offre

    [CHROME]
    # Configuration for the selenium headless browser
    bin     = /usr/bin/google-chrome
    driver  = driver/chromedriver
    profile = driver/profile

    [LABELER]
    # Keywords to use for the automatic labeling of data
    positive_keywords  = developpeur,informatique,java,python,php,machine learning,intelligence artificielle,data science,medical
    negative_keywords  = anxiete,charge,colere,depression,faire preuve de,horaire fixe,obligatoire,sous pression,stress,surcharge,temps plein,temps supplementaire,un minimum de
    # Weights for negative keywords compared to positive ones. Set a negative value to evaluate give more weight to positive keywords
    negative_weight    = 1.5
    # Will be added everytime a new keyword is found in a description. Only 1 will be added for every subsequent occurence
    bonus_for_hits     = 4
    # The fuzzy distance will be detemined by dividing the keyword length by this parameter
    max_l_divider      = 5
    # Minimum length to allow fuzzy search
    min_l_fuzzy        = 5

    [TRAINING]
    # Path to save the pretrained model for further use
    model_path       = model/job_classification.model
    # Path to export the preprocessed data as CSV file for further use
    csv_data_path    = tmp/preprocessed_data.csv
    # Percentage of the most relevant training data to be used for training
    training_percent = 25
    # Max features to be extracted from the training text data
    max_features     = 1000
    # TF_IDF Parameters
    min_df           = 0.05
    max_df           = 0.4
    # Label threshold to seperate positive and negative examples in the training data
    class_threshold  = 0
    
    This is a change
