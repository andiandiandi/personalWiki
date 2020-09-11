import os
import datetime

#usable variables:
#$time
#$datetime
#$date
#$wikipage

def templatePathDict():
	d = {}
	currentDir = os.path.dirname(os.path.abspath(__file__))
	wikiTemplatesDir = os.path.join(currentDir,'wikiTemplates')
	for root, dirs, files in os.walk(wikiTemplatesDir, topdown=False):
		for name in files:
			d[os.path.splitext(name)[0]] = os.path.join(wikiTemplatesDir,name)

	return d

def _templateVariablesDict(wikipageName):
	return {"$wikipage":wikipageName,
			"$datetime": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
			"$date": str(datetime.date.today()),
			"$time": datetime.datetime.now().strftime("%H:%M:%S")}

def getContent(templatename,wikipageName):
	templatePathD = templatePathDict()
	templateVariablesDict = _templateVariablesDict(wikipageName)
	if templatename in templatePathD:
		path = templatePathD[templatename]
		with open(path,"r") as file:
			content = file.read()
			for templateVariable,replacement in templateVariablesDict.items():
				if templateVariable in content:
					content = content.replace(templateVariable,replacement)

			return content

	return None
