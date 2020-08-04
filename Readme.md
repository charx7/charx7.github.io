# Personal Portfolio Page

Made with Frozen-Flask, Flask and Bootstrap deployed using github-pages

## Deployment
With our venv activated run the freeze.py script to generate the build directory
```
python freeze.py
```
In case you haven't, create a new git branch called `gh-pages`. `git branch github-pages`.
Switch to the gh-pages branch and deploy the content.
```
git checkout gh-pages
git add build && git commit -m "build subtree commit"
```
Push to the `gh-pages` branch on gh.
```
git subtree push --prefix dist origin gh-pages
```
