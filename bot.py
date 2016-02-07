#author=rhnvrm<hello@rohanverma.net>

from __future__ import absolute_import, print_function

import tweepy
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

import json
import key
global api 

from nltk.tag import pos_tag
from nltk.chunk import ne_chunk
from nltk import sent_tokenize, word_tokenize, pos_tag

TWITTERID = "@WeFoundBot"

LOST_ITEMS = {}

class StdOutListener(StreamListener):
    """ A listener handles tweets that are received from the stream.
    This is a basic listener that just prints received tweets to stdout.
    """
    def on_data(self, data):
        #this line parses the json data into a python dictionary
        d = json.loads(data)
        
        #uncomment this to explore the dictionary
        print(d , '\n')

        #uncomment this to just see the text of the tweet, simlarly you
        #can see the other fields of the dict
        #print('test: ' + d["text"] + '\n')
        
        #uncomment to to tweet from your twitter bot
        #although before tweeting you might want to implement
        #command parsing and your logic
        #api.update_status(status='[ACMSNUBOT] ' + d["text"])
        try:
            if(d and d["user"]["screen_name"] != TWITTERID):
                
                status = d["text"].lower()
                print(status)
                #remove twitter id from status
                status = ''.join(status.split(TWITTERID.lower()))
                print(status)
                clf = pos_tag(word_tokenize(status.lower()))

                #uncomment to print the data of the classified
                print( clf , '\n')

                #select all the verbs in the status
                verbs = [i[0] for i in clf if i[1][0] == 'V']
                print(verbs)
                
                verb_list_for_lost = ['lost', 'missing', 'find']
                verb_list_for_seen = ['seen', 'found', 'got', 'found']

                hash_tags = [tag.strip("#") for tag in status.split() if status.startswith("#")]

                if(any((True for x in  verbs if  x in verb_list_for_lost ))):
                    #1. Retweet it on our wall
                    pre = 'RT @' + d["user"]["screen_name"] + ' has lost something!' + '('
                    api.update_status(status= pre + status[:140 - len(pre) - 1] + ')')
                    print('ReTweeted! ' + pre)

                    #2.1 Post to that hashtag
                    have_you_seen = 'Have you seen this in your area? '
                    print ("HESTAHS\n", hash_tags)
                    for i in hash_tags :
                        print(i)
                        api.update_status(status = '#' + i + have_you_seen + status[:140 - len(have_you_seen) - len(i) - 2])
                        print('tweeted to '+ i)
                    #2.2 Post to people in that area

                    #3. add to buffer and check

                    nouns = [i[0] for i in clf if i[1][0] == 'N']

                    for i in nouns:
                        LOST_ITEMS[i] = d

                    print(LOST_ITEMS)


                elif(any((True for x in  verbs if  x in verb_list_for_seen ))):
                    #1. Retweet it on our wall
                    pre = 'RT @' + d["user"]["screen_name"] + ' has found something!' + '('
                    api.update_status(status= pre + status[:140 - len(pre) - 1] + ')')
                    print('ReTweeted! ' + pre)
                    #2. Post to people in that area

                    #3.  check buffer dict and if exists tweet

                    nouns = [i[0] for i in clf if i[1][0] == 'N']

                    for i in nouns:
                        if i in LOST_ITEMS:
                            api.update_status('MATCH FOUND! @' + LOST_ITEMS[i]["user"]["screen_name"] + ' @' + d["user"]["screen_name"]) #todo
                
                
            else:
                print("Error in reading Tweet\n")
        except:
            print("error\n")
        

        return True

    def on_error(self, status):
        print("Error: " + repr(status) )

if __name__ == '__main__':
    l = StdOutListener()
    auth = OAuthHandler(key.consumer_key, key.consumer_secret)
    auth.set_access_token(key.access_token, key.access_token_secret)

    api = tweepy.API(auth)


    stream = Stream(auth, l)
    #change filters to listen to various types of tweets
    #eg try 'coldplay', '@rhnvrm', '#ACMSNU' etc
    #f = ['@tehDuckFactory', 'lost', 'find', 'help']
    #f = ['lost dog']
    
    #read only tweets only tweets in which you are mentioned
    filter = [TWITTERID]
    stream.filter(track=filter, async=True)
