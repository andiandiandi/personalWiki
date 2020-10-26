import re

wps = 8

def countWordsCharReadtime(textString):
	wordList = re.split("\s+|-", textString)
	print("WORDLIST",wordList)
	words = len(wordList)
	if words == 1 and not wordList[0]:
		words = 0
	chars = 0
	if words > 0:
		for word in wordList:
			chars += len(word)

	readtime = int(words/wps)
	if readtime <= 0:
		readtime = 1

	return {"words":words,"chars":chars, "readtimeInSeconds" : readtime}

def convert(seconds): 
    seconds = seconds % (24 * 3600) 
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
      
    return "%02d:%02d" % (minutes, seconds) 
      
