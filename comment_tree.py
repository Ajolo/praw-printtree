# ~~~~~~~~~~~~~~~
# Comments
# ~~~~~~~~~~~~~~~

'''
The following comment-tree project is intended to leverage PRAW's existing
GET-comment functionality to create a comment tree visualization within the
command line

Reference:
- https://praw.readthedocs.io/en/latest/index.html

Setup process:
- brew upgrade python
- pip3.7 install --upgrade pip
- pip3.7 install praw termcolor 
- run me with 'python3.7 comment_tree.py'

Reddit API access
- https://www.reddit.com/prefs/apps, select create application
- select 'script' radio button
- use the client id and secret to create the instance object 

Todo: 
- PRAW module incorporation
    - fork latest PRAW version and create new comment_tree module, 
        - perhaps as a method in submission.comments.xxx
    - verify that works as intended
        - will need to change oAuth behavior, as users would already be logged in
            - this is probably already handled elsewhere in PRAW
        - verify that modules importing given dependencies would work 
- option to export comment tree as .txt
''' 


# ~~~~~~~~~~~~~~~
# Imports
# ~~~~~~~~~~~~~~~

import praw, sys, itertools, os, textwrap
from termcolor import colored

# ~~~~~~~~~~~~~~~
# PRAW Instance Init
# ~~~~~~~~~~~~~~~

reddit = praw.Reddit(client_id='6cAYRsnb9XstmA',
                    client_secret='jBO6jTlJ36lTFiICFHmsMeOF7SM',
                    user_agent='test script by /u/Ajolo',
                    username='Ajolo',
                    password='redacted')


# ~~~~~~~~~~~~~~~
# Get command line input 
# ~~~~~~~~~~~~~~~
'''
print("Get the current top post of the given subreddit:")
targetSubreddit = input("--> /r/") # ie: seattlewa+seattle
targetURL = input("--> URL: ")
commentDepth = input("--> Depth: ")
topCommentLimit = input("--> Number of top comments: ")
'''


# ~~~~~~~~~~~~~~~
# Globals
# ~~~~~~~~~~~~~~~

topCommentLimit = 100 # only get the top x comments 
commentDepth = 10 # a depth of 0 or 1 would only retrieve top level comments
# totalCommentLimit = xx # hard comment display limit
trimNegativeComments = True

# create the submission instance based on given URL
# submission = reddit.submission(url=targetURL)

# color code comments based on depth
# termcolor options: grey red green yellow blue magenta cyan white
colorOrder = ['green', 'magenta', 'cyan', 'yellow', 'blue', 'red']


# ~~~~~~~~~~~~~~~
# Comment parsing
# ~~~~~~~~~~~~~~~

def getChildComments(comment, currentDepth):
    # recursively get comment data
    currentDepth += 1
    for reply in itertools.islice(comment.replies, 0, 5):
        if trimNegativeComments == True and reply.score < 1:
            return
        printCommentBreak(currentDepth)
        printCommentData(reply, currentDepth)
        if currentDepth < commentDepth and reply.replies:
            getChildComments(reply, currentDepth)

def printSubmission(submission):
    currentDepth = 0
    # print post body
    printPostBody(submission)
    # print comment tree
    # first trim MoreComments from forest 
    submission.comments.replace_more(limit=0)
    for comment in itertools.islice(submission.comments, 0, topCommentLimit):
        if trimNegativeComments == True and comment.score < 1:
            break
        else:
            printCommentBreak(currentDepth)
            printCommentData(comment, currentDepth)
            # continue down this path
            if commentDepth > 1:
                getChildComments(comment, currentDepth)
    print('\n')

def printCommentData(comment, currentDepth):
    colorIndex = currentDepth % 6
    indent = (' ' * (currentDepth+1))
    bodyIndent = (' ' * (currentDepth+2) + colored(('|'), colorOrder[colorIndex])+ ' ')
    print(indent, end = ' ')
    print(colored(('|'), colorOrder[colorIndex]), end = ' ')
    print('score:', comment.score, '||', end = ' ')
    if comment.is_submitter:
        print('author:', comment.author, "[OP]", end = ' ')
    else:
        print('author:', comment.author, end = ' ')
    print("||", ' reply to:', comment.parent().author)
    print(indent, colored(('|'), colorOrder[colorIndex]))
    terminalWidth = os.get_terminal_size().columns
    print(textwrap.fill(comment.body, width = terminalWidth, initial_indent = \
        bodyIndent, subsequent_indent = bodyIndent))
        
def printCommentBreak(currentDepth):
    colorIndex = currentDepth % 6
    terminalWidth = os.get_terminal_size().columns
    indent = (' ' * (currentDepth+1))
    print(indent, '+',colored('-' * (terminalWidth - (len(indent)+5)), \
        colorOrder[colorIndex]))

def printBodyBreak():
    terminalWidth = os.get_terminal_size().columns
    print(' +', '-' * (terminalWidth - 5))

def printPostBody(submission):
    printBodyBreak()
    terminalWidth = os.get_terminal_size().columns
    print(textwrap.fill(submission.title, width = terminalWidth - 5, \
        initial_indent = ' | ', subsequent_indent = ' | '))
    print(' | ', '\n', '|', end = ' ')
    print('score:', submission.score, end = ' ')
    print('||', 'author:', submission.author, '\n', '| ')
    if submission.selftext:
        print(textwrap.fill(submission.selftext, width = terminalWidth - 5, \
        initial_indent = ' | ', subsequent_indent = ' | '))
    else:
        print(textwrap.fill(submission.url, width = terminalWidth - 5, \
        initial_indent = ' | ', subsequent_indent = ' | '))


def getCurrentTopPost(targetSubreddit):
    try:
        reddit.subreddits.search_by_name(targetSubreddit, exact=True)
    except:
        print("unable to find specified subreddit")
        return
    print('Retrieving the current top post from /r/' + targetSubreddit)
    targetPosts = reddit.subreddit(targetSubreddit).hot(limit=1)
    for submission in targetPosts:
        printSubmission(submission)


# ~~~~~~~~~~~~~~~
# Function Calls
# ~~~~~~~~~~~~~~~

# get a top post for specified sub
# getCurrentTopPost(targetSubreddit)
# or directly specify url/submission:
# printSubmission(submission)

