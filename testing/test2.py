import os


root_folder =  "C:\\Users\\Andre\\Desktop\\onefilewiki"
srcPath = "C:\\Users\\Andre\\Desktop\\onefilewiki\\subfolder\\subsubfolder"
target = "C:\\Users\\Andre\\Desktop\\onefilewiki\\subfolder\\aha.md"


def listFolders(root_folder):
	l = []
	for subdir, dirs, files in os.walk(root_folder):
		for file in files:
			#print os.path.join(subdir, file)
			filepath = subdir + os.sep + file

			l.append(subdir)

	return l

print(l)