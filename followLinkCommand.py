import sublime
import sublime_plugin
import os
import urllib
import re
import webbrowser
import imp
from .helperfun import pathManager

def plugin_loaded():
	imp.reload(pathManager)

# URL-link validation
ip_middle_octet = u"(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5]))"
ip_last_octet = u"(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))"

URL_PATTERN = re.compile(
						u"^"
						# protocol identifier
						u"(?:(?:https?|ftp|rtsp|rtp|mmp)://)"
						# user:pass authentication
						u"(?:\S+(?::\S*)?@)?"
						u"(?:"
						u"(?P<private_ip>"
						# IP address exclusion
						# private & local networks
						u"(?:localhost)|"
						u"(?:(?:10|127)" + ip_middle_octet + u"{2}" + ip_last_octet + u")|"
						u"(?:(?:169\.254|192\.168)" + ip_middle_octet + ip_last_octet + u")|"
						u"(?:172\.(?:1[6-9]|2\d|3[0-1])" + ip_middle_octet + ip_last_octet + u"))"
						u"|"
						# IP address dotted notation octets
						# excludes loopback network 0.0.0.0
						# excludes reserved space >= 224.0.0.0
						# excludes network & broadcast addresses
						# (first & last IP address of each class)
						u"(?P<public_ip>"
						u"(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])"
						u"" + ip_middle_octet + u"{2}"
						u"" + ip_last_octet + u")"
						u"|"
						# host name
						u"(?:(?:[a-z\u00a1-\uffff0-9_-]-?)*[a-z\u00a1-\uffff0-9_-]+)"
						# domain name
						u"(?:\.(?:[a-z\u00a1-\uffff0-9_-]-?)*[a-z\u00a1-\uffff0-9_-]+)*"
						# TLD identifier
						u"(?:\.(?:[a-z\u00a1-\uffff]{2,}))"
						u")"
						# port number
						u"(?::\d{2,5})?"
						# resource path
						u"(?:/\S*)?"
						# query string
						u"(?:\?\S*)?"
						u"$",
						re.UNICODE | re.IGNORECASE
					   )

class FollowLinkCommand(sublime_plugin.TextCommand):
	def run(self, edit):

		view = self.view
		self.edit = edit

		link_regions = view.find_by_selector(
				'markup.underline.link.markdown')

		image_regions = view.find_by_selector(
				'markup.underline.link.image.markdown')

		self.full_path_of_link = None

		for region in link_regions+image_regions:
				if region.a <= view.sel()[0].a <= region.b:
					self.full_path_of_link = view.substr(region)

		if self.full_path_of_link:
			#---insert broken link test here---

			#path is uri
			if validate_url(self.full_path_of_link):
				webbrowser.open(self.full_path_of_link)
			#fallback file
			else:
				#check if exists
				root_folder = pathManager.root_folder_of_view(view)
				#f pathManager.folder_has_file(root_folder,self.full_path_of_link):
				open_link_in_new_tab(self.view,self.full_path_of_link)


def open_link_in_new_tab(view,filename):
	view.window().open_file(filename)

def validate_url(url):   
	return re.compile(URL_PATTERN).match(url) is not None
