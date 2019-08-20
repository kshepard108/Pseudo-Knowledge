from psaw import PushshiftAPI
import praw
import prawcore
import pandas as pd
import datetime as dt
import time
import pprint

start_sub_search = time.time()

api = PushshiftAPI()

# Declare the keyword, subreddit, and time period you want to use for this test.
keyword = 'Hillary'
sub = 'The_Donald'
start_date = int(dt.datetime(2019, 2, 6).timestamp())
end_date = int(dt.datetime(2019, 8, 6).timestamp())

# Conduct a PushShift query using the the above paramemters.
# Resulting submissions are saved into a list called subs, short for "submissions".
submissions = api.search_submissions(q = keyword,
                            after = start_date,
                            before = end_date,
                            subreddit = sub,
                            filter = ["id"])

results = []
numResults = 0
for i in submissions:
    item = str(i)
    results.append(item.split('id=\'')[1].split('\', created=')[0])
    numResults = numResults + 1

# Print the id of each submission and the total number of results.
end_sub_search = time.time()
print("Total submission search runtime: " + str(end_sub_search - start_sub_search))
print(results)
print(numResults)


'''------------------------------------------------------------------'''


# Method to convert UTC time into comprehensible format for 'created' column of table.
def get_date(created):
    return dt.datetime.fromtimestamp(created)

# Used to measure total time of process.
start_comment_search = time.time()

# Creates Reddit instance.
# You can log into an account by completing the fields below.
reddit = praw.Reddit(client_id='client_id',
                     client_secret='client_secret',
                     password='password',
                     user_agent='user_agent',
                     username='username')

# Instantiating the dictionary, which is converted into and saved as a CSV using pandas.
storage_dict = {"title": [],
                "author": [],
                "body": [],
                "permalink": [],
                "score": [],
                "upvote_ratio": [],
                "num_comments": [],
                "id": [],
                "parent_id": [],
                "url": [],
                "number": [],
                "created": []}

# Choose subreddit by changing string.
subreddit = reddit.subreddit(sub)

# IMPORTANT
# Comment out the subsequent line if accessing a non-quarantined subreddit.
subreddit.quaran.opt_in()

# Select posts of interest from subreddit.
# Ignore any posts that do not have comments, as we are looking for social interactions.
new_posts = []
count = 0
for r in results:
    if reddit.submission(id=r).comments.__len__() > 0:
        new_posts.append(reddit.submission(id=r))
        # print(r)
        count = count+1
    if count > 1000:
        break
print(count)


# Value used to keep track of submission #.
thread_num = 1
# Value used to keep track of the current dictionary 'row', used to determine comment nesting.
data_num = 0
# Loop through the posts of interest and add info to dictionary.
for post in new_posts:
    '''print("Submission: " + str(post))
    print("Thread num: " + str(thread_num))
    print("Data num: " + str(data_num))'''
    storage_dict["title"].append(post.title)
    storage_dict["author"].append(post.author)
    storage_dict["body"].append(post.selftext)
    storage_dict["permalink"].append(post.permalink)
    storage_dict["score"].append(post.score)
    storage_dict["upvote_ratio"].append(post.upvote_ratio)
    storage_dict["num_comments"].append(post.num_comments)
    storage_dict["id"].append(post.id)
    storage_dict["parent_id"].append('N/A')
    storage_dict["url"].append(post.url)
    storage_dict["number"].append(thread_num)
    storage_dict["created"].append(post.created_utc)
    thread_num = thread_num + 1
    data_num = data_num + 1
    print("Ready to loop through comments!")
    # Loop through all comments on posts and add info to dictionary.
    post.comments.replace_more(limit=None)
    #print(len(post.comments.list()))
    for comment in post.comments.list():
        #print("Data num: " + str(data_num))
        storage_dict["title"].append('N/A')
        storage_dict["author"].append(comment.author)
        storage_dict["body"].append(comment.body)
        storage_dict["permalink"].append('N/A')
        storage_dict["score"].append(comment.score)
        storage_dict["upvote_ratio"].append('N/A')
        storage_dict["num_comments"].append('N/A')
        storage_dict["id"].append(comment.id)
        storage_dict["parent_id"].append(comment.parent_id)
        storage_dict["url"].append('N/A')
        storage_num = data_num - 1
        count = 1
        add = "t3_"
        #print("We're looking for the ID: " + str(comment.parent_id))
        while (storage_dict["id"][storage_num]) != comment.parent_id[3:]:
            #print("The ID at data_num: " + str(storage_num) + " is: " + str(storage_dict["id"][storage_num]))
            if (storage_dict["parent_id"][storage_num]) == comment.parent_id:
                #print("We've got a match!")
                count = count + 1
            storage_num = storage_num - 1
        number_string = ''
        #print("number string is " + number_string)
        number_string = number_string + str(storage_dict["number"][storage_num])
        #print("adding " + str(storage_dict["number"][storage_num]))
        number_string = number_string + "_" + str(count)
        #print("adding " + str(count))
        storage_dict["number"].append(number_string)
        storage_dict["created"].append(comment.created_utc)
        data_num = data_num + 1

'''I used the print statements to help me troubleshoot the process of recording comment nesting.
They are also helpful for following the program because they display the number of the current submission
and the IDs printing indicates that the program has finished loading the comments, and is determining nesting.'''

# Convert to CSV.
storage_data = pd.DataFrame(storage_dict)

_timestamp = storage_data["created"].apply(get_date)
topics_data = storage_data.assign(timestamp=_timestamp)

file_name = 'reddit_scrape_' + keyword + '.csv'

topics_data.to_csv(file_name, index=False)
end_comment_search = time.time()
# Print total runtime.
print("Total comment search runtime: " + str(end_comment_search - start_comment_search))
print(numResults)