import os


root_folder =  "C:\\Users\\Andre\\Desktop\\onefilewiki"
srcPath = "C:\\Users\\Andre\\Desktop\\onefilewiki\\subfolder\\subsubfolder"
target = "C:\\Users\\Andre\\Desktop\\onefilewiki\\subfolder\\aha.md"

def _templatePathDict():
	d = {}
	for root, dirs, files in os.walk("./t", topdown=False):
		for name in files:
			d[os.path.splitext(name)[0]] = os.path.abspath(name)

	return d


def listFolders(root_folder):
	l = []
	for subdir, dirs, files in os.walk(root_folder):
		for file in files:
			#print os.path.join(subdir, file)
			filepath = subdir + os.sep + file

			l.append(subdir)

	return l

d = _templatePathDict()
print(d)