import os
import subprocess
import re
from textblob import TextBlob
import pandas
from textgenrnn import textgenrnn


get_tweet_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.join('Optimized-Modified-GetOldTweets3-OMGOT-fix-api', 'GetOldTweets3-0.0.10'))
outfile = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.join('output', 'output.txt'))


def gather_tweets(kwd):
    # Create command to pull tweets based on a certain keyword and output to csv
    # Limit (increments of 20) - we will investigate how this impacts our results
    cmd = 'python cli.py -s ' + kwd + ' --limit 1000 --links exclude --lang en --near Chicago'

    # CD into directory of GetOldTweets code and run code
    os.chdir(get_tweet_path)

    # Open output file and redirect output of the GetTweet command to text file
    with open(outfile, 'w') as out:
        p = subprocess.run(cmd, stdout=out, stderr=out)


def clean_tweet(tweet):
    # Strip twitter mentions (@username), punctuation and special characters and emojis, and twtter usernames (<username>)
    # TODO: get rid of website links
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


def analyze_tweets():
    # Format options used only for appearance of output in IDE window
    pandas.set_option('display.max_columns', None)

    # Read the format width text file into a dataframe and add column names
    tweet_df = pandas.read_fwf(outfile, header=None, colspecs=[
                               (0, 20), (20, 30), (31, 39), (39, 45), (46, -1)])
    tweet_df.columns = ['id', 'date', 'time', 'val', 'tweet']

    # Clean each tweet
    tweet_df['clean'] = [remove_emoji(clean_tweet(tweet)) for tweet in tweet_df['tweet']]

    # Add sentiment of each clean tweet to dataframe
    tweet_df['sentiment'] = [analyze_sentiment(
        tweet) for tweet in tweet_df['clean']]

    # Return only the clean tweet and its sentiment
    return tweet_df[['clean', 'sentiment']].copy()


def train_model(path):
    textgen = textgenrnn()

    # TODO: Explore number of epochs and results
    textgen.train_from_file(tweet_file, num_epochs=1)

    # Generate lots of examples
    # TODO: explore temperature - modify length of output
    print(textgen.generate(10, temperature=0.5))

    # TODO: Output generated text to text file

if __name__ == '__main__':
    keyword = 'IPhone'
    gather_tweets(keyword)

    tweet_set = analyze_tweets()
    print(tweet_set['sentiment'].value_counts())

    sentiment = 'positive'
    training_set = tweet_set.loc[tweet_set['sentiment'] == sentiment]

    tweet_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.join('output', 'training_tweets.txt'))
    with open(tweet_file, 'w') as f:
        f.writelines([line + '\n' for line in training_set['clean']])

    train_model(tweet_file)


