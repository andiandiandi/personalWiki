import socketFakeServer
import json

				

#w = DbWrapper()
#w.create_connection()
#w.prepare_tables()

#jsondata = {"type": "folder", "folders": [{"type": "folder", "folders": [], "name": "wikiconfig", "files": []}], "name": "testwiki", "files": [{"content": "[I'm an inline-style link](https://www.google.com)\n\n[I'm an inline-style link with title](https://www.google.com \"Google's Homepage\")\nInline-style: \n![alt text](https://github.com/adam-p/markdown-here/raw/master/src/common/images/icon48.png \"Logo Title Text 1\")\n\n[I'm a reference-style link][Arbitrary case-insensitive reference text]\n\n[I'm a relative reference to a repository file](../blob/master/LICENSE)\n\n[You can use numbers for reference-style link definitions][1]\n\n# headertest\nparagraph under header with name headertest\n\nReference-style: \n![alt text][logo]\n\nOr leave it empty and use the [link text itself].\n\nURLs and URLs in angle brackets will automatically get turned into links. \nhttp://www.example.com or <http://www.example.com> and sometimes \nexample.com (but not on Github, for example).\n\nSome text to show that the reference links can follow later.\n\nHere's our logo (hover to see the title text):\n\n[asdas](test.py)\n\n\n\n\n\n[arbitrary case-insensitive reference text]: https://www.mozilla.org\n[1]: http://slashdot.org\n[link text itself]: http://www.reddit.com\n[logo]: https://github.com/adam-p/markdown-here/raw/master/src/common/images/icon48.png \"Logo Title Text 2\"\n\n\nfile:*\na:footnotes\nvalues:name=\"logo\" & title!=\"test\"\n\n\nfile:*\na:footnotes\nvalues:name=\"logo\" & title!=\"test\"", "path": "C:\\Users\\Andre\\Desktop\\testwiki\\asd.md"}, {"content": "# header 1\nasdasd\nasdasd\n\n[link to asd](asd.md)\n[link gdfgdfgdfgd](gfdgdfgd.md)\n[link asdasdasdasd](errsres.md)\n\nasdasd\n\n", "path": "C:\\Users\\Andre\\Desktop\\testwiki\\b.md"}, {"content": "", "path": "C:\\Users\\Andre\\Desktop\\testwiki\\test.py"}]}
jsondata = {'type': 'folder', 'folders': [{'type': 'folder', 'folders': [{'type': 'folder', 'folders': [{'type': 'folder', 'folders': [{'type': 'folder', 'folders': [], 'name': 's', 'files': [{'lastmodified': 1595172750.26847, 'content': "# This is an <h1> tag\n## This is an <h2> tag\n###### This is an <h6> tag\n\n*This text will be italic*\n_This will also be italic_\n\n**This text will be bold**\n__This will also be bold__\n\n_You **can** combine them_\n\n\n![GitHub Logo](/images/logo.png)\nFormat: ![Alt Text](url)\n\n\nhttp://github.com - automatic!\n[GitHub](http://github.com)\n\nAs Kanye West said:\n\n> We're living the future so\n> the present is our past.\n\nI think you should use an\n`<addr>` element here instead.\n\n\n```javascript\nfunction fancyAlert(arg) {\n  if(arg) {\n    $.facebox({div:'#foo'})\n  }\n}\n```", 'path': 'C:\\Users\\Andre\\Desktop\\nowiki\\testfolder\\subtestfolder\\s\\s\\ddd.md'}, {'lastmodified': 1595242189.484356, 'content': 'asdasd\n## header2\nasdasd\n\n#### header xxxx\naaaaaaaasdasdaasd\naaasd\naddssdasd\na\n# header 222\n\n# header 222\n\t', 'path': 'C:\\Users\\Andre\\Desktop\\nowiki\\testfolder\\subtestfolder\\s\\s\\ff.md'}]}], 'name': 's', 'files': [{'lastmodified': 1595244182.9139004, 'content': 'sasd\nsd\ndffd\nasd\n\n\nsss\n#header 1\n', 'path': 'C:\\Users\\Andre\\Desktop\\nowiki\\testfolder\\subtestfolder\\s\\asdasd.md'}, {'lastmodified': 1595242288.606153, 'content': '# header33\n\ns', 'path': 'C:\\Users\\Andre\\Desktop\\nowiki\\testfolder\\subtestfolder\\s\\newfile.md'}]}], 'name': 'subtestfolder', 'files': []}], 'name': 'testfolder', 'files': [{'lastmodified': 1595241642.709231, 'content': "# This is an <h1> tag\n## This is an <h2> tag\n###### This is an <h6> tag\ns\n*This text will be italic*\n_This will also be italic_\n\n**This text will be bold**\n__This will also be bold__\n\n_You **can** combine them_\n\ns\n![GitHub Logo](/images/logo.png)\nFormat: ![Alt Text](url)\n\n\nhttp://github.com - automatic!\n[GitHub](http://github.com)\n\nAs Kanye West said:\n\n> We're living the future so\n> the present is our past.\n\nI think you should use an\n`<addr>` element here instead.\n\n\n```javascript\nfunction fancyAlert(arg) {\n  if(arg) {\n    $.facebox({div:'#foo'})\n  }\n}\n```", 'path': 'C:\\Users\\Andre\\Desktop\\nowiki\\testfolder\\ddd.md'}, {'lastmodified': 1595241904.8068953, 'content': 'asdasd\n## header2\nasdasd\nasd\nasdasdasd\nasdasd\nasd\n\n## header33\t', 'path': 'C:\\Users\\Andre\\Desktop\\nowiki\\testfolder\\ff.md'}]}], 'name': 'nowiki', 'files': []}





jsonsearch = {"files":{"negate":False,"values":["newfile.md"]},"element":{"negate":False, "value":"headers"},"values":[{"attribute":"content","negate":False,"value":"header333"}]}
jsonsearch2 = {"files":{"negate":False,"values":["ddd.md"]},"element":{"negate":False, "value":"headers"},"values":[]}


changedata = {"queue": [{"type": "created", "lastmodified":2 ,"srcPath": "C:\\Users\\Andre\\Desktop\\nowiki\\testfolder\\subtestfolder\\s\\s\\fff.md", "content": "asdasd\n## header2\nasdasd\n\n#### header xxxx\naaaaaaaasdasdaasdasd\naaasd\naddssdasd\na\n# header 222\n\n# header 222\n\t"},
 {"type": "modified", "lastmodified":1, "srcPath": "C:\\Users\\Andre\\Desktop\\nowiki\\testfolder\\subtestfolder\\s\\s\\ddd.md", "content": "asdasd\n## header2\nasdasd\n\n#### header xxxx\naaaaaaaasdasdaasdasd\naaasd\naddssdasd\na\n# header 222\n\n# header 222\n\t"}]}

root_folder = "C:\\Users\\Andre\\Desktop\\nowiki"
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

d = {
    "root_folder": root_folder,
    "project_structure": jsondata
}

socketFakeServer.on_connect(123,Socket())
socketFakeServer.on_initializeProject(123,json.dumps(d))
socketFakeServer.on_filesChanged(123,json.dumps(changedata))
#socketFakeServer.on_searchQuery(123,json.dumps(jsonsearch2))




#C:\Users\Andre\Desktop\nowiki
#C:\Users\Andre\Desktop\nowiki\wikiconfig
#C:\Users\Andre\Desktop\nowiki\wikiconfig\wiki.db