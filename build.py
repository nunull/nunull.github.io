import re, shutil, os.path

def read():
	pages = {}

	f = open('content.md', 'r')
	md = f.read()
	f.close()

	parts = md.split('---\n')
	parts.pop(0)
	for i, part in enumerate(parts[::2]):
		page = {}

		metaStr = part.split('\n')
		page['content'] = parts[i*2+1]

		for m in metaStr:
			p = m.split(':')
			if len(p) == 2:
				page[p[0]] = p[1].strip()

		if 'slug' not in page:
			page['slug'] = page['name'].lower()

		pages[page['slug']] = page

	return pages

def parse(pages):
	def countLeadingChars(char, str):
		return len(str) - len(str.lstrip(char))

	def formatTag(mdTag, htmlTag, md):
		mdTag = re.escape(mdTag)
		return re.sub(r'{0}([^{0}]*){0}'.format(mdTag), r'<{0}>\1</{0}>'.format(htmlTag), md)

	linkRegEx = re.compile(r'([a-z]+:\/\/([\w.\/\-+~?=#&%,@;]*))')

	for slug in pages:
		content = pages[slug]['content']
		lines = content.split('\n')

		prevListLevel = 0
		html = ''
		for line in lines:
			# todo: htmlentities

			headerLevel = countLeadingChars('#', line)
			listLevel = 0

			# Header
			if headerLevel > 0 and headerLevel <= 6:
				line = '<h{0}>{1}</h{0}>'.format(headerLevel, line.split(' ', 1)[1])

			# List item
			elif line.find('- ') == 0:
				listLevel = countLeadingChars('\t', line) + 1
				line = '<li>{}</li>'.format(line.split(' ', 1)[1])

			# Horizontal row
			elif countLeadingChars('-', line) == len(line) and len(line) > 2:
				line = '<hr>'

			# Preformatted and code
			elif line.find('\t') == 0:
				line = '<pre><code>{}</pre></code>'.format(line[1:].replace('\t', '    '))

			# Paragraph
			elif len(line.strip()) != 0:
				line = '<p>{}</p>'.format(line)

			# Insert list tags
			listLevelDiff = listLevel - prevListLevel
			if listLevelDiff > 0:
				html += '<ul>' * listLevelDiff
			elif listLevelDiff < 0:
				html += '</ul>' * (-listLevelDiff)
			prevListLevel = listLevel

			# Links
			line = linkRegEx.sub(r'<a href="\1">\2</a>', line)

			# Bold, italic, strike and code
			line = formatTag('**', 'b', line)
			line = formatTag('*', 'i', line)
			line = formatTag('~', 'strike', line)
			line = formatTag('`', 'code', line)

			html += line

		pages[slug]['content'] = html

	return pages

def write(pages):
	def compile(template, content):
		return template.replace('{{content}}', content)

	def writePage(path, html):
		f = open(path, 'w')
		f.write(html)
		f.close()

	f = open('template.html', 'r')
	template = f.read()
	f.close()

	index = pages['index']
	del pages['index']

	navHtml = '<a href="/">{0}</a>'.format(index['name'])
	for slug in pages:
		page = pages[slug]

		navHtml += '\n<a href="/{0}">{1}</a>'.format(page['slug'], page['name'])

	template = template.replace('{{nav}}', navHtml)

	writePage('index.html', compile(template, index['content']))
	for slug in pages:
		page = pages[slug]

		if not os.path.exists(page['slug']):
			os.makedirs(page['slug'])
		writePage('{0}/index.html'.format(page['slug']), compile(template, page['content']))

write(parse(read()))