

span = {"from":1, "to":1}
linesRead = 0
linesToRet = 0

def next():
	span["from"] = span["to"] + 1
	span["to"] = span["from"]

def inc():
	span["to"] += 1

def reset():
	span = {"from":1,"to":1}

def get():
	return {"from":span["from"], "to":span["to"]}

def lines():
	global linesRead
	toret = linesRead
	linesRead = 0
	return toret

def retLines():
	global linesToRet
	toret = linesToRet
	linesToRet = 0
	return toret
