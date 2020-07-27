---
type: How to create a Static Blog from Scratch Using Python [1]
post_id: 1
tags: python, flask, frozen-flask, jinja, markdown
author: Carlos Huerta 
title: Static website using python, flask, and frozen-flask (1)
date: Jul 25 2020
---

### A blog post about building a blog
To start-off this personal/portfolio page we are going to get 'meta' :emoji: we will dwell into the first series of blog-posts about :drum: how to make a static blog and deploy it into **github-pages**.

I have wanted to make a personal web-page for quite some time as well as *dust off* my web-dev skills :broom:, so I tried many multiple static web page generators to my surprise I didn't like any of them that much and I felt that many of them did give me the pedagogic purpose that I was looking for... At the end I ended up coding a static web-site from scratch as I felt that It would give me the best learning experience one can afford.

## 1. Set-up a flask blog to be frozen
The first thing that we need to do is to set-up a flask dev environment, the standard way would be to create a **virtual environment** and install all the required dependencies. I will be assuming you have python3 previously installed on your computer and that you are using bash commands, sorry windows users :P best switch to mac/linux before you start pulling your hair-off.
```bash
python3 -m venv blog-env
```

Now we will cd into it and activate the newly created **venv**. 
```bash
cd blog-env/bin
source activate 
```

Now the text `(blog-env)` or any other name you gave the venv will be appearing before your bash prompt, but if you need to verify, I'd suggest running the `which` command just to make sure of it.
```bash
which pip
```
This command should point to pip inside your virtual environment and not to the pip in your home directory. Now we can proceed to install all the required dependencies of our project:
```bash
pip install flask markdown
```

* **flask** will be used for the back-end services (before the freeze).
* **markdown** will be used for converting our previously done markdown blog posts into HTML. 

Now let's create a folder that will contain our blog with the following file structure:
```bash
tree
.
├── content
│   ├── blog
│   └── portfolio
├── flaskblog.py
├── static
│   ├── css
│   ├── images
│   └── js
├── templates
└── utils.py
```
* The `content` folder will be containing our blog posts as well as our portfolio projects,
* The `static` folder will be containing our required `css` and `js` libraries for formatting, in this case we will be using the *Bootstrap* css frame-work to give our blog a more *modern* look.
* The `templates` folder will be containing our necessary `jinja` templates that will be rendered using flask.
* `flaskblog.py` and `utils.py` contain the programming logic of our basic blog site :D.  

Let's dive into `flaskblog.py` for a minimal set-up:
<div class="input">
  MY_PROJECT_NAME/flaskblog.py
</div>
```python
from flask import Flask, render_template
from utils import get_blog_posts

app = Flask(__name__)

@app.route("/")
@app.route("/index.html")
def index():
  bio_small = """
  Insert your bio-info here!
  """

  blog_posts = get_blog_posts()

  return render_template('home.html', posts=blog_posts, bio_small=bio_small)
```

The `utils.py` will contain some basic util functions that our flask-blog page will need.

<div class="input">
  MY_PROJECT_NAME/utils.py
</div>
```python
def get_blog_posts():
  print('I should return all the blog posts!')
  return []
```

Don't forget home.html...

<div class="input">
  MY_PROJECT_NAME/templates/home.html
</div>
```html
<!DOCTYPE html>
<html>
<head>
    <!-- Required meta tags -->
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    {% if title %}
        <title>Flask Blog - {{ title }}</title>
    {% else %}
        <title>Flask Blog</title>
    {% endif %}
</head>
<body>
    <h1> Hello World! </h1>
    <p>{{ bio_small }}</p>
</body>
</html>
```
You may have noticed some veeery strange naming in the `flaskblog.py` file we named our home page `index.htm`, the reason behind this is that when we will generate the static files to be deployed into *github-pages* we will need an entry point named `index.html` that alongside how `frozen-flask` freezes our flask web-page. More of this in the upcoming blog posts...
We should be able to run a basic functioning web-page *locally* via the `python flaskblog.py` command! et voila we now have the basic structure for a simple personal blog page.

In part 2, we will see how we can write our blog content in the *markdown* format and parse it to working *html* that will be rendered by our templates.