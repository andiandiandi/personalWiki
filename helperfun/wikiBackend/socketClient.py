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


jsondata = {"folders": [{"folders": [{"folders": [], "files": [{"lastmodified": 1594917518.8200457, "content": "asd", "path": "C:\\Users\\Andre\\Desktop\\nowiki\\testfolder\\subtestfolder\\subtestfile1.md"}], "type": "folder", "name": "subtestfolder"}], "files": [], "type": "folder", "name": "testfolder"}], "files": [{"lastmodified": 1594920175.005276, "content": "asdasd\n\nasdasd\n\n\n\n\n\n\n\n\n# header 222\n", "path": "C:\\Users\\Andre\\Desktop\\nowiki\\newfile.md"}, {"lastmodified": 1594920140.8075106, "content": "# This is an <h1> tag\n## This is an <h2> tag\n###### This is an <h6> tag\n\n*This text will be italic*\n_This will also be italic_\n\n**This text will be bold**\n__This will also be bold__\n\n_You **can** combine them_\n\n\n![GitHub Logo](/images/logo.png)\nFormat: ![Alt Text](url)\n\nhttp://github.com - automatic!\n[GitHub](http://github.com)\n\nAs Kanye West said:\n\n> We're living the future so\n> the present is our past.\n\nI think you should use an\n`<addr>` element here instead.\n\n\n```javascript\nfunction fancyAlert(arg) {\n  if(arg) {\n    $.facebox({div:'#foo'})\n  }\n}\n```", "path": "C:\\Users\\Andre\\Desktop\\nowiki\\testfile2.md"}], "type": "folder", "name": "nowiki"}




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

