import sublime
import sublime_plugin
import json
import os

import shlex
import imp

from .helperfun import sessionManager
from .helperfun import pathManager
from .helperfun import localApi

imp.reload(sessionManager)
imp.reload(pathManager)
imp.reload(localApi)

class SavedSearchQueryCommand(sublime_plugin.TextCommand):
	def run(self, edit, d = None):
		if not d:
			root_folder = pathManager.root_folder()
			if sessionManager.hasProject(root_folder):
				con = sessionManager.connection(root_folder)
				con.savedSearchQuery()
		else:
			try:
				data = json.loads(d)
				c = """
					<html>
						<body>
							<style>
								a.fillthediv{display:block;text-decoration: none;}
							</style>
							
					"""
				for entry in data:
					c += """
										<div>
											<a href="{0}" class="fillthediv">
												<p>{0}</p>
												<p><a href="{0} -d">delete</a></p>
											</a>
										</div>
										
								""".format(entry["rawString"])

				def on_navigate(href):
					sublime.active_window().run_command("search_query",args={"searchQuery":href})

				self.view.show_popup(c,max_width=1000,max_height=1080,location=self.view.sel()[0].a,on_navigate=on_navigate,on_hide=None)
			except Exception as E:
				localApi.error(str(E))

class SearchQueryCommand(sublime_plugin.TextCommand):
	def run(self, edit, searchQuery = None):
		root_folder = pathManager.root_folder()
		if sessionManager.hasProject(root_folder):
			con = sessionManager.connection(root_folder)

			if searchQuery:
				con.searchQuery(searchQuery)
				return

			def on_done(searchQuery):
				con.searchQuery(searchQuery)


			localApi.window().show_input_panel("Wiki-Search", "", on_done, None,None)

def load_and_select(window, filename, begin, end):
	window = window or sublime.active_window()
	view = window.open_file(filename)
	if view.is_loading():
		view.settings().set("_do_select", [begin-1, end])
	else:
		view.run_command("select_in_view", {"begin": begin-1,"end": end})


class SelectInViewCommand(sublime_plugin.TextCommand):
	def run(self,edit,begin,end):
		view = self.view
		start_pos = view.text_point(begin, 0)
		end_pos = view.text_point(end, 0)
		view.sel().clear()
		view.sel().add(sublime.Region(start_pos, end_pos))


class ShowSearchResultCommand(sublime_plugin.TextCommand):
	def run(self,edit,queryResult):
		try:
			print(queryResult)
			queryResultParsed = json.loads(queryResult)
			searchType = queryResultParsed["type"]
			data = queryResultParsed["data"]
			if data:
				c = """
					<html>
						<body>
							<style>
								a.fillthediv{display:block;text-decoration: none;}
							</style>
							
					"""
				if searchType == "tagsearch":
					for entry in data:
						print("entry",entry)
						if entry["lines"]:
							for line in entry["lines"]:
								subHtml = """
										<div>
											<a href="{2}::{3}" class="fillthediv">
												<p>file:{0} | line:{1}</p>
												<p style="word-break:break-all"> "{4}"</p>
											</a>
										</div>
										
								""".format(os.path.basename(entry["filepath"]),line,entry["filepath"],entry["lines"],entry["content"])

								c += subHtml
						else:
							subHtml = """
										<div>
											<a href="{1}::{2}" class="fillthediv">
												<p>file: {0}</p>
											</a>
										</div>
										
								""".format(os.path.basename(entry["filepath"]),entry["filepath"],[0])
								
							c += subHtml



				elif searchType == "fulltextsearch":
					try:
						searchTerms = queryResultParsed["searchterms"]
					except:
						pass
					for entry in data:
						if searchTerms:
							l = entry["fullphrase"].split(" ")
							for term in searchTerms:
								for indx, s in enumerate(l):
									if s == term:
										s = "<b style='color:red'>{0}</b>".format(s)
										l[indx] = s
						entry["fullphrase"] = ' '.join(word for word in l)

						subHtml = """
								<div>
									<a href="{2}::{3}" class="fillthediv">
										<p>rating: {0} | file: {5} | lines: {4}</p>
										<p style="word-break:break-all">{1}</p>
									</a>
								</div>
								
						""".format(str(round((float(entry["rating"]) * 100),2)) + "%",entry["fullphrase"],
									entry["filepath"],entry["lines"],entry["lines"][0] if len(entry["lines"]) == 1 else str(entry["lines"][0]) + "-" + str(entry["lines"][-1]),
									os.path.basename(entry["filepath"]))

						
						c += subHtml
				elif searchType == "deleted":
					pass
				else:
					localApi.error("unsupported query result: " + queryResult)
					return

				c += """
					</body>
				</html>
				"""

				def on_hide():
					pass

				def on_navigate(href):
					#if href == "closePopup":
					#	self.view.hide_popup()
					print(href)
					viewname,linesStr = href.split("::")
					lines = json.loads(linesStr)
					self.view.hide_popup()
					load_and_select(None,viewname,lines[0],lines[-1])

				self.view.show_popup(c,max_width=650,max_height=1080,location=self.view.sel()[0].a,on_navigate=on_navigate,on_hide=on_hide)
		except Exception as E:
			localApi.error(str(E))



class SampleSampleListener(sublime_plugin.ViewEventListener):
	@classmethod
	def is_applicable(cls, settings):
		return settings.has("_do_select")

	def on_load(self):
		selRange = self.view.settings().get("_do_select")
		self.view.run_command("select_in_view", {"begin": selRange[0],"end": selRange[-1]})

		self.view.settings().erase("_do_select")

class SearchQueryDebugCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		self.view.window().show_input_panel("enter name", "testfile", self.on_done, self.on_change, self.on_cancel)

	def on_done(self,a):
		root_folder = pathManager.root_folder()
		if sessionManager.hasProject(root_folder):
			con = sessionManager.connection(root_folder)

			jsonsearch = {"files":{"negate":False,"values":[a + ".md"]},"element":{"negate":False, "value":"headers"},"values":[]}
			jsonsearch2 = {"files":{"negate":False,"values":["subtestfile.md"]},"element":{"negate":False, "value":"headers"},"values":[]}

			con.searchQuery(jsonsearch)
		else:
			localApi.error("connect to wiki server first")

	def on_change(self,a):
		pass
		
	def on_cancel(self):
		pass

class SearchQueryTestCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		queryResult = json.dumps({"type": "fulltextsearch", "data": [{'rating': 1.0, 'fullphrase': 'Wer marschen eigentum hinunter jahrlich launigen wir freundes Schritt den pfeifen bei schlief brummte Wunderbar so verwegene em ri aufstehen neugierig turnhalle Gegen haute hin guter ferne gib zarte war Heut ein auf las fiel igen Schlupfte aufstehen tat weiterhin schnupfen den Ja er knopf darum blank ri du notig lange etwas', 'lines': [3], 'filepath': 'C:\\Users\\Andre\\Desktop\\onefilewiki\\tt.md'},{'rating': 1.0, 'fullphrase': 'Wer marschen eigentum hinunter jahrlich launigen wir freundes Schritt den pfeifen bei schlief brummte Wunderbar so verwegene em ri aufstehen neugierig turnhalle Gegen haute hin guter ferne gib zarte war Heut ein auf las fiel igen Schlupfte aufstehen tat weiterhin schnupfen den Ja er knopf darum blank ri du notig lange etwas', 'lines': [3], 'filepath': 'C:\\Users\\Andre\\Desktop\\onefilewiki\\tt.md'},{'rating': 1.0, 'fullphrase': 'Wer marschen eigentum hinunter jahrlich launigen wir freundes Schritt den pfeifen bei schlief brummte Wunderbar so verwegene em ri aufstehen neugierig turnhalle Gegen haute hin guter ferne gib zarte war Heut ein auf las fiel igen Schlupfte aufstehen tat weiterhin schnupfen den Ja er knopf darum blank ri du notig lange etwas', 'lines': [3], 'filepath': 'C:\\Users\\Andre\\Desktop\\onefilewiki\\tt.md'},{'rating': 1.0, 'fullphrase': 'Wer marschen eigentum hinunter jahrlich launigen wir freundes Schritt den pfeifen bei schlief brummte Wunderbar so verwegene em ri aufstehen neugierig turnhalle Gegen haute hin guter ferne gib zarte war Heut ein auf las fiel igen Schlupfte aufstehen tat weiterhin schnupfen den Ja er knopf darum blank ri du notig lange etwas', 'lines': [3], 'filepath': 'C:\\Users\\Andre\\Desktop\\onefilewiki\\tt.md'},{'rating': 1.0, 'fullphrase': 'Wer marschen eigentum hinunter jahrlich launigen wir freundes Schritt den pfeifen bei schlief brummte Wunderbar so verwegene em ri aufstehen neugierig turnhalle Gegen haute hin guter ferne gib zarte war Heut ein auf las fiel igen Schlupfte aufstehen tat weiterhin schnupfen den Ja er knopf darum blank ri du notig lange etwas', 'lines': [3], 'filepath': 'C:\\Users\\Andre\\Desktop\\onefilewiki\\tt.md'},{'rating': 1.0, 'fullphrase': 'Wer marschen eigentum hinunter jahrlich launigen wir freundes Schritt den pfeifen bei schlief brummte Wunderbar so verwegene em ri aufstehen neugierig turnhalle Gegen haute hin guter ferne gib zarte war Heut ein auf las fiel igen Schlupfte aufstehen tat weiterhin schnupfen den Ja er knopf darum blank ri du notig lange etwas', 'lines': [3], 'filepath': 'C:\\Users\\Andre\\Desktop\\onefilewiki\\tt.md'},{"lines": [3], "rating": 1.0, "fullphrase": "Wer marschen eigentum hinunter jahrlich launigen wir freundes Schritt den pfeifen bei schlief brummte Wunderbar so verwegene em ri aufstehen neugierig turnhalle Gegen haute hin guter ferne gib zarte war Heut ein auf las fiel igen Schlupfte aufstehen tat weiterhin schnupfen den Ja er knopf darum blank ri du notig lange etwas", "filepath": "C:\\Users\\Andre\\Desktop\\onefilewiki\\tt.md"}], "searchterms": ["hinunter", "jahrlich"]})
		queryResult = json.dumps({"type": "fulltextsearch", "data": [{"lines": [15], "rating": 1.0, "fullphrase": "Gern pa da uber kerl frei kaum um grad en Hol bis euern habet gro viere hoher trost Schnupfen das sag die aufraumen des plotzlich bettstatt Tat hinuber mit kleines ein fingern das nachher unruhig Gewandert er bekummert er uberhaupt vogelnest pa stadtchen Eigentlich ubelnehmen vertreiben schuttelte em he wohlgefuhl dammerigen zu wo Stillen des nun lichten gerbers langsam Sa wanderer lampchen so arbeiter lauschte se Indem du alten reden in deren am funfe um faden Wunschte wo gerberei rabatten gesellen du konntest schmalen je so", "filepath": "C:\\Users\\Andre\\Desktop\\zehnWikiseiten\\c.md"}, {"lines": [17], "rating": 1.0, "fullphrase": "Auf jemand daumen geh linken lag armeln kleide nimmer Grasplatz zufrieden was aus wohnstube Du hatt je ku habs leid nest Gespielt je erzahlen mi wo schonste ob Gesagt lustig wo hinter zu gefuhl musset so er burste Gescheite furchtete art bettstatt sorglosen verweilen dir wei von Tadellos brannten her war sto was erschien gesellen Abstellte das zuschauer der rausperte vogelnest plotzlich ein Vor begierig gespielt hin ein zinnerne tag Hast gebe der dran mir dies seid ehe", "filepath": "C:\\Users\\Andre\\Desktop\\zehnWikiseiten\\h.md"}, {"lines": [15, 17], "rating": 0.94, "fullphrase": "Gern pa da uber kerl frei kaum um grad en Hol bis euern habet gro viere hoher trost Schnupfen das sag die aufraumen des plotzlich bettstatt Tat hinuber mit kleines ein fingern das nachher unruhig Gewandert er bekummert er uberhaupt vogelnest pa stadtchen Eigentlich ubelnehmen vertreiben schuttelte em he wohlgefuhl dammerigen zu wo Stillen des nun lichten gerbers langsam Sa wanderer lampchen so arbeiter lauschte se Indem du alten reden in deren am funfe um faden Wunschte wo gerberei rabatten gesellen du konntest schmalen je so...Endigend befehlen gedichte er zu ziemlich Habet en armen haben zu wu Wo wo durchs kuhlen freund in fragte schlie um Leuchter ist las verlohnt achtzehn sie gru hausherr Bummelte gesprach vollbart gespielt kam hut neunzehn Hubschen doppelte ja schonste bummelte ja schreien pa pa befehlen Nichtstun aufstehen behaglich mu ja an belustigt dammerung plotzlich", "filepath": "C:\\Users\\Andre\\Desktop\\zehnWikiseiten\\c.md"}, {"lines": [13, 25], "rating": 0.68, "fullphrase": "In ja unbeirrt endigend erzahlen ubrigens du se schuppen Ei fingern namlich an ri wartete es speisen gefallt stiefel Unwissend geblendet gestrigen rausperte um bettstatt bi vergnugen Wu gegangen se liebsten gewartet vergnugt ja unbeirrt schuppen Sind erst rand im es la bi name Kennt la kinde da ewige hause Mu geschirr in herunter kurioses trostlos schlecht getraumt Land er oben te kein lass gern mich je La da viehmarkt ja im ausgeruht duftenden Erzahlen doppelte aufstand wu er gerberei la zwischen pa...Sog die schonheit duftenden hol plotzlich spazieren Kummer fragen worden eck und daheim treppe tat gruben Dus lag lassig handen unterm lauter stimme Streckte halbwegs herunter nochmals schreien es pa Du feinheit er du kindbett marschen te Augenblick vielleicht am achthausen vielleicht la erkundigte da Vor wenn tag sohn drei duse mich flei", "filepath": "C:\\Users\\Andre\\Desktop\\zehnWikiseiten\\i.md"}, {"lines": [13, 31], "rating": 0.59, "fullphrase": "In ja unbeirrt endigend erzahlen ubrigens du se schuppen Ei fingern namlich an ri wartete es speisen gefallt stiefel Unwissend geblendet gestrigen rausperte um bettstatt bi vergnugen Wu gegangen se liebsten gewartet vergnugt ja unbeirrt schuppen Sind erst rand im es la bi name Kennt la kinde da ewige hause Mu geschirr in herunter kurioses trostlos schlecht getraumt Land er oben te kein lass gern mich je La da viehmarkt ja im ausgeruht duftenden Erzahlen doppelte aufstand wu er gerberei la zwischen pa...Nie sogar tur lagen nun klage Feinen flu servus feucht dus bis vor jahren regnet Ausblasen ein filzhutes tat tat zuschauer plotzlich Zum mit ins mir riefe ihren zahne Vor mannsbild dahinging aufstehen senkrecht oha Geburstet zog man liebevoll einfacher verlangst tur hei", "filepath": "C:\\Users\\Andre\\Desktop\\zehnWikiseiten\\i.md"}, {"lines": [3, 25], "rating": 0.21, "fullphrase": "Em verdrossen fluchtigen wasserkrug am dazwischen getunchten so nachmittag Im ebenso buckte er diesem fremde durren sitzen Ei hing zehn ab wach ture am Tadellos her mit jenseits mitreden betrubte kollegen las Ja anzeichen en fu vorbeugte bettstatt Extra halbe reden im es Brotlose nur ziemlich aus lachelte hat blo...Sog die schonheit duftenden hol plotzlich spazieren Kummer fragen worden eck und daheim treppe tat gruben Dus lag lassig handen unterm lauter stimme Streckte halbwegs herunter nochmals schreien es pa Du feinheit er du kindbett marschen te Augenblick vielleicht am achthausen vielleicht la erkundigte da Vor wenn tag sohn drei duse mich flei", "filepath": "C:\\Users\\Andre\\Desktop\\zehnWikiseiten\\i.md"}, {"lines": [3, 31], "rating": 0.18, "fullphrase": "Em verdrossen fluchtigen wasserkrug am dazwischen getunchten so nachmittag Im ebenso buckte er diesem fremde durren sitzen Ei hing zehn ab wach ture am Tadellos her mit jenseits mitreden betrubte kollegen las Ja anzeichen en fu vorbeugte bettstatt Extra halbe reden im es Brotlose nur ziemlich aus lachelte hat blo...Nie sogar tur lagen nun klage Feinen flu servus feucht dus bis vor jahren regnet Ausblasen ein filzhutes tat tat zuschauer plotzlich Zum mit ins mir riefe ihren zahne Vor mannsbild dahinging aufstehen senkrecht oha Geburstet zog man liebevoll einfacher verlangst tur hei", "filepath": "C:\\Users\\Andre\\Desktop\\zehnWikiseiten\\i.md"}], "searchterms": ["plotzlich", "bettstatt"]})
		try:
			queryResultParsed = json.loads(queryResult)
			print(queryResultParsed)
			searchType = queryResultParsed["type"]
			data = queryResultParsed["data"]
			if data:
				c = """
					<html>
						<body>
							<style>
								a.fillthediv{display:block;text-decoration: none;}
							</style>
							
					"""
				if searchType == "tagsearch":
					for entry in data:
						print("entry",entry)
						if entry["lines"]:
							for line in entry["lines"]:
								subHtml = """
										<div>
											<a href="{2}::{3}" class="fillthediv">
												<p>file:{0} | line:{1}</p>
												<p style="word-break:break-all"> "{4}"</p>
											</a>
										</div>
										
								""".format(os.path.basename(entry["filepath"]),line,entry["filepath"],entry["lines"],entry["content"])

								c += subHtml
						else:
							subHtml = """
										<div>
											<a href="{1}::{2}" class="fillthediv">
												<p>file: {0}</p>
											</a>
										</div>
										
								""".format(os.path.basename(entry["filepath"]),entry["filepath"],[0])
								
							c += subHtml



				elif searchType == "fulltextsearch":
					try:
						searchTerms = queryResultParsed["searchterms"]
					except:
						pass
					for entry in data:
						if searchTerms:
							l = entry["fullphrase"].split(" ")
							for term in searchTerms:
								for indx, s in enumerate(l):
									if s == term:
										s = "<b style='color:red'>{0}</b>".format(s)
										l[indx] = s
						entry["fullphrase"] = ' '.join(word for word in l)
						subHtml = """
								<div>
									<a href="{2}::{3}" class="fillthediv">
										<p>rating: {0} | file: {5} | lines: {4}</p>
										<p style="word-break:break-all">{1}</p>
									</a>
								</div>
								
						""".format(str(round((float(entry["rating"]) * 100),2)) + "%",entry["fullphrase"],
									entry["filepath"],entry["lines"],entry["lines"][0] if len(entry["lines"]) == 1 else str(entry["lines"][0]) + "-" + str(entry["lines"][-1]),
									os.path.basename(entry["filepath"]))


						c += subHtml
				elif searchType == "deleted":
					pass
				else:
					localApi.error("unsupported query result: " + queryResult)
					return

				c += """
					</body>
				</html>
				"""

				def on_hide():
					pass

				def on_navigate(href):
					#if href == "closePopup":
					#	self.view.hide_popup()
					print(href)
					viewname,linesStr = href.split("::")
					lines = json.loads(linesStr)
					self.view.hide_popup()
					load_and_select(None,viewname,lines[0],lines[-1])

				self.view.show_popup(c,max_width=650,max_height=1080,location=self.view.sel()[0].a,on_navigate=on_navigate,on_hide=on_hide)
		except Exception as E:
			localApi.error(str(E))