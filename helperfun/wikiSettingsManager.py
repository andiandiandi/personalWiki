import sublime
import os
import io
from . import pathManager

def __settings_file():
	if not __settings_file_exists():
		generate_new_stock_settings_file()

	return sublime.load_settings('wiki.sublime-settings')

def __settings_file_exists():
	return pathManager.exists(full_path_to_settings_file())

def full_path_to_settings_file():
	return os.path.join(pathManager.path_to_plugin_folder(),"wiki.sublime-settings")

def get(settings_name):
	settings_file = __settings_file()
	if settings_file.has(settings_name):
		return settings_file.get(settings_name)
	else:
		sublime.error_message("settings file:'wiki.sublime-settings' has no setting: " + settings_name)
		return None



def generate_new_stock_settings_file():
	wiki_settings_content = """{
									"saving":{

										"auto_save": true,
										"whitelist_filetypes": [".md",".txt"]

									},
									"navigation":{
										"traverse_filetypes": [".md"]
									},
									"wordcount":{

										"enable_live_count": true,

										"enable_readtime": true,
										"readtime_wpm": 200,
										"char_ignore_whitespace": true,

										"enable_line_word_count": true,
										"enable_line_char_count": true,

										"enable_count_chars": true,
										"enable_count_lines": true,

										"enable_count_pages": true,
										"words_per_page": 300,
										"page_count_mode_count_words": true,

										"whitelist_filetypes": [".md",".txt"],

										/* please use lowercase for the syntax names in the following section: */
										"strip": {
											"php": [
												"<[^>]*>"
											],
											"html": [
												"<[^>]*>"
											]
										}
									},
								}"""
	with io.open(full_path_to_settings_file(), "w", encoding="utf-8") as file:
		file.write(wiki_settings_content)
