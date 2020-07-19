import socketio
import time
import json

sio = socketio.Client()

def connect():
    print('connected')

def disconnect():
    print("I'm disconnected!")

def projectInitializeResponse(jsondata):
	 print("sio got projectInitializeResponse:" + str(jsondata))

def searchQueryResponse(jsondata):
	print("sio got searchQueryResponse:" + str(jsondata))

sio.on("connect",connect)
sio.on("disconnect",disconnect)

sio.on("project_initialized", projectInitializeResponse)
sio.on("search_query", searchQueryResponse)

sio.connect('http://localhost:9000')
print(sio.sid)


jsondata = {'name': 'nowiki', 'files': [], 'type': 'folder', 'folders': [{'name': 'testfolder', 'files': [{'path': 'C:\\Users\\Andre\\Desktop\\nowiki\\testfolder\\ddd.md', 'content': "# This is an <h1> tag\n## This is an <h2> tag\n###### This is an <h6> tag\n\n*This text will be italic*\n_This will also be italic_\n\n**This text will be bold**\n__This will also be bold__\n\n_You **can** combine them_\n\n\n![GitHub Logo](/images/logo.png)\nFormat: ![Alt Text](url)\n\n\nhttp://github.com - automatic!\n[GitHub](http://github.com)\n\nAs Kanye West said:\n\n> We're living the future so\n> the present is our past.\n\nI think you should use an\n`<addr>` element here instead.\n\n\n```javascript\nfunction fancyAlert(arg) {\n  if(arg) {\n    $.facebox({div:'#foo'})\n  }\n}\n```", 'lastmodified': 1595172750.26847}, {'path': 'C:\\Users\\Andre\\Desktop\\nowiki\\testfolder\\fasfas.md', 'content': 'asd', 'lastmodified': 1594995741.5512588}, {'path': 'C:\\Users\\Andre\\Desktop\\nowiki\\testfolder\\ff.md', 'content': 'asdasd\n## header2\nasdasd\n\n#### header xxxx\naaaaaaa\naa\na\na\n# header 222\n\n# header 222\n\t', 'lastmodified': 1595174907.488773}], 'type': 'folder', 'folders': [{'name': 'subtestfolder', 'files': [], 'type': 'folder', 'folders': [{'name': 's', 'files': [], 'type': 'folder', 'folders': [{'name': 's', 'files': [{'path': 'C:\\Users\\Andre\\Desktop\\nowiki\\testfolder\\subtestfolder\\s\\s\\ddd.md', 'content': "# This is an <h1> tag\n## This is an <h2> tag\n###### This is an <h6> tag\n\n*This text will be italic*\n_This will also be italic_\n\n**This text will be bold**\n__This will also be bold__\n\n_You **can** combine them_\n\n\n![GitHub Logo](/images/logo.png)\nFormat: ![Alt Text](url)\n\n\nhttp://github.com - automatic!\n[GitHub](http://github.com)\n\nAs Kanye West said:\n\n> We're living the future so\n> the present is our past.\n\nI think you should use an\n`<addr>` element here instead.\n\n\n```javascript\nfunction fancyAlert(arg) {\n  if(arg) {\n    $.facebox({div:'#foo'})\n  }\n}\n```", 'lastmodified': 1595172750.26847}, {'path': 'C:\\Users\\Andre\\Desktop\\nowiki\\testfolder\\subtestfolder\\s\\s\\fasfas.md', 'content': 'asd', 'lastmodified': 1594995741.5512588}, {'path': 'C:\\Users\\Andre\\Desktop\\nowiki\\testfolder\\subtestfolder\\s\\s\\ff.md', 'content': 'asdasd\n## header2\nasdasd\n\n#### header xxxx\naaaaaaa\naa\na\na\n# header 222\n\n# header 222\n\t', 'lastmodified': 1595174907.488773}], 'type': 'folder', 'folders': []}]}]}]}]}



jsonsearch = {"files":{"negate":False,"values":["newfile.md"]},"element":{"negate":False, "value":"headers"},"values":[{"attribute":"content","negate":False,"value":"header 222"}]}
jsonsearch2 = {"files":{"negate":False,"values":["subtestfile.md"]},"element":{"negate":False, "value":"headers"},"values":[]}



d = {
	"root_folder":"C:\\Users\\Andre\\Desktop\\nowiki",
	"project_structure": jsondata,
}

sio.emit("initialize_project",json.dumps(d))
sio.emit("search_query",json.dumps(jsonsearch))

time.sleep(3)
sio.disconnect()

