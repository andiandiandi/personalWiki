from html.parser import HTMLParser


htmlstr = """

<!doctype html>
<!DOCTYPE html>
<html>
	<head>
		<title></title>
		<link rel="stylesheet" href="/static/wikipageLayout.css">
		<link rel="stylesheet" href="/static/folderPageLayout.css">
		<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css" rel="stylesheet"/>
	</head>
	<body>
			<div style="position: absolute; left: 50%;">
			    <div style="position: relative; left: -50%;">
			     	<p><img src="/images/logo.jpg" alt="GitHub Logo" />
<img src="https://produkt-tests.com/wp-content/uploads/2018/07/IKRA-Akku-Rasenm%C3%A4her-IAM-40-4625-S-im-Test-3.jpg" alt="test" /></p>

			    </div>
			  </div>
		<script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/2.3.0/socket.io.js"></script>
		<script type="text/javascript">
			var sid = "095f7a3df3974de88c176c35dae186c8"
			var path = "C:\\Users\\Andre\\Desktop\\nowiki\\testfolder\\ddd.md"
			var dirpath = "C:\\Users\\Andre\\Desktop\\nowiki\\testfolder"

			var absUri = new RegExp('^(?:[a-z]+:)?//', 'i');


			function escapeRegExp(string) {
 				 return string.replace(/[.*+\-?^${}()|[\]\\]/g, '\\$&'); // $& means the whole matched string
			}

			function replaceAll(str, find, replace) {
 				 return str.replace(new RegExp(escapeRegExp(find), 'g'), replace);
			}

			function absoluteUrl(path){
				encodedStr = encodeURIComponent(path)
				alert("en " + encodedStr)
				var url = "http://localhost:9000/" + sid + "/" + encodedStr.toString()
				return url	
			}

			function normalize(path){
			    path = Array.prototype.join.apply(arguments,['/'])
			    var sPath;
			    while (sPath!==path) {
			        sPath = n(path);
			        path = n(sPath);
			    }
			    function n(s){return s.replace(/\/+/g,'/').replace(/\w+\/+\.\./g,'')}
			    return path.replace(/^\//,'').replace(/\/$/,'');
			}

			function resolveRelativeImages(){
				var images = document.getElementsByTagName('img'); 
				for(var i = 0; i < images.length; i++) {
					image = images[i]
					src = image.getAttribute("src")
					console.log("src",src)
					if (!absUri.test(src)){
						dirname = replaceAll(dirpath,"\\","//")
						resolvedpath = normalize(dirname + "//" + src)
						image.setAttribute("src",resolvedpath)
					}
				}
			}

			function attachClicklistenerToHrefs(){
				var links = document.getElementsByTagName('a');


				for(var i = 0; i< links.length; i++){
					links[i].onclick = function(){
						href = this.getAttribute("href")
						if(!absUri.test(href)){
							dirname = replaceAll(dirpath,"\\","//")
							resolvedpath = normalize(dirname + "//" + href)
							newHref = absoluteUrl(replaceAll(resolvedpath,"/","\\"))
							this.setAttribute("href",newHref)
							return true
						}
						return true
					}
				}
			}



			window.onload = function() {
				resolveRelativeImages()
			  	attachClicklistenerToHrefs();
			};
			var ioSocket = io("http://localhost:9000/events");
			ioSocket.on("connect",function(msg){
				ioSocket.emit("subscribe",JSON.stringify([{"eventname":"render_wikipage","targetsid":sid},{"eventname":"update_wikipage","targetsid":sid,"path":path}]))
			})
			ioSocket.on('render_wikipage', function(path) {
						var url = absoluteUrl(path)
						if(window.location.href !== url){
							window.location.href = url
					}
					return false
	           });
			ioSocket.on('update_wikipage', function(notUsedFlag) {
					window.location.reload()
					return false
				});
			ioSocket.on("disconnect",function(msg){
				return false
			})
		</script>
	</body>
</html>
"""

class MyHTMLParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        print("Encountered a start tag:", tag)
        print("attr",attrs)
        print("dir",dir(attrs))

    def handle_endtag(self, tag):
        print("Encountered an end tag :", tag)

    def handle_data(self, data):
        print("Encountered some data  :", data)

parser = MyHTMLParser()


parser.feed(htmlstr)