# Use make for local testing and make deploy to deploy to GitHub Pages

# Local basepath
BASEPATH=/web/nunull.github.io/

compile:
	sass --sourcemap=none --no-cache cms/main.sass cms/main.css
	cd cms && python build.py $(BASEPATH)
push:
	git add -A
	git commit -m "Updated content (automatic commit)"
	git push origin master

all: compile
deploy: BASEPATH=/
deploy: compile push