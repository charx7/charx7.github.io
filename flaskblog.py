from flask import Flask, render_template
from utils import get_blog_posts

app = Flask(__name__)

# posts = [
#   {
#     'author': 'Carlos H',
#     'title': 'First post title',
#     'content': 'First post content',
#     'date': 'Jul 17 2020'
#   },
#   {
#     'author': 'Carlos H',
#     'title': 'Second post title',
#     'content': 'Second post content',
#     'date': 'Jul 17 2020'
#   }
# ]

@app.route("/")
@app.route("/home")
def home():
  blog_posts = get_blog_posts()

  return render_template('home.html', posts=blog_posts)

@app.route("/about")
def about():
  return render_template('about.html', title='About')

if __name__ == "__main__":
  app.run(debug=True)