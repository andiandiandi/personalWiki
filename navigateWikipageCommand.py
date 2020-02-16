import sublime
import sublime_plugin
import os

Navigator = {}


class Navigator():
	def __init__(self):
		self.list_of_full_filepaths = DoublyLinkedList()
		self.current_index = 0

	def debug(self):
		self.list_of_full_filepaths.debug()

	def insert(self,full_filepath):
		self.list_of_full_filepaths.insert(full_filepath)


	def ret_next_filepath(self, forward = True, home = False):
		if home:
			self.list_of_full_filepaths.go_home()
		else:
			if forward:
				self.list_of_full_filepaths.go_forward()
			else:
				self.list_of_full_filepaths.go_back()
		
		return self.list_of_full_filepaths.current.data

def plugin_loaded():
	global Navigator
	Navigator = Navigator()

class NavigateWikipageCommand(sublime_plugin.TextCommand):
	def run(self, edit, forward = True, home=False):
		file_path = Navigator.ret_next_filepath(forward = forward, home = home)
		self.view.window().open_file(file_path)



class OpenNewFile(sublime_plugin.EventListener):

	def on_activated(self,view):
		global Navigator
		if Navigator:
			if self.is_syntax_supported(view.file_name()):
				Navigator.insert(view.file_name())

	def is_syntax_supported(self, full_filepath_with_name):

		#old way
		#vs =  view.settings()
		#self.syntax = vs.get('syntax')
		#self.syntax = basename(self.syntax).split('.')[0].lower() if self.syntax != None else "plain text"

		self.filetype = OpenNewFile.path_to_fileextension(full_filepath_with_name)

		if self.filetype == ".md":
			return True

		return False


	@staticmethod
	def path_to_fileextension(full_filepath_with_name):
		return os.path.splitext(os.path.basename(full_filepath_with_name))[1]


class DListNode:
	"""
	A node in a doubly-linked list.
	"""
	def __init__(self, data=None, prev=None, next=None):
		self.data = data
		self.prev = prev
		self.next = next

	def __repr__(self):
		return repr(self.data)


class DoublyLinkedList:
	def __init__(self):
		"""
		Create a new doubly linked list.
		Takes O(1) time.
		"""
		self.head = None
		self.current = None

	def __repr__(self):
		"""
		Return a string representation of the list.
		Takes O(n) time.
		"""
		nodes = []
		curr = self.head
		while curr:
			nodes.append(repr(curr))
			curr = curr.next
		return '[' + ', '.join(nodes) + ']'

	def insert(self, data):
		"""
		Insert a new element at the end of the list.
		Takes O(n) time.
		"""
		if self.current:
			if data == self.current.data:
					return

		if not self.head:
			self.head = DListNode(data=data)
			self.current = self.head
			print("inserting==prev:{0},next:{1},current:{2}".format(self.current.prev.data if self.current.prev else None,self.current.next.data if self.current.next else None,self.current.data))
			return
		curr = self.head
		while curr is not self.current:
			curr = curr.next
		curr.next = DListNode(data=data, prev=curr)
		self.current = curr.next
		print("inserting==prev:{0},next:{1},current:{2}".format(self.current.prev.data if self.current.prev else None,self.current.next.data if self.current.next else None,self.current.data))

	def find(self, key):
		"""
		Search for the first element with `data` matching
		`key`. Return the element or `None` if not found.
		Takes O(n) time.
		"""
		curr = self.head
		while curr and curr.data != key:
			curr = curr.next
		return curr  # Will be None if not found

	def remove_elem(self, node):
		"""
		Unlink an element from the list.
		Takes O(1) time.
		"""
		if node.prev:
			node.prev.next = node.next
		if node.next:
			node.next.prev = node.prev
		if node is self.head:
			self.head = node.next
		node.prev = None
		node.next = None

	def remove(self, key):
		"""
		Remove the first occurrence of `key` in the list.
		Takes O(n) time.
		"""
		elem = self.find(key)
		if not elem:
			return
		self.remove_elem(elem)

	def go_back(self):
		if self.current.prev:
			self.current = self.current.prev
		print("back==prev:{0},next:{1},current:{2}".format(self.current.prev.data if self.current.prev else None,self.current.next.data if self.current.next else None,self.current.data))

	def go_forward(self):
		if self.current.next:
			self.current = self.current.next
		print("forward==prev:{0},next:{1},current:{2}".format(self.current.prev.data if self.current.prev else None,self.current.next.data if self.current.next else None,self.current.data))

	def go_home(self):
		if self.head:
			self.insert(self.head.data)

	def reverse(self):
		"""
		Reverse the list in-place.
		Takes O(n) time.
		"""
		curr = self.head
		prev_node = None
		while curr:
			prev_node = curr.prev
			curr.prev = curr.next
			curr.next = prev_node
			curr = curr.prev
		self.head = prev_node.prev

	def debug(self):
		pass

   