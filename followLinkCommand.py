import sublime
import sublime_plugin
import os
import subprocess


class FollowLinkCommand(sublime_plugin.TextCommand):
	def run(self, edit):

		view = self.view
		self.edit = edit

		link_regions = view.find_by_selector(
	            'markup.underline.link.markdown')

		self.full_path_of_link = None

		for region in link_regions:
				if region.a <= view.sel()[0].a <= region.b:
					self.full_path_of_link = view.substr(region)

		if self.full_path_of_link:
			#---insert broken link test here---
			self.open_link_in_new_tab()


	def open_link_in_new_tab(self):
		#subprocess.Popen(["sublime_text", self.full_path_of_link])
		self.view.window().open_file(self.full_path_of_link)