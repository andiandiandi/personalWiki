import socketFakeServer
				

#w = DbWrapper()
#w.create_connection()
#w.prepare_tables()

#jsondata = {"type": "folder", "folders": [{"type": "folder", "folders": [], "name": "wikiconfig", "files": []}], "name": "testwiki", "files": [{"content": "[I'm an inline-style link](https://www.google.com)\n\n[I'm an inline-style link with title](https://www.google.com \"Google's Homepage\")\nInline-style: \n![alt text](https://github.com/adam-p/markdown-here/raw/master/src/common/images/icon48.png \"Logo Title Text 1\")\n\n[I'm a reference-style link][Arbitrary case-insensitive reference text]\n\n[I'm a relative reference to a repository file](../blob/master/LICENSE)\n\n[You can use numbers for reference-style link definitions][1]\n\n# headertest\nparagraph under header with name headertest\n\nReference-style: \n![alt text][logo]\n\nOr leave it empty and use the [link text itself].\n\nURLs and URLs in angle brackets will automatically get turned into links. \nhttp://www.example.com or <http://www.example.com> and sometimes \nexample.com (but not on Github, for example).\n\nSome text to show that the reference links can follow later.\n\nHere's our logo (hover to see the title text):\n\n[asdas](test.py)\n\n\n\n\n\n[arbitrary case-insensitive reference text]: https://www.mozilla.org\n[1]: http://slashdot.org\n[link text itself]: http://www.reddit.com\n[logo]: https://github.com/adam-p/markdown-here/raw/master/src/common/images/icon48.png \"Logo Title Text 2\"\n\n\nfile:*\na:footnotes\nvalues:name=\"logo\" & title!=\"test\"\n\n\nfile:*\na:footnotes\nvalues:name=\"logo\" & title!=\"test\"", "path": "C:\\Users\\Andre\\Desktop\\testwiki\\asd.md"}, {"content": "# header 1\nasdasd\nasdasd\n\n[link to asd](asd.md)\n[link gdfgdfgdfgd](gfdgdfgd.md)\n[link asdasdasdasd](errsres.md)\n\nasdasd\n\n", "path": "C:\\Users\\Andre\\Desktop\\testwiki\\b.md"}, {"content": "", "path": "C:\\Users\\Andre\\Desktop\\testwiki\\test.py"}]}
jsondata = {"type": "folder", "folders": [{"type": "folder", "folders": [], "name": "wikiconfig", "files": []}], "name": "testwiki", "files": [{"content": "[I'm an inline-style link](https://www.google.com)\n\n[I'm an inline-style link with title](https://www.google.com \"Google's Homepage\")\nInline-style: \n![alt text](https://github.com/adam-p/markdown-here/raw/master/src/common/images/icon48.png \"Logo Title Text 1\")\n\n[I'm a reference-style link][Arbitrary case-insensitive reference text]\n\n[I'm a relative reference to a repository file](../blob/master/LICENSE)\n\n[You can use numbers for reference-style link definitions][1]\n\n# headertest\nparagraph under header with name headertest\n\nReference-style: \n![alt text][logo]\n\nOr leave it empty and use the [link text itself].\n\nURLs and URLs in angle brackets will automatically get turned into links. \nhttp://www.example.com or <http://www.example.com> and sometimes \nexample.com (but not on Github, for example).\n\nSome text to show that the reference links can follow later.\n\nHere's our logo (hover to see the title text):\n\n[asdas](test.py)\n\n\n\n\n\n[arbitrary case-insensitive reference text]: https://www.mozilla.org\n[1]: http://slashdot.org\n[link text itself]: http://www.reddit.com\n[logo]: https://github.com/adam-p/markdown-here/raw/master/src/common/images/icon48.png \"Logo Title Text 2\"", "path": "C:\\Users\\Andre\\Desktop\\testwiki\\asd.md"}, {"content": "# header 1\nasdasd\nasdasd\n\n[link to asd](asd.md)\n[link gdfgdfgdfgd](gfdgdfgd.md)\n[link asdasdasdasd](errsres.md)\n\nasdasd\n\n", "path": "C:\\Users\\Andre\\Desktop\\testwiki\\b.md"}, {"content": "", "path": "C:\\Users\\Andre\\Desktop\\testwiki\\test.py"}]}



jsonsearch = {"files":{"negate":False,"values":["asd.md"]},"element":{"negate":False, "value":"headers"},"values":[{"attribute":"content","negate":False,"value":"headertest"}]}
jsonsearch2 = {"files":{"negate":False,"values":["asd.md"]},"element":{"negate":True, "value":"headers"},"values":[{"attribute":"content","negate":False,"value":"headertest"}]}



#w.initProject(jsondata)
#ret = runSearchQuery(jsonsearch,w)
#
#print(ret)
class Socket:
	def emit(self,event,jsondata,room=None):
		print("************************************")
		print("event",event)
		print("data",jsondata)
		print("sid",room)

socketFakeServer.on_connect(123,Socket())
socketFakeServer.on_initdb(123,jsondata)
socketFakeServer.on_search(123,jsonsearch)

socketFakeServer.on_connect(555,Socket())
socketFakeServer.on_initdb(555,jsondata)
socketFakeServer.on_search(555,jsonsearch2)