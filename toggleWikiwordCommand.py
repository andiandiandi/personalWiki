import sublime
import sublime_plugin
import mdpopups
import os
from .wikipageTemplates import templateGenerator as templateGenerator
import imp

def plugin_loaded():
    imp.reload(templateGenerator)

frontmatter = {
    "markdown_extensions": [
        "markdown.extensions.admonition",
        "markdown.extensions.attr_list",
        "markdown.extensions.def_list",
        "markdown.extensions.nl2br",
        # Smart quotes always have corner cases that annoy me, so don't bother with them.
        {"markdown.extensions.smarty": {"smart_quotes": False}},
        "pymdownx.betterem",
        {
            "pymdownx.magiclink": {
                "repo_url_shortener": True,
                "repo": "sublime-markdown-popups",
                "user": "facelessuser"
            }
        },
        "pymdownx.extrarawhtml",
        "pymdownx.keys",
        {"pymdownx.escapeall": {"hardbreak": True, "nbsp": True}},
        # Sublime doesn't support superscript, so no ordinal numbers
        {"pymdownx.smartsymbols": {"ordinal_numbers": False}}
    ]
}

class ToggleWikiwordCommand(sublime_plugin.TextCommand):
    def run(self, edit):
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

        if selected_region is not None:
            self.prompt_for_wikiword_linkfile(edit,selected_region,selected_wikiword)
          

    def get_root_folder(self,view):
        return view.window().extract_variables()['folder']

    def prompt_for_wikiword_linkfile(self,edit,selected_region,selected_wikiword):
        root_folder = self.get_root_folder(self.view)

        subdirs = [("+new Wikipage",None)]

        for folder, subs, files in os.walk(root_folder):
            for filename in files:
                if(filename.endswith('.md')):
                    subdirs.append((filename,os.path.join(folder, filename)))


        def on_done(subdir_index):
            if subdir_index == 0:
                self.prompt_for_linkfile_folder(edit,selected_region,selected_wikiword)
            elif subdir_index > 0:
               #full path + filename
               linkfile = subdirs[subdir_index][1]
               new_selected_md_link = self.generate_md_link(edit,selected_region,selected_wikiword,linkfile)
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
                self.generate_md_link(edit,selected_region,selected_wikiword,absolute_filename)
                if subdir_index >=1:
                    self.view.window().run_command("insert_template",{"wikipage":absolute_filename,"template_filename":available_templates[subdir_index]})

        self.view.show_popup_menu(available_templates, on_done)

    def generate_md_link(self,edit,selected_region,description,linkfile):
        self.view.replace(edit,selected_region,"[{0}]({1})".format(description,linkfile))
        return self.view.sel()[0]

    def asdfasdf(self):
        def on_done(input_string):
                self.view.run_command("move_to", {"to": "bof"})
                self.view.run_command("insert", {"characters": input_string})

        def on_change(input_string):
            print("Input changed: %s" % input_string)

        def on_cancel():
            print("User cancelled the input")

        window = self.view.window()
        window.show_input_panel("Text to Insert:", "Hello, World!",
                                 on_done, on_change, on_cancel)


def on_close_phantom(href):
    """Close all phantoms."""
    view = sublime.active_window().active_view()
    mdpopups.erase_phantoms(view, 'wiki_word_creation')


def show_phantom(text,start_region,end_region):
    """Show the phantom."""
    mdpopups.clear_cache()
    close = '\n[close](#){: .btn .btn-small .btn-info}\n'
    view = sublime.active_window().active_view()
    mdpopups.add_phantom(
        view, 'wiki_word_creation', sublime.Region(start_region,end_region), text + close, 2,
        on_navigate=on_close_phantom, wrapper_class='wiki_word_creation'
    )
