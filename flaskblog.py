import json
import math

from flask import Flask, render_template, redirect, url_for, abort
from pygments.formatters import HtmlFormatter
from utils import get_blog_posts, get_portfolio_posts

app = Flask(__name__)

@app.route("/")
@app.route("/index.html")
def index():
  DEFAULT_DESCRIPTION = """
  Carlos Huerta blog/portfolio page on data science and programming. 
  /blog/ page contains tutorials about DS and /portfolio/ shows some of my projects.
  """

  bio_small = """
  Data Science and Machine Learning Enthusiast, 
  currently working with Dynamic Bayesian Networks models for gene network reconstruction.
  Love programming, modelling, web-development, and data engineering.
  Curious for A.I. research - model explainability and Natural Language Processing.

  Ensembles over Deep Neural Networks!
  """

  blog_posts = get_blog_posts()

  return render_template('home.html', posts=blog_posts,
    num_posts=len(blog_posts), bio_small=bio_small, description = DEFAULT_DESCRIPTION)

@app.route("/about.html")
def about():
  return render_template('about.html', title='About')

@app.route("/portfolio.html")
def portfolio():
  desc = """
  Carlos Huerta - Personal portfolio page showcasing some of my projects.
  """
  portfolio_posts = get_portfolio_posts()
  # sort posts by id
  portfolio_posts = sorted(portfolio_posts, key=lambda x: int(x['portfolio_id'][0]))

  # transform into list of lists with len 2
  num_rows = math.ceil(len(portfolio_posts) / 2) # because we have 2 elements per row
  t_portfolio_posts = [[] for _ in range(num_rows)]
  
  curr_list_idx = 0
  for idx in range(len(portfolio_posts)):
    # modify the index of the list using modulo max row operations
    if idx > 0 and idx % 2 == 0:
      curr_list_idx = curr_list_idx + 1

    # append to the list of lists
    t_portfolio_posts[curr_list_idx].append(portfolio_posts[idx])

  return render_template('portfolio.html',
    title='Portfolio',
    description = desc,
    posts_list = t_portfolio_posts)

@app.route("/post/<post_id>/")
def post(post_id):
  # Get the specific post from the list of posts
  blog_posts = get_blog_posts()

  print('the type of the post id is: ', type(post_id))
  found_post = None
  for post in blog_posts:
    if post_id == post['post_id']:
      print('Found the post')
      found_post = post

  if found_post:
    # CSS addition for syntax highlighting
    # formatter = HtmlFormatter(style="colorful", full=True, cssclass="codehilite")
    # css_string = formatter.get_style_defs()
    # md_css_string = "<style>" + css_string + "</style>"
    md_css_string = ''
    
    return render_template('post.html', title = post['title'], post = found_post, 
      code_css = md_css_string )
  else:
    return abort(404)

# error handling route
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == "__main__":
  app.run(debug=True)
  