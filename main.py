import os
import subprocess
import re
# TODO: Import textblob and test sentiment analysis
#from textblob import TextBlob
import pandas


get_tweet_path = 'Optimized-Modified-GetOldTweets3-OMGOT-fix-api\\GetOldTweets3-0.0.10'
outfile = 'C:\\Users\\shari\\Documents\\School\\CS 510 NLP Adv\\TermProject\\output\\output.csv'


def gather_tweets(kwd):
    # Create command to pull tweets based on a certain keyword and output to csv
    cmd = 'python cli.py -s ' + kwd + ' --csv -o ' + outfile

    # CD into directory of GetOldTweets code and run code
    os.chdir(get_tweet_path)
    p = subprocess.run(cmd)

    # # Open output file and redirect output of the GetTweet command to text file
    # with open(outfile, 'w') as out:
    #     # TODO: find out how to make this stop running ??
    #     p = subprocess.run(cmd, stdout=out, stderr=out)


def clean_tweet(tweet):
    # Strip twitter mentions (@username), punctuation and special characters and emojis, and twtter usernames (<username>)
    # TODO: figure out why this isn't capturing all emojis, website links, etc.
    return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t]) | (\w+:\ / \ / \S+) | (<[\w]+>)", " ", tweet).split())


def analyze_sentiment(tweet):
    return
    # Use TextBlob to find the sentiment of each individual tweet
    # analysis = TextBlob(tweet)
    #
    # # Return the sentiment value for the tweet
    # if analysis.sentiment.polarity > 0:
    #     return 'positive'
    # elif analysis.sentiment.polarity == 0:
    #     return 'neutral'
    # else:
    #     return 'negative'


def analyze_tweets():
    # Format options used only for appearance of output in IDE window
    pandas.set_option('display.max_columns', None)

    # Read the format width text file into a dataframe and add column names
    # tweet_df = pandas.read_fwf(outfile, header=None, colspecs=[(0, 20), (20, 30), (31, 39), (39, 45), (46, -1)])
    tweet_df = pandas.read_csv(outfile)
    tweet_df.columns = ['id', 'date', 'time', 'val', 'tweet']

    # Clean each tweet
    tweet_df['clean'] = [clean_tweet(tweet) for tweet in tweet_df['tweet']]

    # Add sentiment of each clean tweet to dataframe
    tweet_df['sentiment'] = [analyze_sentiment(tweet) for tweet in tweet_df['clean']]

    print(tweet_df.head())

    # Return only the clean tweet and its sentiment
    return tweet_df[['clean', 'sentiment']].copy()


if __name__ == '__main__':
    keyword = 'computers'
    gather_tweets(keyword)

    # tweet_set = analyze_tweets()
    #
    # # TODO: Train model
    # sentiment = 'positive'
    # training_set = [tweet for tweet in tweet_set['clean'] if tweet_set['sentiment'] == sentiment]

