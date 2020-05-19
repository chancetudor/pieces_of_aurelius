import tweepy
import statistics
from textblob import TextBlob
from os import environ

C_KEY = environ['C_KEY']
C_SECRET = environ['C_SECRET']
A_TOKEN = environ['A_TOKEN']
A_TOKEN_SECRET = environ['A_TOKEN_SECRET']


def authenticate():
    auth = tweepy.OAuthHandler(C_KEY, C_SECRET)
    auth.set_access_token(A_TOKEN, A_TOKEN_SECRET)
    return tweepy.API(auth)


def tweet(api, status):
    if isinstance(status, list):
        for t in status:
            try:
                api.update_status(t)
            except tweepy.TweepError as e:
                print(e.reason)
    else:
        try:
            api.update_status(status)
        except tweepy.TweepError as e:
            print(e.reason)


def set_line_ptr(line):
    with open('curr_line.txt', 'w+') as out_file:
        out_file.write(str(line))


def get_line_ptr():
    try:
        with open('curr_line.txt') as f:
            curr_line = f.read()
            try:
                return int(curr_line)
            except ValueError:
                return 0
    except FileNotFoundError:
        f = open('curr_line.txt', 'w+')
        f.close()
        return 0


def get_line():
    curr_line = get_line_ptr()
    with open('meditations.txt') as file:
        lines = TextBlob(file.read())
    status = str(lines.sentences[curr_line]).replace('\n', ' ').strip()
    set_line_ptr(curr_line + 1)

    return status


def find_all(find_str, sub):
    start = 0
    while True:
        start = find_str.find(sub, start)
        if start == -1:
            return
        yield start
        start += len(sub)


def find_split_index(status):
    indices = {
        ';': list(find_all(status, ';')),
        ',': list(find_all(status, ',')),
        ':': list(find_all(status, ':')),
        '?': list(find_all(status, '?')),
        '!': list(find_all(status, '!'))
    }
    index_value_list = list()
    for key, value in indices.items():
        for i in value:
            index_value_list.append(i)

    if len(index_value_list) % 2 != 0:
        split_index = statistics.median(index_value_list)

    else:
        index_value_list.sort()
        middle = int(len(index_value_list) / 2)
        split_index = index_value_list[middle]

    return split_index


def split_status(status):
    index = find_split_index(status)
    tweets_list = []
    tweet1 = status[:index + 1] + '...'
    tweet2 = status[index + 2:].strip()
    tweets_list.append(tweet1)
    tweets_list.append(tweet2)

    if len(tweet1) < 240 and len(tweet2) < 240:
        return tweets_list
    else:
        if len(tweet1) > 240:
            tweets_list[0] = split_status(tweet1)
        if len(tweet2) > 240:
            tweets_list[1] = split_status(tweet2)

    return tweets_list


def flatten_nested_list(nested_list):
    flat_list = []
    for elem in nested_list:
        if isinstance(elem, list):
            flat_list.extend(flatten_nested_list(elem))
        else:
            flat_list.append(elem)

    return flat_list


def main():
    # api = authenticate()
    api = ''
    status = get_line()
    if len(status) > 240:
        cleaned_status_list = split_status(status)
        flattened_status = flatten_nested_list(cleaned_status_list)
        tweet(api, flattened_status)
    else:
        tweet(api, status)


if __name__ == "__main__":
    main()
