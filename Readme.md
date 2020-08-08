# Personal Portfolio Page

Made with Frozen-Flask, Flask and Bootstrap deployed using github-pages

## Deployment
With our venv activated run the freeze.py script to generate the build directory
```
python freeze.py
```
In case you haven't, create a new git branch called `gh-pages` and merge the new content developed in the master branch. `git branch github-pages`.
Switch to the gh-pages branch and deploy the content.
```
git checkout gh-pages
git merge master
git add build && git commit -m "build subtree commit"
```
Push to the `gh-pages` branch on gh.
```
git subtree push --prefix dist origin gh-pages
```
Make sure the file CNAME with the content `charx7.me` exists on the build directory.