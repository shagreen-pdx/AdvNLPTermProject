import os
import subprocess
import re
from textblob import TextBlob
import pandas
from textgenrnn import textgenrnn
import time
import sys

get_tweet_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.join('Optimized-Modified-GetOldTweets3-OMGOT-fix-api', 'GetOldTweets3-0.0.10'))
output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')


def gather_tweets(kwd, loc, f):
    # Create command to pull tweets based on a certain keyword
    # Limit (increments of 20) - we will investigate how this impacts our results
    # Links - we want to exclude tweets with links to avoid ads and having to remove links manually
    # Lang - we only want english tweets
    # --> Drawback: our keywords are in english so it'll match all tweets with keyword regardless of rest of language
    # Near - allows us to specify a location to give us more english results
    cmd = 'python cli.py -s \"' + kwd + '\" --limit 1000 --links exclude --lang en --near \"' + loc + '\"'

    # CD into directory of GetOldTweets code and run code
    os.chdir(get_tweet_path)

    # Open output file and redirect output of the GetTweet command to text file
    with open(f, 'w') as out:
        p = subprocess.run(cmd, stdout=out, stderr=out)


def clean_tweet(tweet):
    # Strip twitter mentions (@username), punctuation and special characters and emojis, and twitter usernames (<username>)
    return ' '.join(re.sub("(<[\w]+>)|(@[\w]+)|([^0-9A-Za-z \t])|(\w+:\/ \/ \S+)", " ", tweet).split())


def remove_emoji(string):
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                               u"\U00002500-\U00002BEF"  # chinese char
                               u"\U00002702-\U000027B0"
                               u"\U00002702-\U000027B0"
                               u"\U000024C2-\U0001F251"
                               u"\U0001f926-\U0001f937"
                               u"\U00010000-\U0010ffff"
                               u"\u2640-\u2642"
                               u"\u2600-\u2B55"
                               u"\u200d"
                               u"\u20b9"
                               u"\u23cf"
                               u"\u23e9"
                               u"\u231a"
                               u"\ufe0f"  # dingbats
                               u"\u3030"
                               U"\u200b"
                               U"\u034f"
                               "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', string)


def analyze_sentiment(tweet):
    # Use TextBlob to find the sentiment of each individual tweet
    analysis = TextBlob(tweet)

    # Return the sentiment value for the tweet
    if analysis.sentiment.polarity > 0:
        return 'positive'
    elif analysis.sentiment.polarity == 0:
        return 'neutral'
    else:
        return 'negative'


def analyze_tweets(f):
    # Format options used only for appearance of output in IDE window
    pandas.set_option('display.max_columns', None)

    # Read the format width text file into a dataframe and add column names
    tweet_df = pandas.read_fwf(f, header=None, colspecs=[
                               (0, 20), (20, 30), (31, 39), (39, 45), (46, -1)])
    tweet_df.columns = ['id', 'date', 'time', 'val', 'tweet']

    # Clean each tweet and remove emojis
    tweet_df['clean'] = [remove_emoji(clean_tweet(tweet)) for tweet in tweet_df['tweet']]

    # Analyze sentiment of each clean tweet and add to dataframe
    tweet_df['sentiment'] = [analyze_sentiment(
        tweet) for tweet in tweet_df['clean']]

    # Return only the clean tweet and its sentiment
    return tweet_df[['clean', 'sentiment']].copy()


def train_model(path, f):
    textgen = textgenrnn()

    sys.stdout = open(f, 'w')
    textgen.train_from_file(path, num_epochs=25,  max_gen_length=280)
    sys.stdout = sys.__stdout__


if __name__ == '__main__':
    # keyword = ''
    # sentiment = ''
    # location = ''
    # try:
    #     opts, args = getopt.getopt(argv, "hk:s:l:", ["keyword=", "sentiment=", "location="])
    # except getopt.GetoptError:
    #     print
    #     'main.py -k <keyword> -s <sentiment> -l <location>'
    #     sys.exit(2)
    # for opt, arg in opts:
    #     if opt == '-h':
    #         print
    #         'main.py -k <keyword> -s <sentiment> -l <location>'
    #         sys.exit()
    #     elif opt in ("-k", "--keyword"):
    #         keyword = arg
    #     elif opt in ("-s", "--sentiment"):
    #         sentiment = arg
    #     elif opt in ("-l", "--location"):
    #         location = arg


    for keyword in ['Apple']:
        for location in ['Los Angeles']:
            # Output file for all tweets gathered
            tweet_file = os.path.join(output_dir, keyword + '_' + location + '_all.txt')

            # Gather tweets from twitter based on keyword and location
            start = time.time()
            gather_tweets(keyword, location, tweet_file)
            get_tweet_time = time.time()
            print("Time elapsed for scraping tweets from Twitter: ", get_tweet_time - start)

            # Clean and analyze the sentiment of the gathered tweets
            start = time.time()
            tweet_set = analyze_tweets(tweet_file)
            analyze_tweet_time = time.time()
            print("Time elapsed for sentiment analysis: ", analyze_tweet_time - start)
            print(tweet_set['sentiment'].value_counts())

            # for sentiment in ['positive', 'negative', 'neutral']:
            for sentiment in ['positive']:

                # Output file for training data and generated tweets
                sentiment_file = os.path.join(output_dir, keyword + '_' + location + '_' + sentiment + '.txt')
                output_file = os.path.join(output_dir, keyword + '_' + location + '_' + sentiment + '_generated.txt')

                # Gather training set of tweets based on sentiment
                training_set = tweet_set.loc[tweet_set['sentiment'] == sentiment]
                with open(sentiment_file, 'w') as file:
                    file.writelines([line + '\n' for line in training_set['clean']])

                # Train model on tweet set
                start = time.time()
                train_model(sentiment_file, output_file)
                training_time = time.time()
                print("Time elapsed for training: ", training_time - start)


