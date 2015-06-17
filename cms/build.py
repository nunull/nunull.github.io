import re, shutil, os.path, sys, operator

def read():
	pages = {}

	f = open('../content.md', 'r')
	md = f.read()
	f.close()

	parts = md.split('---\n')

	options = parts.pop(0).split('\n')
	parsedOptions = {}
	for option in options:
		optionParts = option.split(':', 1)

		if(len(optionParts) == 2):
			key = optionParts[0].strip()
			value = optionParts[1].strip()
			parsedOptions[key] = value

	for i, part in enumerate(parts[::2]):
		page = {}
		page['id'] = i

		metaStr = part.split('\n')
		page['content'] = parts[i*2+1]

		for m in metaStr:
			p = m.split(':')
			if len(p) == 2:
				page[p[0]] = p[1].strip()

		if 'slug' not in page:
			page['slug'] = page['name'].lower()

		pages[page['slug']] = page

	return (pages, parsedOptions)

def parse(pages):
	def countLeadingChars(char, str):
		return len(str) - len(str.lstrip(char))

	def formatTag(mdTag, htmlTag, md):
		mdTag = re.escape(mdTag)
		return re.sub(r'{0}([^{0}]*){0}'.format(mdTag), r'<{0}>\1</{0}>'.format(htmlTag), md)

	linkRegEx = re.compile(r'(?<=[ >])([a-z]+:\/\/([\w.\/\-+~?=#&%,@;]*))')
	imgAbsRegEx = re.compile(r'\(img ([a-z]+:\/\/([\w.\/\-+~?=#&%,@;]*))\)')
	imgRelRegEx = re.compile(r'\(img ([^\)]+)\)')

	for slug in pages:
		content = pages[slug]['content']
		lines = content.split('\n')

		prevListLevel = 0
		html = ''
		for line in lines:
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

			# Images
			line = imgAbsRegEx.sub(r'<img src="\1">', line)
			line = imgRelRegEx.sub(r'<img src="{0}{1}/\1">'.format(baseUrl, 'cms/res'), line)

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

def write(pages, options):
	def compile(template, page):
		pages['index']['slug'] = ''

		# Create a sorted representation of the pages dict
		sortedPages = sorted(pages.items(), key=operator.itemgetter(1))

		navHtml = ''
		for cur in sortedPages:
			classes = ''
			if page['slug'] == cur[1]['slug']:
				classes = 'class="active"'

			navHtml += '\n<a href="{0}{1}"{2}>{3}</a>'.format(baseUrl, cur[1]['slug'], classes, cur[1]['name'])

		return template.replace('{{content}}', page['content']).replace('{{nav}}', navHtml)

	def writePage(path, html):
		f = open('../{0}'.format(path), 'w')
		f.write(html)
		f.close()

	baseUrl = options['baseUrl']

	f = open('template.html', 'r')
	template = f.read()
	f.close()

	for key in options:
		template = template.replace('{{' + key + '}}', options[key])

	index = pages['index']
	# del pages['index']

	err = pages['404']
	del pages['404']

	writePage('index.html', compile(template, index))
	writePage('404.html', compile(template, err))
	for slug in pages:
		page = pages[slug]

		path = '../{0}'.format(page['slug'])
		if not os.path.exists(path):
			os.makedirs(path)

		page['content'] = page['content'].replace('{{baseUrl}}', baseUrl)
		writePage('{0}/index.html'.format(page['slug']), compile(template, page))

baseUrl = sys.argv[1]

data = read()
pages = parse(data[0])
options = data[1]
options['baseUrl'] = baseUrl
options['css'] = '{0}cms/main.css'.format(baseUrl)
write(pages, options)