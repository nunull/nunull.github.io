all:
	sass sass/main.sass sass/main.css
	python build.py
	git add -A
	git commit -m "Updated content (automatic commit)"
	git push origin master