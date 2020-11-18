import pandas as pd
from os import listdir
import re

# a path to the folder with TXT files that contain scraped messages ...
# ... from each Slack user that you want to analyse
scraped_messages_folder = 'team/'

# creating an empty list that will be populated with names of TXT files ...
# ... that will be used as identifiers (names of Slack users)
all_users = []

# creating an empty dataframe that will be populated with counts of words ...
# ... from each Slack user
all_together = pd.DataFrame()

# opening each file from the folder
for file in listdir(scraped_messages_folder):
    f = open(scraped_messages_folder + file, 'r', encoding='utf8')
    all_words = f.read()
    f.close()
    
    # getting the user's name from the name of the file and adding it to the list
    user_name = file.rsplit('.',1)[0]
    all_users.append(user_name)
    
    # ________
    #
    # Part I. Data cleaning (removing links, punctuation, numbers, stopwords, etc.)
    # ________
    #
    
    # removing links
    all_words = re.sub('http[:\.\?\&\%\@\+_#=\-/A-Za-z0-9]*', '', all_words)

    # removing special characters and punctuation
    all_words = re.sub('[\?\!\.,:;”“«»’‘•><—=+"()/\&\*\-\{\}]', '', all_words)
    all_words = re.sub("[']", '', all_words)

    # unifying words by making them all lowercase
    all_words = all_words.lower()
    
    # removing messages that say that the user just uploaded a file
    all_words.replace('uploaded a file', '')
    
    # removing names of images; other file extensions don't appear in text messages (as of April 2020)
    all_words = re.sub('[A-Za-z]*\.jpg', '', all_words)
    all_words = re.sub('[A-Za-z]*\.png', '', all_words)
    all_words = re.sub('[A-Za-z]*\.gif', '', all_words)
    
    # removing numbers
    all_words = re.sub('[0-9]', '', all_words)

    # removing mentions and other words that start with @, except '@here'
    all_words = re.sub('(?!@here)@[a-zA-Z]*', '', all_words)

    # defining word combinations (up to 3) that should be treated as 1 word in statistics
    combined_words = ['ab test',
                      'ab testing',
                      'google analytics',
                      'dynamic yield',
                      'product analytics',
                      'is down',
                      'stand up',
                      'feel better',
                      'product owner',
                      'materialized view']    
    
    for combined_word in combined_words:
        all_words = all_words.replace(combined_word, combined_word.replace(' ','').replace(' ',''))
    
    # creating a set of stop words, the words that will have little value in analysing slack users, ...
    # ... so they should be removed from the statistics
    stopwords = {"a","about","above","after","again","against","ain","all","also","am","an","and","any","are",
                 "aren","arent","as","at","be","because","been","before","being","below","between",
                 "both","but","by","can","couldn","couldnt","did","didn","didnt","do","does","doesn",
                 "doesnt","doing","don","dont","down","during","each","few","for","from","further",
                 "had","hadn","hadnt","has","hasn","hasnt","have","haven","havent","having","he","her",
                 "here","hers","herself","him","himself","his","how","i","im","ill","ive","if","in",
                 "into","is","isn","isnt","it","its","its","itself","just","me","mightn","mightnt",
                 "more","most","mustn","mustnt","my","myself","needn","neednt","no","nor","not","now",
                 "o","of","off","on","one","once","only","or","other","our","ours","ourselves","out","over",
                 "own","re","s","same","shan","shant","she","shes","should","shouldve","shouldn",
                 "shouldnt","since","so","some","still","such","than","that","thatll","the","their","theirs","them",
                 "themselves","then","there","these","they","this","those","through","to","too","under",
                 "until","up","ve","very","was","wasn","wasnt","we","were","weren","werent","what",
                 "when","where","which","while","who","whom","why","will","with","won","wont","would","wouldn",
                 "wouldnt","you","youd","youll","youre","youve","your","yours","yourself","yourselves"}
    
    # creating a list of all words
    words = all_words.split()
    
    # creating a variable that will be appended with words that are not stop words
    updated_all_words = []
    
    for word in words:
        if word not in stopwords:
            updated_all_words.append(word)
    
    # ________
    #
    # Part II. Counting words for each Slack user
    # ________
    #
    
    # creating an empty dictionary that will be populated with counts of words
    counts = dict()
    
    # counting the number of each word
    for word in updated_all_words:
        if word in counts:
            counts[word] += 1
        else:
            counts[word] = 1

    # transforming a dictionary into a dataframe
    word_items = counts.items()
    word_list = list(word_items)
    word_df = pd.DataFrame(word_list)

    # defining columns in the dataframe
    word_df.columns = ['word', user_name]
    
    # sorting columns by user names
    word_df = word_df.sort_values(user_name, ascending=False)
    
    # using 'word' column as index
    word_df.index = word_df.word
    
    # deleting the 'word' column (not index)
    word_df = word_df.drop('word', axis='columns')

    # concatenating the dataframe horizontally (axis=1) with the counts of words for each user
    all_together = pd.concat([all_together, word_df], axis=1)
    
    print('Words from ', user_name, ' are analysed', sep='')
    

# ________
#
# Part III. Using the formula to get the most unique words for each user
# ________
#    
    
# creating a 'Total' row and column
all_together.loc["Total"] = all_together.sum(axis=0)
all_together["Total"] = all_together.sum(axis=1)

for user in all_users:
    column_name = user+'_est_uniq'
    all_together[column_name] = all_together[user]**2/all_together["Total"]*all_together.loc["Total", "Total"]/all_together.loc["Total", user]

print('Done!')
print('')
    
# exporting a CSV file with the most unique words estimation
all_together.to_csv('unique_words.csv', encoding='utf-8-sig')

print("The data is exported to 'unique_words.csv'.")
print("The output consists of word counts and estimated word uniqueness.")
print("Use the words that scored the highest for each user and also the highest among other users to identify the most unique words.")
#print(all_together)