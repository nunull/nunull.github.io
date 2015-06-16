all:
	sass --sourcemap=none --no-cache cms/main.sass cms/main.css
	cd cms && python build.py /web/nunull.github.io/
deploy:
	sass --sourcemap=none --no-cache cms/main.sass cms/main.css
	cd cms && python build.py /
	git add -A
	git commit -m "Updated content (automatic commit)"
	git push origin master
