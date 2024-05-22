# DEXOnlineScraper
A script to scrape all words from DEXOnline

DEXOnline only returns the first 1000 words in a query. This program scrapes almost all words based on the starting letters. It first generates all two-letter combinations. When DEXOnline reports that more than 1000 results exist for a combination, all possible three letter combinations are formed based on said combination. The procedure then iterates until no combinations return more than 1000 results.

To slightly reduce the number of requests, some filters were applied: no combinations involving k, q, w, y (letters appearing only in neologisms), an upper case letter or an empty space were considered.
