import sublime
import sublime_plugin
import mdpopups
import os
import imp
from .wikipageTemplates import templateGenerator as templateGenerator

def plugin_loaded():
    imp.reload(templateGenerator)


class InsertMdLinkCommand(sublime_plugin.TextCommand):
    def run(self, edit, title, link):

        if not title or not link:
            return
        caret_region = self.view.sel()[0]
        self.view.insert(edit, caret_region.a, "[{0}]({1})".format(title,link))

class ToggleWikiwordCommand(sublime_plugin.TextCommand):
    def run(self, edit):

        if not wikiValidator.validate() == wikiValidator.ValidationResult.success:
            return

        view = self.view

        selected_region = None

        for region in view.sel():
            if not region.empty():
                # Get the selected text
                selected_region = region
                selected_wikiword = view.substr(region)
            else:
                #automatically select current word at cursor
                current_caret_pos = view.sel()[0]
                view.run_command("expand_selection", {"to": "word"}) 
                expanded_selection = view.sel()[0]
                selected_region = sublime.Region(expanded_selection.begin(),expanded_selection.end())
                selected_wikiword = view.substr(selected_region)
                if len(selected_wikiword) == 0 or selected_wikiword.isspace():
                    view.sel().clear() 
                    view.sel().add(sublime.Region(current_caret_pos.end()))
                    return

        if selected_region:
            self.prompt_for_wikiword_linkfile(edit,selected_region,selected_wikiword)
          

    def get_root_folder(self,view):
        return view.window().extract_variables()['folder']

    def prompt_for_wikiword_linkfile(self,edit,selected_region,selected_wikiword):
        root_folder = self.get_root_folder(self.view)

        subdirs = [("+new Wikipage",None)]

        for folder, subs, files in os.walk(root_folder):
            for filename in files:
                if(filename.endswith('.md')):
                    filename_folder_mapping = filename,folder
                    subdirs.append(filename_folder_mapping)


        def on_done(subdir_index):
            if subdir_index == 0:
                self.prompt_for_linkfile_folder(edit,selected_region,selected_wikiword)
            elif subdir_index > 0:
               #folder
               filename = subdirs[subdir_index][0]
               foldername = subdirs[subdir_index][1]
               fullpath = os.path.join(foldername,filename)
               new_selected_md_link = self.replace_md_link(edit,selected_region,selected_wikiword,fullpath)
               self.view.sel().clear() 
               self.view.sel().add(sublime.Region(new_selected_md_link.end()))

        self.view.show_popup_menu([i[0] for i in subdirs], on_done)

    def prompt_for_linkfile_folder(self,edit,selected_region,selected_wikiword):
        root_folder = self.get_root_folder(self.view)

        all_project_folder_paths = ["+new Folder"]

        def on_done(subdir_index):
            if subdir_index == 0:
                print("not supported yet")
            elif subdir_index > 0:
               #full folderpath
               folder_path = all_project_folder_paths[subdir_index]
               if os.path.exists(folder_path):
                    absolute_filename = os.path.join(folder_path,"{0}.md".format(selected_wikiword))
                    self.prompt_for_template(edit,selected_region,selected_wikiword,absolute_filename)

        for folder, subs, files in os.walk(root_folder):
            found_match = False
            for filename in files:
                filename_without_ext = os.path.splitext(os.path.basename(filename))[0]
                fileextension = os.path.splitext(os.path.basename(filename))[1]
                if fileextension == ".md" and filename_without_ext == selected_wikiword:
                    found_match = True
            if not found_match:
                all_project_folder_paths.append(folder)

        self.view.show_popup_menu(all_project_folder_paths, on_done)

    def prompt_for_template(self,edit,selected_region,selected_wikiword,absolute_filename):
        available_templates = ["-no Template"]
        available_templates += templateGenerator.list_available_templates()

        def on_done(subdir_index):
            if subdir_index == -1:
                return
            elif subdir_index >= 0:
                #create empty file
                open(absolute_filename,"a").close()
                self.replace_md_link(edit,selected_region,selected_wikiword,absolute_filename)
                if subdir_index >=1:
                    self.view.window().run_command("insert_template",{"wikipage":absolute_filename,"template_filename":available_templates[subdir_index]})

        self.view.show_popup_menu(available_templates, on_done)

    def replace_md_link(self,edit,selected_region,description,abs_linked_filepath):
        filelink = os.path.relpath(abs_linked_filepath,os.path.dirname(self.view.file_name()))
        print(abs_linked_filepath)
        self.view.replace(edit,selected_region,"[{0}]({1})".format(description,filelink))
        return self.view.sel()[0]
