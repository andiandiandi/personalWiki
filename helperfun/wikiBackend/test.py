import socketFakeServer
import json

#jsondata = {"type": "folder", "folders": [{"type": "folder", "folders": [], "name": "wikiconfig", "files": []}], "name": "testwiki", "files": [{"content": "[I'm an inline-style link](https://www.google.com)\n\n[I'm an inline-style link with title](https://www.google.com \"Google's Homepage\")\nInline-style: \n![alt text](https://github.com/adam-p/markdown-here/raw/master/src/common/images/icon48.png \"Logo Title Text 1\")\n\n[I'm a reference-style link][Arbitrary case-insensitive reference text]\n\n[I'm a relative reference to a repository file](../blob/master/LICENSE)\n\n[You can use numbers for reference-style link definitions][1]\n\n# headertest\nparagraph under header with name headertest\n\nReference-style: \n![alt text][logo]\n\nOr leave it empty and use the [link text itself].\n\nURLs and URLs in angle brackets will automatically get turned into links. \nhttp://www.example.com or <http://www.example.com> and sometimes \nexample.com (but not on Github, for example).\n\nSome text to show that the reference links can follow later.\n\nHere's our logo (hover to see the title text):\n\n[asdas](test.py)\n\n\n\n\n\n[arbitrary case-insensitive reference text]: https://www.mozilla.org\n[1]: http://slashdot.org\n[link text itself]: http://www.reddit.com\n[logo]: https://github.com/adam-p/markdown-here/raw/master/src/common/images/icon48.png \"Logo Title Text 2\"\n\n\nfile:*\na:footnotes\nvalues:name=\"logo\" & title!=\"test\"\n\n\nfile:*\na:footnotes\nvalues:name=\"logo\" & title!=\"test\"", "path": "C:\\Users\\Andre\\Desktop\\testwiki\\asd.md"}, {"content": "# header 1\nasdasd\nasdasd\n\n[link to asd](asd.md)\n[link gdfgdfgdfgd](gfdgdfgd.md)\n[link asdasdasdasd](errsres.md)\n\nasdasd\n\n", "path": "C:\\Users\\Andre\\Desktop\\testwiki\\b.md"}, {"content": "", "path": "C:\\Users\\Andre\\Desktop\\testwiki\\test.py"}]}
jsondata = {'files': [], 'folders': [{'files': [{'path': 'C:\\Users\\Andre\\Desktop\\nowiki\\testfolder\\ddd.md', 'content': '\n![GitHub Logo](/images/logo/logo.jpg)\n![test](https://produkt-tests.com/wp-content/uploads/2018/07/IKRA-Akku-Rasenm%C3%A4her-IAM-40-4625-S-im-Test-3.jpg)\n', 'lastmodified': 1595777590.1196454}, {'path': 'C:\\Users\\Andre\\Desktop\\nowiki\\testfolder\\ff.md', 'content': '', 'lastmodified': 1595770761.4283435}], 'folders': [{'files': [], 'folders': [{'files': [], 'folders': [], 'name': 'logo', 'type': 'folder'}], 'name': 'images', 'type': 'folder'}, {'files': [{'path': 'C:\\Users\\Andre\\Desktop\\nowiki\\testfolder\\subtestfolder\\aaa.md', 'content': '', 'lastmodified': 1595797061.562074}], 'folders': [{'files': [{'path': 'C:\\Users\\Andre\\Desktop\\nowiki\\testfolder\\subtestfolder\\s\\ey.md', 'content': 'do\nasd\n\n# header1\n\nasd\n\nasd\n\n[wikilink](s/wa.md)\n\nasd\n\nasdas', 'lastmodified': 1595864128.4158976}, {'path': 'C:\\Users\\Andre\\Desktop\\nowiki\\testfolder\\subtestfolder\\s\\ka.md', 'content': '# header122\n\n[www](www.md)\n\nasdasdasdasdasdadsasdasd\n\nasd\n\nasdasd\n\n\nasdas\n\n\nasdad\nasd', 'lastmodified': 1595800700.232463}], 'folders': [{'files': [{'path': 'C:\\Users\\Andre\\Desktop\\nowiki\\testfolder\\subtestfolder\\s\\s\\dinLLY.md', 'content': '\n\n\n\n\n\n\n\n', 'lastmodified': 1595797088.8640347}, {'path': 'C:\\Users\\Andre\\Desktop\\nowiki\\testfolder\\subtestfolder\\s\\s\\ttt.md', 'content': '\n [aha](wa.md)\n\n# header99', 'lastmodified': 1595872859.9364302}, {'path': 'C:\\Users\\Andre\\Desktop\\nowiki\\testfolder\\subtestfolder\\s\\s\\www.md', 'content': 'asdasdasdasddasd\n\n[ye](../ye.md)', 'lastmodified': 1595797068.0586572}], 'folders': [], 'name': 's', 'type': 'folder'}], 'name': 's', 'type': 'folder'}], 'name': 'subtestfolder', 'type': 'folder'}], 'name': 'testfolder', 'type': 'folder'}], 'name': 'nowiki', 'type': 'folder'}



jsonsearch = {"files":{"negate":False,"values":["ka.md"]},"element":{"negate":False, "value":"headers"},"values":[{"attribute":"content","negate":False,"value":"header122"}]}
jsonsearch2 = {"files":{"negate":False,"values":["www.md"]},"element":{"negate":False, "value":"headers"},"values":[]}


changedata = {"queue": [{"type": "created", "lastmodified":2 ,"srcPath": "C:\\Users\\Andre\\Desktop\\nowiki\\testfolder\\subtestfolder\\s\\s\\fff.md", "content": "asdasd\n## header2\nasdasd\n\n#### header xxxx\naaaaaaaasdasdaasdasd\naaasd\naddssdasd\na\n# header 222\n\n# header 222\n\t"},
 {"type": "modified", "lastmodified":1, "srcPath": "C:\\Users\\Andre\\Desktop\\nowiki\\testfolder\\subtestfolder\\s\\s\\ddd.md", "content": "asdasd\n## header2\nasdasd\n\n#### header xxxx\naaaaaaaasdasdaasdasd\naaasd\naddssdasd\na\n# header 222\n\n# header 222\n\t"}]}

root_folder = "C:\\Users\\Andre\\Desktop\\nowiki"

class Socket:
	def emit(self,event,jsondata,room=None):
		print("************************************")
		print("event",event)
		print("data",jsondata)
		print("sid",room) 

d = {
    "root_folder": root_folder,
    "project_structure": jsondata
}

socket = Socket()
image = "C:\\Users\\Andre\\Desktop\\nowiki\\testfolder\\ddd.md"

onefilewiki = "C:\\Users\\Andre\\Desktop\\onefilewiki"

filename = "C:\\Users\\Andre\\Desktop\\onefilewiki\\subfolder\\ref.md"
filename2 = "C:\\Users\\Andre\\Desktop\\onefilewiki\\subfolder\\renamedpage.md"

socketFakeServer.on_initializeProject(123,onefilewiki,socket)
socketFakeServer.on_clearDB(123,onefilewiki)
socketFakeServer.on_initializeProject(123,onefilewiki,socket)
socketFakeServer.on_selImages(123,"")
socketFakeServer.on_disconnect(123)

"""

filename = "C:\\Users\\Andre\\Desktop\\nowiki\\testfolder\\images\\logo\\logo.jpg"
filename2 = "C:\\Users\\Andre\\Desktop\\nowiki\\testfolder\\images\\logo\\ogol.jpg"
socketFakeServer.on_moveFile(123,filename,filename2)
f3 = socketFakeServer.on_selFiles(123,"")
print(f3)
socketFakeServer.on_moveFile(123,filename2,filename)
f4 = socketFakeServer.on_selFiles(123,"")
print(f4)

f5 = socketFakeServer.on_selImages(123,"")
print(f5)

"""

"""
socketFakeServer.on_searchQuery(123,json.dumps(jsonsearch))
socketFakeServer.on_disconnect(123)

"""
#socketFakeServer.on_filesChanged(123,json.dumps(changedata))




#C:\Users\Andre\Desktop\nowiki
#C:\Users\Andre\Desktop\nowiki\wikiconfig
#C:\Users\Andre\Desktop\nowiki\wikiconfig\wiki.db