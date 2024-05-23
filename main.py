#Download almost all words from DEXOnline
#Included basic filters to perform fewer requests: no words with k, q, w, y, starting with an uppercase letter and expressions
from requests_html import HTMLSession
import itertools
from collections import defaultdict
import os
import json
import time

def generate_link(onset):
    return f'https://dexonline.ro/definitie/{onset}'

def generate_pair_onsets(chars):
    combinations = [''.join(x) + '*' for x in list(itertools.product(chars, repeat = 2))]
    return combinations

def count_words(content):
    index = content.find('<h3>')
    content = content[index:]
    count = content[:content.find('<strong>')].split()[1]
    return 0 if count == 'Niciun' else 1 if count == 'Un' else int(count)

def get_word_from_link (url, remove_expressions = True, remove_upper = True):
    word = url.split('lexem/')[1].split('/')[0]
    if remove_expressions and len(word) > 0 and len(word.split()) > 1:
        return ''
    if remove_upper and len(word) > 0 and word[0].isupper():
        return ''
    return word

def extract_words(response, remove_expressions = True, remove_upper = True):
    links = response.html.absolute_links
    links = [s for s in links if 'https://dexonline.ro/lexem/'in s]
    words = []
    for s in links:
        word = get_word_from_link(s, remove_expressions, remove_upper)
        if word != '':
            words.append(word)
    return words

def make_folder(folder_path):
    if not os.path.exists (folder_path):
        os.makedirs(folder_path)

def save_words(folder_path, onset_list, start = 2, remove_expressions = True, remove_upper = True):
    make_folder(folder_path)
    dict_satisfy = defaultdict()
    dict_exceed = defaultdict()
    words = []
    print(f'Scraping words grouped by the {start} starting characters.')
    for onset in onset_list:
        url = generate_link(onset)
        session = HTMLSession()
        response = session.get(url)
        count = count_words(response.html.html)
        if count > 0:
            if count < 1001:
                current_words = extract_words(response, remove_expressions,remove_upper)
                if len(current_words) > 0:
                    dict_satisfy[onset] = len(current_words)
                    words += current_words
            else:
                dict_exceed[onset] = count
            print(f'{count} words at {url}.')
        time.sleep(2)  
    with open(f'{folder_path}/dict_satisfy{start}.json', 'w') as f:
        json.dump(dict_satisfy, f)
    with open(f'{folder_path}/words{start}.json', 'w') as f:
        json.dump(words, f)
    if len(dict_exceed) > 0:
        with open(f'{folder_path}/dict_exceed{start + 1}.json', 'w') as f:
            json.dump(dict_exceed, f)
        return True
    return False

def write_words(folder_path, first_start, start):
    words = []
    files = [f'{folder_path}/words{i}.json' for i in range(first_start, start + 1)]
    for file in files:
        with open(file, 'r') as f:
            words += json.load(f)
    words = sorted(set(words))
    print (f'{len(words)} words found.')
    with open(f'{folder_path}/All words.txt', 'w', encoding = 'utf-8') as f:
        for word in words:
            f.write (word + '\n')

def scrape_words(folder_path, chars, start = 2, remove_expressions = True, remove_upper = True):
    onset_list = generate_pair_onsets(chars)
    ok = save_words(folder_path, onset_list, start, remove_expressions, remove_upper)
    first_start = start
    while (ok):
        start += 1
        with open(f'{folder_path}/dict_exceed{start}.json', 'r') as f:
           dict_exceed = json.load(f)
        onset_list = [x.replace('*', '') + y +'*' for x in dict_exceed.keys() for y in chars]
        ok = save_words(folder_path, onset_list, start, remove_expressions, remove_upper)
    write_words(folder_path, first_start, start) 

def main():
    folder_path = 'Saved'
    chars = 'abcdefghijlmnoprstuvxz'
    #DEXOnline only returns the first 1000 words in a query
    #We scrape words by their starting letters
    #In the beginning, all combinations of two letters are tried
    #When DEXOnline reports that more than 1000 results exists for a combination, all possible three letter combinations are formed based on said combination
    #The procedure then iterates until no combinations return more than 1000 results.
    #To slightly reduce the number of requests, some filters were applied: no combinations involving k, q, w, y, upper case letters or an empty space were considered.
    start = 2
    remove_expressions = True
    remove_upper = True
    scrape_words(folder_path, chars, start, remove_expressions, remove_upper)

if __name__ == '__main__':
    main()

