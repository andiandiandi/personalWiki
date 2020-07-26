import os
def createContainer():
	return '<div class="foldercontainer">'

def createFile(file):
	return '<span class="file fa-file-text">' + os.path.basename(file) + '</span>'

def createNonemptyFolder(name):
	return '<span class="folder fa-folder-o" data-isexpanded="true">' + name + '</span>'

def createEmptyFolder(name):
	return '<span class="folder fa-folder">' + name + '</span>'

def createNoItems():
	return '<span class="noitems">No Items</span>'

def funct(jsondata):
	toret = ""
	for data in jsondata:
		toret += createContainer()
		files = data["files"]
		if files:
			toret += createNonemptyFolder(data["name"])
			for file in files:
				toret += createFile(file["path"])
		else:
			toret += createEmptyFolder(data["name"])
			toret += createNoItems()
		toret += funct(data["folders"])
		toret += '</div>'


	return toret







html1 =  """
<!doctype html>
<!DOCTYPE html>
<html>
	<head>
		<title>{{wikipageName}}</title>
		<style>
			#hierarchy
{
    font-family: FontAwesome;
    width: 300px;
}
.foldercontainer, .file, .noitems
{
    display: block;
    padding: 5px 5px 5px 50px;
}
.folder
{
    color: red;
}
.file
{
    color: green;
}
.folder, .file
{
    cursor: pointer;
}
.noitems
{
    display: none;
    pointer-events: none;
}
.folder:hover,.file:hover
{
    background: yellow;
}
.folder:before, .file:before
{
    padding-right: 10px;
}
.column {
  float: left;
}

.left, .right {
  width: 25%;
}

.middle {
  width: 50%;
}

/* Clear floats after the columns */
.row:after {
  content: "";
  display: table;
  clear: both;
}
		</style>
		<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css" rel="stylesheet"/>
	</head>
	<body>
		<div class="row">
			<div class="column left">
				
				<div id="hierarchy">
"""

jsondata = {'type': 'folder', 'files': [], 'folders': [{'type': 'folder', 'files': [{'lastmodified': 1595446285.5500617, 'content': "# tis ye\n\n#sdfsdfsdfsijf\nsdfsdf\n\nsdfsdf\n\nasdasd\n\n# This is an <h1> tag\n## This is an <h2> tag\n###### This is an <h6> tag\ns\n*This text will be italic*\n_This will also be italic_\n\n**This text will be bold**\n__This will also be bold__\n\n_You **can** combine them_\n\ns\n![GitHub Logo](/images/logo.png)\nFormat: ![Alt Text](url)\n\n\nhttp://github.com - automatic!\n[GitHub](http://github.com)\n\nAs Kanye West said:\n\n> We're living the future so\n> the present is our past.\n\nI think you should use an\n`<addr>` element here instead.\n\n\n```javascript\nfunction fancyAlert(arg) {\n  if(arg) {\n    $.facebox({div:'#foo'})\n  }\n}\n```", 'path': 'C:\\Users\\Andre\\Desktop\\nowiki\\testfolder\\ddd.md'}, {'lastmodified': 1595443830.0248666, 'content': 'asdasd\n## header2\nasdasd\nasd\nasdasdasd\nasdasd\nasd\n\n## header33', 'path': 'C:\\Users\\Andre\\Desktop\\nowiki\\testfolder\\ff.md'}], 'folders': [{'type': 'folder', 'files': [], 'folders': [{'type': 'folder', 'files': [{'lastmodified': 1595442600.3932858, 'content': '\nasd\n\n', 'path': 'C:\\Users\\Andre\\Desktop\\nowiki\\testfolder\\subtestfolder\\s\\newfile.md'}], 'folders': [{'type': 'folder', 'files': [], 'folders': [], 'name': 's'}], 'name': 's'}], 'name': 'subtestfolder'}], 'name': 'testfolder'}], 'name': 'nowiki'}

html2 = funct(jsondata["folders"])
html3 = """					
				</div>
				
			</div>
			<div class="column middle">
				Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod
				tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
				quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
				consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
				cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non
				proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
			</div>
			
			<div class="column right">
				Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod
				tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
				quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
				consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
				cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non
				proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
			</div>
		</div>
		<script type="text/javascript">
		var hierarchy = document.getElementById("hierarchy");
		hierarchy.addEventListener("click", function(event){
		var elem = event.target;
		if(elem.tagName.toLowerCase() == "span" && elem !== event.currentTarget)
		{
		var type = elem.classList.contains("folder") ? "folder" : "file";
		if(type=="file")
		{
		alert("File accessed");
		}
		if(type=="folder")
		{
		var isexpanded = elem.dataset.isexpanded=="true";
		if(isexpanded)
		{
		elem.classList.remove("fa-folder-o");
		elem.classList.add("fa-folder");
		}
		else
		{
		elem.classList.remove("fa-folder");
		elem.classList.add("fa-folder-o");
		}
		elem.dataset.isexpanded = !isexpanded;
		var toggleelems = [].slice.call(elem.parentElement.children);
		var classnames = "file,foldercontainer,noitems".split(",");
		toggleelems.forEach(function(element){
		if(classnames.some(function(val){return element.classList.contains(val);}))
		element.style.display = isexpanded ? "none":"block";
		});
		}
		}
		});
		</script>
	</body>
</html>
"""
print(html1+html2+html3)