"""
HTML renderer for mistletoe.
"""

import re
import sys
import os
from itertools import chain
from urllib.parse import quote
from .block_token import HTMLBlock
from .span_token import HTMLSpan
from .base_renderer import BaseRenderer
import urllib.parse
if sys.version_info < (3, 4):
	from . import _html as html
else:
	import html

urlRegex = re.compile(
		r'^(?:http|ftp)s?://' # http:// or https://
		r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
		r'localhost|' #localhost...
		r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
		r'(?::\d+)?' # optional port
		r'(?:/?|[/?]\S+)$', re.IGNORECASE)


class HTMLRenderer(BaseRenderer):
	"""
	HTML renderer class.

	See mistletoe.base_renderer module for more info.
	"""
	def __init__(self, *extras,path=None,wikilinks=None,base64PathDict=None):
		"""
		Args:
			extras (list): allows subclasses to add even more custom tokens.
		"""
		self.path = path
		self.wikilinks = wikilinks
		self.base64PathDict = base64PathDict
		self._suppress_ptag_stack = [False]
		super().__init__(*chain((HTMLBlock, HTMLSpan), extras))
		# html.entities.html5 includes entitydefs not ending with ';',
		# CommonMark seems to hate them, so...
		self._stdlib_charref = html._charref
		_charref = re.compile(r'&(#[0-9]+;'
							  r'|#[xX][0-9a-fA-F]+;'
							  r'|[^\t\n\f <&#;]{1,32};)')
		html._charref = _charref

	def __exit__(self, *args):
		super().__exit__(*args)
		html._charref = self._stdlib_charref

	def render_to_plain(self, token):
		if hasattr(token, 'children'):
			inner = [self.render_to_plain(child) for child in token.children]
			return ''.join(inner)
		return self.escape_html(token.content)

	def render_strong(self, token):
		template = '<strong>{}</strong>'
		return template.format(self.render_inner(token))

	def render_emphasis(self, token):
		template = '<em>{}</em>'
		return template.format(self.render_inner(token))

	def render_inline_code(self, token):
		template = '<code>{}</code>'
		inner = html.escape(token.children[0].content)
		return template.format(inner)

	def render_strikethrough(self, token):
		template = '<del>{}</del>'
		return template.format(self.render_inner(token))

	def render_image(self, token):
		template = '<img src="{}" alt="{}"{} />'
		if token.title:
			title = ' title="{}"'.format(self.escape_html(token.title))
		else:
			title = ''

		if self.base64PathDict:
			if token.src.startswith("/"):
				token.src = token.src[1:]
			if token.src in self.base64PathDict:
				token.src = self.base64PathDict[token.src]
				print("HERE")

		print("TOKENSRC",token.src)

		return template.format(token.src, self.render_to_plain(token), title)



	def render_link(self, token):
		template = '<a href="{target}"{title} {wikilink}>{inner}</a>'
		target = self.escape_url(token.target)
		wikilink = ''
		if self.path:
			if not re.match(urlRegex,target):
				print("PATH",self.path)
				dirname = os.path.dirname(self.path)
				dirname = dirname.replace("\\","/")
				print("DIRNAME",dirname)
				if target.startswith("/"):
					target = target[1:]
				target = urllib.parse.unquote(target)
				unresolved_rel_path = os.path.join(dirname,target)
				print("UNRES",unresolved_rel_path)
				normpath = os.path.normpath(unresolved_rel_path)
				print(normpath)
				wikilink = ' data-wikilink="{}"'.format(normpath)

		if token.title:
			title = ' title="{}"'.format(self.escape_html(token.title))
		else:
			title = ''
		inner = self.render_inner(token)
		return template.format(target=target, title=title, wikilink=wikilink, inner=inner)

	def render_auto_link(self, token):
		template = '<a href="{target}">{inner}</a>'
		if token.mailto:
			target = 'mailto:{}'.format(token.target)
		else:
			target = self.escape_url(token.target)
		inner = self.render_inner(token)
		return template.format(target=target, inner=inner)

	def render_escape_sequence(self, token):
		return self.render_inner(token)

	def render_raw_text(self, token):
		return self.escape_html(token.content)

	@staticmethod
	def render_html_span(token):
		return token.content

	def render_heading(self, token):
		template = '<h{level}>{inner}</h{level}>'
		inner = self.render_inner(token)
		return template.format(level=token.level, inner=inner)

	def render_quote(self, token):
		elements = ['<blockquote>']
		self._suppress_ptag_stack.append(False)
		elements.extend([self.render(child) for child in token.children])
		self._suppress_ptag_stack.pop()
		elements.append('</blockquote>')
		return '\n'.join(elements)

	def render_paragraph(self, token):
		if self._suppress_ptag_stack[-1]:
			return '{}'.format(self.render_inner(token))
		return '<p>{}</p>'.format(self.render_inner(token))

	def render_block_code(self, token):
		template = '<pre><code{attr}>{inner}</code></pre>'
		if token.language:
			attr = ' class="{}"'.format('language-{}'.format(self.escape_html(token.language)))
		else:
			attr = ''
		inner = html.escape(token.children[0].content)
		return template.format(attr=attr, inner=inner)

	def render_list(self, token):
		template = '<{tag}{attr}>\n{inner}\n</{tag}>'
		if token.start is not None:
			tag = 'ol'
			attr = ' start="{}"'.format(token.start) if token.start != 1 else ''
		else:
			tag = 'ul'
			attr = ''
		self._suppress_ptag_stack.append(not token.loose)
		inner = '\n'.join([self.render(child) for child in token.children])
		self._suppress_ptag_stack.pop()
		return template.format(tag=tag, attr=attr, inner=inner)

	def render_list_item(self, token):
		if len(token.children) == 0:
			return '<li></li>'
		inner = '\n'.join([self.render(child) for child in token.children])
		inner_template = '\n{}\n'
		if self._suppress_ptag_stack[-1]:
			if token.children[0].__class__.__name__ == 'Paragraph':
				inner_template = inner_template[1:]
			if token.children[-1].__class__.__name__ == 'Paragraph':
				inner_template = inner_template[:-1]
		return '<li>{}</li>'.format(inner_template.format(inner))

	def render_table(self, token):
		# This is actually gross and I wonder if there's a better way to do it.
		#
		# The primary difficulty seems to be passing down alignment options to
		# reach individual cells.
		template = '<table>\n{inner}</table>'
		if hasattr(token, 'header'):
			head_template = '<thead>\n{inner}</thead>\n'
			head_inner = self.render_table_row(token.header, is_header=True)
			head_rendered = head_template.format(inner=head_inner)
		else: head_rendered = ''
		body_template = '<tbody>\n{inner}</tbody>\n'
		body_inner = self.render_inner(token)
		body_rendered = body_template.format(inner=body_inner)
		return template.format(inner=head_rendered+body_rendered)

	def render_table_row(self, token, is_header=False):
		template = '<tr>\n{inner}</tr>\n'
		inner = ''.join([self.render_table_cell(child, is_header)
						 for child in token.children])
		return template.format(inner=inner)

	def render_table_cell(self, token, in_header=False):
		template = '<{tag}{attr}>{inner}</{tag}>\n'
		tag = 'th' if in_header else 'td'
		if token.align is None:
			align = 'left'
		elif token.align == 0:
			align = 'center'
		elif token.align == 1:
			align = 'right'
		attr = ' align="{}"'.format(align)
		inner = self.render_inner(token)
		return template.format(tag=tag, attr=attr, inner=inner)

	@staticmethod
	def render_thematic_break(token):
		return '<hr />'

	@staticmethod
	def render_line_break(token):
		return '\n' if token.soft else '<br />\n'

	@staticmethod
	def render_html_block(token):
		return token.content

	def render_document(self, token):
		self.footnotes.update(token.footnotes)
		inner = '\n'.join([self.render(child) for child in token.children])
		return '{}\n'.format(inner) if inner else ''

	@staticmethod
	def escape_html(raw):
		return html.escape(html.unescape(raw)).replace('&#x27;', "'")

	@staticmethod
	def escape_url(raw):
		"""
		Escape urls to prevent code injection craziness. (Hopefully.)
		"""
		return html.escape(quote(html.unescape(raw), safe='/#:()*?=%@+,&'))
