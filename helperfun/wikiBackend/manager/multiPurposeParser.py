from fuzzywuzzy import fuzz
import itertools
from collections import Counter

from .libs import mistletoe
from .libs.mistletoe.ast_renderer import ASTRenderer
import re

def list_of_imagelinks(md_ast):
	objs = []
	if "type" in md_ast:
		if md_ast["type"] == "Image":
			objs.append(md_ast)
	if "children" in md_ast:
		for child in md_ast["children"]:
			objs += list_of_imagelinks(child)

	return objs

def list_of_textlinks(md_ast):
	objs = []
	if "type" in md_ast:
		if "Link" in md_ast["type"]:
			objs.append(md_ast)
	if "children" in md_ast:
		for child in md_ast["children"]:
			objs += list_of_textlinks(child)

	return objs

def list_of_headers(md_ast):
	objs = []
	if "type" in md_ast:
		if "Heading" in md_ast["type"]:
			objs.append(md_ast)
	if "children" in md_ast:
		for child in md_ast["children"]:
			objs += list_of_headers(child)

	return objs

def list_of_footnotes(md_ast,footnotes = False):
	objs = []
	if not footnotes:
		if "footnotes" in md_ast:
			objs += list_of_footnotes(md_ast["footnotes"],footnotes = True)
	else:
		for footnote in md_ast:
			footnote_ast = md_ast[footnote]
			target = footnote_ast[0] if 0 <= 0 < len(footnote_ast) else ""
			title = footnote_ast[1] if 0 <= 1 < len(footnote_ast) else ""
			span = footnote_ast[2] if 0 <= 1 < len(footnote_ast) else ""
			objs.append({"name":footnote, "target":target, "title":title, "span": span})

	return objs


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


def parseText(md_ast, d = None, p = 0):
	if d is None:
		d = {}
	for entry in md_ast:
		if "children" in entry:
			parseText(entry["children"],d=d,p=p)
			p+=1
		elif "text" in entry:
			if entry["text"]:
				for s in entry["text"].split():
					if s[0] in d:
						d[s[0]].append((s,p))
					else: 
						d[s[0]] = []
						d[s[0]].append((s,p))
	return d

def search(phrase, wordHash, linespan=0,filepath = None):
	def validLines(tupl):
		for t in tupl:
			found = True
			for x in tupl:
				if t == x:
					continue
				else:
					if not abs(t-x) <= int(linespan):
						found = False
						break;
			if found:
				return True

		return False

	def lines(l):

		result = set()
		if len(l) > 1:
			for e in itertools.product(*l):
				validTuple = validLines(e)
				if validTuple:
					sortedUniqueLines = tuple(sorted(set(e)))
					if len(sortedUniqueLines) > 2:
						sortedUniqueLines = (sortedUniqueLines[0],sortedUniqueLines[-1])
					result.add(sortedUniqueLines)
			return list(result)
		else:
			entry = l[0]
			return [tuple([i]) for i in entry]

	def findWord(searchword,wordlist):
		bestratio = -1
		bestmatch = None
		for wordLineTuple in wordlist:
			#word
			w = wordLineTuple[0]
			#here compare
			ratio = fuzz.ratio(w.lower(),searchword.lower())
			if ratio >= 85 and ratio > bestratio:
				bestmatch = wordLineTuple[1]

		return bestmatch

	finalResult = None
	#["hallo ich","auto meer"]
	combinations = []
	#["hallo ich"]
	abort = False
	if not type(phrase) == list:
		phrase = [w.replace(" ","") for w in phrase.split(" ")]
	for word in phrase:
		#[(word,[start])]
		if not word[:1] in wordHash:
			return None
		wordlist = wordHash[word[:1]]
		#(word,[start])
		listOfLines = findWord(word,wordlist)
		if listOfLines:			
			combinations.append(listOfLines)
		else:
			abort = True
			break;

	if abort:
		return None
	else:
		result = lines(combinations)
		l = []
		for i in result:
			a = Counter(i).most_common(1)[0]
			fullphrase = "PREVIEW NOT AVAILABLE"
			try:
				fullphrase = "...".join([wordHash["lines"][str(line)] for line in i])
			except:
				pass
			r = {"lines":i,"rating":round(i[0]/(sum(i)/len(i)),2),"fullphrase":fullphrase}
			if filepath:
				r["filepath"] = filepath
			l.append(r)
		if l:
			sortedFindings = sorted(l, key=lambda k: k['rating'], reverse=True) 
			finalResult = sortedFindings

	return finalResult


def parseContentMistletoe(content):
	tree = mistletoe.markdown(content, ASTRenderer)
	#print(tree)
	return tree

def md2html(content,path,wikilinks=None,base64PathDict = None):
	try:
		tree = mistletoe.markdown(content,path=path,wikilinks=wikilinks,base64PathDict=base64PathDict)
		return tree
	except Exception as e:
		return str(e)

def extractFiles(jsondata):
	f = []
	if "files" in jsondata:
		f += jsondata["files"]
	if "folders" in jsondata:
		for folder in jsondata["folders"]:
			f += extractFiles(folder)

	return f