from nltk.stem import PorterStemmer
import re

userSearch = input('Search: ')

tokens = re.findall(r'\w+', userSearch.lower(), flags=re.ASCII)

ps = PorterStemmer()
stemmedTokens = list(map(lambda token: ps.stem(token), tokens))


print(stemmedTokens)