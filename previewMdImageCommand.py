import sublime
import sublime_plugin
import os
import re
import base64
import urllib.request

phantom_dict = {}


url_regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

class PreviewMdImageCommand(sublime_plugin.TextCommand):

	def run(self, edit):

		view = self.view

		if not view.id() in phantom_dict:
			phantom_dict[view.id()] = set()
		
		img_regions = view.find_by_selector(
	            'markup.underline.link.image.markdown')

		if PreviewMdImageCommand.points_at_imagelink(view):

			image_linkname = None

			for region in img_regions:
				if region.a <= view.sel()[0].a <= region.b:
					image_linkname = view.substr(region)

			if view.id() in phantom_dict:
				if image_linkname in phantom_dict[view.id()]:
					self.hide_image(view,image_linkname)
				else:
					self.preview_single_local_image(view,image_linkname,view.sel()[0])
		else:

			full_image_path_at_region = {}

			for region in img_regions:
				image_linkname = view.substr(region)
				if view.id() in phantom_dict:
					if image_linkname not in phantom_dict[view.id()]:
						full_image_path_at_region[image_linkname] = region

			if full_image_path_at_region:
				self.preview_multiple_images(view,full_image_path_at_region)
			else:
				self.hide_image(view,None,True)

	@staticmethod 
	def points_at_imagelink(view):
		scope_at_caret = view.scope_name(view.sel()[0].b)
		return "markup.underline.link.image.markdown" in scope_at_caret

	def hide_image(self,view,image_linkname,full_clear = False):
		if full_clear:
			while phantom_dict[view.id()]:
				image_linkname = phantom_dict[view.id()].pop()
				view.erase_phantoms(image_linkname)
		else:
			view.erase_phantoms(image_linkname)
			if view.id() in phantom_dict:
				phantom_dict[view.id()].remove(image_linkname)
			
		
	def preview_single_local_image(self,view,image_linkname,region):

		if re.match(url_regex,image_linkname) is None:
			cwd = PreviewMdImageCommand.get_path_of(view)
			if not cwd:
				view.window().status_message("projectfolder not found")
				return
			content_type = "file://"
			content_image = os.path.join(cwd, image_linkname)
		else:
			content_type = "data:image/{0};base64,".format(image_linkname.split('.')[-1])
			content_image = PreviewMdImageCommand.convert_to_base64(image_linkname)

		phantom_content = """
								<a href="close"><img src="{0}{1}" class="inlineImage" width="128" height="128"></a>
						  """.format(content_type,content_image)

		nav = lambda href: self.hide_image(view,image_linkname)

		view.add_phantom(image_linkname,region ,phantom_content,sublime.LAYOUT_BELOW, on_navigate = nav)
		phantom_dict[view.id()].add(image_linkname)


	def preview_multiple_images(self,view,image_name_at_region):
		
		#{background.png : (10,15)}
		for image_linkname in image_name_at_region.keys():
			self.preview_single_local_image(view,image_linkname,image_name_at_region[image_linkname])

	@staticmethod
	def convert_to_base64(url):

		req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
		url_content = urllib.request.urlopen(req).read()

		base64_encoded_string = base64.b64encode(url_content)
		ascii_decoded_string = base64_encoded_string.decode('ascii')

		return ascii_decoded_string

	@staticmethod
	def get_path_of(view):

	    folder = None
	    if view.window().project_file_name():
	        folder = os.path.dirname(view.window().project_file_name())
	    elif view.file_name():
	        folder = os.path.dirname(view.file_name())
	    elif view.window().folders():
	        folder = os.path.abspath(view.window().folders()[0])

	    return folder


class ViewCalculator(sublime_plugin.ViewEventListener):
    def __init__(self, view):
        self.view = view
       
    def on_close(self):
    	if self.view.id() in phantom_dict:
    		phantom_dict[self.view.id()].clear()

    
