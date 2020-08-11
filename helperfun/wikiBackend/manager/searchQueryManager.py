import shlex
import json

from . import responseGenerator


def supportedArg(arg):
	supportedArgs = ["s","f","fe","t","n","d"]
	return arg in supportedArgs

def supportedTagPhrase(phrase):
	supportedTagPhrases = ["#","!","[","^"]
	return phrase in supportedTagPhrases

def parseQuery(queryString):
	if not queryString:
		return responseGenerator.createExceptionResponse("empty query string")
	PHRASELIMIT = 6
	query_tokens = shlex.split(queryString)
	phrase=[]
	args ={}
	addToSearchHistory = False
	if query_tokens[0] == "+":
		addToSearchHistory = True
		query_tokens.pop(0)
	skipNext = False
	for i,word in enumerate(query_tokens):
		if skipNext:
			skipNext=False
			continue
		if not word.startswith("-"):
			phrase.append(word)
			if len(phrase) > PHRASELIMIT:
				return responseGenerator.createExceptionResponse("too many words in phrase specified, limit is: " + PHRASELIMIT)
		else:
			word = word.replace("-","")
			if not supportedArg(word):
				return responseGenerator.createExceptionResponse("unsupported argument: " + word)
			elif word == "d":
				rawQuery = queryString[:-3]
				return responseGenerator.createSuccessResponse(json.dumps({"type":"delete","query":rawQuery}))
			elif word == "t":
				args[word] = None
				skipNext = False
			elif word == "n":
				args[word] = None
				skipNext = False
			elif word in ["fe","f"]:
				if i+1 >= len(query_tokens):
					return responseGenerator.createExceptionResponse("corrupted search-string: no argument value found for: " + word)
				argValue = query_tokens[i+1]
				if argValue.startswith("-"):
					return responseGenerator.createExceptionResponse("arguments corrupted, form should be '-arg argvalue'")
				args[word] = [t for t in argValue.split(",")] if len(argValue.split(",")) > 1 else [argValue]
				skipNext = True
			else:
				if i+1 >= len(query_tokens):
					return responseGenerator.createExceptionResponse("corrupted search-string: no argument value found for: " + word)
				argValue = query_tokens[i+1]
				if argValue.startswith("-"):
					return responseGenerator.createExceptionResponse("arguments corrupted, form should be '-arg argvalue'")
				args[word] = argValue
				skipNext = True

	if not phrase:
		return responseGenerator.createExceptionResponse("no search-phrase specified")

	if "t" in args:
		for word in phrase:
			if not supportedTagPhrase(word):
				return responseGenerator.createExceptionResponse("unsupported tag phrase: " + word)
		return responseGenerator.createSuccessResponse(json.dumps({"type":"tagsearch",
																	"phrase":phrase,
																	"args":args,
																	"searchhistory":" ".join(query_tokens) if addToSearchHistory else None}))
	else:
		return responseGenerator.createSuccessResponse(json.dumps({"type":"fulltextsearch",
																	"phrase":phrase,
																	"args":args,
																	"searchhistory":" ".join(query_tokens) if addToSearchHistory else None}))

def getElement(tag):
	if tag == '#':
		return "headers"
	elif tag == "!":
		return "imagelinks"
	elif tag == "[":
		return "textlinks"
	elif tag == "^":
		return "footnotes"

def jsondataTagQuery(phrase,args):
	if not phrase or len(phrase) >1:
		return responseGenerator.createExceptionResponse("Tag-Query received too many words in phrase, only 1 allowed: " + phrase)
	else:
		files = {}
		element = {}
		elementname = getElement(phrase[0])
		if not elementname:
			return responseGenerator.createExceptionResponse("Elementname not supported: " + phrase[0])
		else:
			element["value"] = elementname
		if "f" in args:
			files["negate"] = False
			files["values"] = args["f"]
		elif "fe" in args:
			files["negate"] = True
			files["values"] = args["fe"]
		else:
			files["negate"] = False
			files["values"] = []
		if "n" in args:
			element["negate"] = True
		else:
			element["negate"] = False

		return {"files":files,"element":element,"values":[]}

def jsondataFulltextQuery(phrase,args):
	span = 99999999
	files = []
	files_exclude = None
	if "s" in args:
		span = args["s"]
	if "fe" in args:
		files = args["fe"]
		files_exclude = True
	elif "f" in args:
		files = args["f"]
		files_exclude = False

	return {"phrase":phrase,"files":files,"files_exclude":files_exclude,"span":span}
