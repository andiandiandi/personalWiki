import sublime_plugin,sublime

class EraseRegionCommand(sublime_plugin.TextCommand):
	def run(self, edit, regionA, regionB):
		if (regionA and regionB) and (type(regionA) is int and type(regionB) is int):
			region = sublime.Region(regionA, regionB)
			self.view.replace(edit, region, "")
		else:
			sublime.error_message("regionA or regionB is not an int" )

class LinkReplaceListener(sublime_plugin.ViewEventListener):

	def on_text_command(self,command_name, args):

		if command_name == "paste":
			view = self.view
			
			link_regions = view.find_by_selector(
					'markup.underline.link.markdown')

			image_regions = view.find_by_selector(
					'markup.underline.link.image.markdown')

			modified_region = None
			clipboard_string = None
			#max url length
			CLIPBOARD_LIMIT = 2048

			for region in link_regions+image_regions:
					if region.a <= view.sel()[0].a <= region.b:
						clipboard_string = sublime.get_clipboard(CLIPBOARD_LIMIT)
						modified_region = region

			if modified_region and clipboard_string:
				view.run_command("erase_region",{"regionA":modified_region.a,"regionB":modified_region.b})



	