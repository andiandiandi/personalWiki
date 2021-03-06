"""
Block-level tokenizer for mistletoe.
"""
from . import lineManager
from . import block_token

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
	a = tokenize_block(iterable, token_types, {"start":1,"read":0})
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
		for token_type in token_types:
			if token_type.start(line):
				spannew = {"start":span["start"] + span["read"],"read":0}
				result = token_type.read(lines, spannew)
				if result is not None:
					parse_buffer.append((token_type, result,{"start":spannew["start"],"read": spannew["read"]}))
					span["read"] += spannew["read"]
					break
		else:  # unmatched newlines
			next(lines)
			span["read"] = lines.index() + 1
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
		#print("type",token_type)
		#print("result",result)
		#print("span",span)
		token = token_type(result, span)
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

