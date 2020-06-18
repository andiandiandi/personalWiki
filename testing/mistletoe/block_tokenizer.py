"""
Block-level tokenizer for mistletoe.
"""
from mistletoe import lineManager
from mistletoe import block_token

stack = None
linenum = -1

class Stack(object):
	def __init__(self, name):
		self.items = []
		self.name = name

	def push(self, item):
		print("adding to stack",item)
		self.items.append(item)

	def pop(self):
		return self.items.pop()

	def peek(self):
		if not self.items:
			return None
		return self.items[-1]
	
	def clearToFirst(self):
		while self.size() > 1:
			self.pop()

	def clear(self):
		self.items = []

	def print(self):
		for x in self.items:
			if type(x) == Stack:
				x.print()
			else:
				print(name,x)

	def isEmpty(self):
		return len(self.items) == 0


class FileWrapper:
	def __init__(self, lines):
		self.lines = lines if isinstance(lines, list) else list(lines)
		self._index = -1
		self._anchor = 0

	def __next__(self):
		if self._index + 1 < len(self.lines):
			self._index += 1
			return self.lines[self._index]
		raise StopIteration

	def index(self):
		return self._index
	def __iter__(self):
		return self

	def __repr__(self):
		return repr(self.lines[self._index+1:])

	def anchor(self):
		self._anchor = self._index

	def reset(self):
		self._index = self._anchor

	def peek(self):
		if self._index + 1 < len(self.lines):
			return self.lines[self._index+1]
		return None

	def backstep(self):
		if self._index != -1:
			self._index -= 1

def tokenize(iterable, token_types):
	"""
	Searches for token_types in iterable.

	Args:
		iterable (list): user input lines to be parsed.
		token_types (list): a list of block-level token constructors.

	Returns:
		block-level token instances.
	"""
	global stack
	stack = Stack("master")
	a = tokenize_block(iterable, token_types, {"start":1,"read":0})
	stack = None
	global linenum
	linenum = 0
	b = make_tokens(a)
	return b


def tokenize_block(iterable, token_types, span = None):
	"""
	Returns a list of pairs (token_type, read_result).

	Footnotes are parsed here, but span-level parsing has not
	started yet.
	"""
	lines = FileWrapper(iterable)
	parse_buffer = ParseBuffer()
	line = lines.peek()


	while line is not None:
		print("parsing line",line)
		print("line is at index",lines.index()+2)
		for token_type in token_types:
			if token_type.start(line):
				spannew = {"start":span["start"] + span["read"],"read":0}
				print("calling result with spannew",spannew)
				print("t",token_type)
				result = token_type.read(lines, spannew)
				if result is not None:
					print("result for line calculated",line)
					print("spannew after result",spannew)
					parse_buffer.append((token_type, result,{"start":spannew["start"]," read": spannew["read"]}))
					span["read"] += spannew["read"]
					print("updating span",span)
					print("after updating span is now", span)
					break
		else:  # unmatched newlines
			next(lines)
			span["read"] = lines.index() + 1
			print("no lines found, span is now", span)
			parse_buffer.loose = True
		line = lines.peek()


	return parse_buffer


def make_tokens(parse_buffer):
	"""
	Takes a list of pairs (token_type, read_result) and
	applies token_type(read_result).

	Footnotes are already parsed before this point,
	and span-level parsing is started here.
	"""
	tokens = []
	for token_type, result, span in parse_buffer:
		print(token_type,span)
		token = token_type(result)
		if token is not None:
			tokens.append(token)
	return tokens


class ParseBuffer(list):
	"""
	A wrapper around builtin list,
	so that setattr(list, 'loose') is legal.
	"""
	def __init__(self, *args):
		super().__init__(*args)
		self.loose = False
		self.read = 0

