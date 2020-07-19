import socketFakeServer
				

#w = DbWrapper()
#w.create_connection()
#w.prepare_tables()

#jsondata = {"type": "folder", "folders": [{"type": "folder", "folders": [], "name": "wikiconfig", "files": []}], "name": "testwiki", "files": [{"content": "[I'm an inline-style link](https://www.google.com)\n\n[I'm an inline-style link with title](https://www.google.com \"Google's Homepage\")\nInline-style: \n![alt text](https://github.com/adam-p/markdown-here/raw/master/src/common/images/icon48.png \"Logo Title Text 1\")\n\n[I'm a reference-style link][Arbitrary case-insensitive reference text]\n\n[I'm a relative reference to a repository file](../blob/master/LICENSE)\n\n[You can use numbers for reference-style link definitions][1]\n\n# headertest\nparagraph under header with name headertest\n\nReference-style: \n![alt text][logo]\n\nOr leave it empty and use the [link text itself].\n\nURLs and URLs in angle brackets will automatically get turned into links. \nhttp://www.example.com or <http://www.example.com> and sometimes \nexample.com (but not on Github, for example).\n\nSome text to show that the reference links can follow later.\n\nHere's our logo (hover to see the title text):\n\n[asdas](test.py)\n\n\n\n\n\n[arbitrary case-insensitive reference text]: https://www.mozilla.org\n[1]: http://slashdot.org\n[link text itself]: http://www.reddit.com\n[logo]: https://github.com/adam-p/markdown-here/raw/master/src/common/images/icon48.png \"Logo Title Text 2\"\n\n\nfile:*\na:footnotes\nvalues:name=\"logo\" & title!=\"test\"\n\n\nfile:*\na:footnotes\nvalues:name=\"logo\" & title!=\"test\"", "path": "C:\\Users\\Andre\\Desktop\\testwiki\\asd.md"}, {"content": "# header 1\nasdasd\nasdasd\n\n[link to asd](asd.md)\n[link gdfgdfgdfgd](gfdgdfgd.md)\n[link asdasdasdasd](errsres.md)\n\nasdasd\n\n", "path": "C:\\Users\\Andre\\Desktop\\testwiki\\b.md"}, {"content": "", "path": "C:\\Users\\Andre\\Desktop\\testwiki\\test.py"}]}
jsondata = {'name': 'nowiki', 'files': [], 'type': 'folder', 'folders': [{'name': 'testfolder', 'files': [{'path': 'C:\\Users\\Andre\\Desktop\\nowiki\\testfolder\\ddd.md', 'content': "# This is an <h1> tag\n## This is an <h2> tag\n###### This is an <h6> tag\n\n*This text will be italic*\n_This will also be italic_\n\n**This text will be bold**\n__This will also be bold__\n\n_You **can** combine them_\n\n\n![GitHub Logo](/images/logo.png)\nFormat: ![Alt Text](url)\n\n\nhttp://github.com - automatic!\n[GitHub](http://github.com)\n\nAs Kanye West said:\n\n> We're living the future so\n> the present is our past.\n\nI think you should use an\n`<addr>` element here instead.\n\n\n```javascript\nfunction fancyAlert(arg) {\n  if(arg) {\n    $.facebox({div:'#foo'})\n  }\n}\n```", 'lastmodified': 1595172750.26847}, {'path': 'C:\\Users\\Andre\\Desktop\\nowiki\\testfolder\\fasfas.md', 'content': 'asd', 'lastmodified': 1594995741.5512588}, {'path': 'C:\\Users\\Andre\\Desktop\\nowiki\\testfolder\\ff.md', 'content': 'asdasd\n## header2\nasdasd\n\n#### header xxxx\naaaaaaa\naa\na\na\n# header 222\n\n# header 222\n\t', 'lastmodified': 1595174907.488773}], 'type': 'folder', 'folders': [{'name': 'subtestfolder', 'files': [], 'type': 'folder', 'folders': [{'name': 's', 'files': [], 'type': 'folder', 'folders': [{'name': 's', 'files': [{'path': 'C:\\Users\\Andre\\Desktop\\nowiki\\testfolder\\subtestfolder\\s\\s\\ddd.md', 'content': "# This is an <h1> tag\n## This is an <h2> tag\n###### This is an <h6> tag\n\n*This text will be italic*\n_This will also be italic_\n\n**This text will be bold**\n__This will also be bold__\n\n_You **can** combine them_\n\n\n![GitHub Logo](/images/logo.png)\nFormat: ![Alt Text](url)\n\n\nhttp://github.com - automatic!\n[GitHub](http://github.com)\n\nAs Kanye West said:\n\n> We're living the future so\n> the present is our past.\n\nI think you should use an\n`<addr>` element here instead.\n\n\n```javascript\nfunction fancyAlert(arg) {\n  if(arg) {\n    $.facebox({div:'#foo'})\n  }\n}\n```", 'lastmodified': 1595172750.26847}, {'path': 'C:\\Users\\Andre\\Desktop\\nowiki\\testfolder\\subtestfolder\\s\\s\\fasfas.md', 'content': 'asd', 'lastmodified': 1594995741.5512588}, {'path': 'C:\\Users\\Andre\\Desktop\\nowiki\\testfolder\\subtestfolder\\s\\s\\ff.md', 'content': 'asdasd\n## header2\nasdasd\n\n#### header xxxx\naaaaaaa\naa\na\na\n# header 222\n\n# header 222\n\t', 'lastmodified': 1595174907.488773}], 'type': 'folder', 'folders': []}]}]}]}]}


jsonsearch = {"files":{"negate":False,"values":["newfile.md"]},"element":{"negate":False, "value":"headers"},"values":[{"attribute":"content","negate":False,"value":"header333"}]}
jsonsearch2 = {"files":{"negate":False,"values":["subtestfile.md"]},"element":{"negate":False, "value":"headers"},"values":[]}



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
socketFakeServer.on_initializeProject(123,"C:\\Users\\Andre\\Desktop\\nowiki",jsondata)
#socketFakeServer.on_search(123,jsonsearch)



#C:\Users\Andre\Desktop\nowiki
#C:\Users\Andre\Desktop\nowiki\wikiconfig
#C:\Users\Andre\Desktop\nowiki\wikiconfig\wiki.db