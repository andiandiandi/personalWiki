import json
import re
from fuzzywuzzy import fuzz

import itertools
from collections import Counter

a = """
{
	"type": "Document",
	"footnotes": {},
	"children": [
		{
			"type": "Paragraph",
			"span": {
				"start": 1,
				"read": 1
			},
			"children": [
				{
					"type": "RawText",
					"content": "das haus am meer.",
					"span": {
						"start": 1,
						"read": 1
					}
				}
			]
		},
		{
			"type": "Paragraph",
			"span": {
				"start": 3,
				"read": 1
			},
			"children": [
				{
					"type": "RawText",
					"content": "ich habe ges\u00fcndigt.",
					"span": {
						"start": 3,
						"read": 1
					}
				}
			]
		},
		{
			"type": "Heading",
			"span": {
				"start": 4,
				"read": 1
			},
			"level": 1,
			"children": [
				{
					"type": "RawText",
					"content": "header",
					"span": {
						"start": 4,
						"read": 1
					}
				}
			]
		},
		{
			"type": "Paragraph",
			"span": {
				"start": 5,
				"read": 1
			},
			"children": [
				{
					"type": "RawText",
					"content": "abschnitt 3",
					"span": {
						"start": 5,
						"read": 1
					}
				}
			]
		},
		{
			"type": "Paragraph",
			"span": {
				"start": 7,
				"read": 2
			},
			"children": [
				{
					"type": "RawText",
					"content": "das ist ein haus. es ist sehr sch\u00f6n ist halt echt so muss du mir glaub es ist das beste h\u00e4uschen was du je gesehen hast glaub mir",
					"span": {
						"start": 7,
						"read": 1
					}
				},
				{
					"type": "LineBreak",
					"soft": true,
					"content": "",
					"span": {
						"start": 7,
						"read": 1
					}
				},
				{
					"type": "RawText",
					"content": "wenn du mir nicht glaubst dann glaub halt nicht.",
					"span": {
						"start": 8,
						"read": 1
					}
				}
			]
		}
	]
}
"""

d = json.loads(a)

def textDict(md_ast):
	l = []
	if "children" in md_ast:
		for entry in md_ast["children"]:
			l += textDict(entry)
	elif "content" in md_ast:
			content = re.sub('\W+',' ', md_ast["content"]).strip()
			if content:
				l.append({"start":md_ast["span"]["start"],"read":md_ast["span"]["read"],"content": content})
	return l



def createWordHash(textDict):
	d = {}
	d["lines"] = {}
	for entry in textDict:
		content = entry["content"]
		d["lines"][entry["start"]] = content
		for word in content.split(" "):
			if word:
				if word[:1] not in d:
					d.setdefault(word[:1],[]).append((word,list(set([entry["start"]]))))
				else:
					#(word,[start,..])
					found = False
					for e in d[word[:1]]:
						if e[0] == word:
							e[1].append(entry["start"])
							found = True
							break
					if not found:
						d[word[:1]].append((word,list(set([entry["start"]]))))

	return d

k = textDict(d)
print(k)
print("____")

rr = createWordHash(k)
print(rr)
print("***********")
#das haus
def search(phrase, wordHash, linespan=0,filepath = None):
	def validLines(tupl):
		for t in tupl:
			found = True
			for x in tupl:
				if t == x:
					continue
				else:
					if not abs(t-x) <= linespan:
						found = False
						break;
			if found:
				print("found:",tupl)
				return True

		print("not found:",tupl)
		return False

	def lines(l):

		result = set()
		if len(l) > 1:
			for e in itertools.product(*l):
				validTuple = validLines(e)
				if validTuple:
					sortedUniqueLines = tuple(sorted(set(e)))
					print("sortedUniqueLines",sortedUniqueLines)
					if len(sortedUniqueLines) > 2:
						sortedUniqueLines = (sortedUniqueLines[0],sortedUniqueLines[-1])
					result.add(sortedUniqueLines)
				print("_______")
			return list(result)
		else:
			entry = l[0]
			return [tuple([i]) for i in entry]

	def findWord(searchword,wordlist):
		bestratio = -1
		bestmatch = None
		for wordLineTuple in wordlist:
			print("wordLineTuple:",wordLineTuple)
			#word
			w = wordLineTuple[0]
			#here compare
			ratio = fuzz.ratio(w.lower(),searchword.lower())
			print("ratio",ratio)
			if ratio >= 85 and ratio > bestratio:
				bestmatch = wordLineTuple[1]

		return bestmatch

	finalResult = None
	#["hallo ich","auto meer"]
	print("phrase:",phrase)
	combinations = []
	#["hallo ich"]
	abort = False
	for word in [w.replace(" ","") for w in phrase.split(" ")]:
		#[(word,[start])]
		if not word[:1] in wordHash:
			return None
		wordlist = wordHash[word[:1]]
		#(word,[start])
		print("wordlist:",wordlist)
		listOfLines = findWord(word,wordlist)
		print("lifoflines",listOfLines)
		if listOfLines:			
			combinations.append(listOfLines)
		else:
			abort = True
			break;

	if abort:
		return None
	else:
		print("combinations",combinations)
		result = lines(combinations)
		print("result",result)
		l = []
		for i in result:
			a = Counter(i).most_common(1)[0]
			print("A",a)
			fullphrase = "PREVIEW NOT AVAILABLE"
			try:
				fullphrase = "...".join([wordHash["lines"][line] for line in i])
			except:
				pass
			r = {"lines":i,"rating":round(i[0]/(sum(i)/len(i)),2),"fullphrase":fullphrase}
			if filepath:
				r["filepath"] = filepath
			l.append(r)
		print("result",result)
		if l:
			sortedFindings = sorted(l, key=lambda k: k['rating'], reverse=True) 
			finalResult = sortedFindings

	return finalResult

s = search("das haus nicht", rr,linespan=10,filepath="newfile.md")
print(s)