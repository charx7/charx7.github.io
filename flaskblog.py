from flask import Flask, render_template

app = Flask(__name__)

posts = [
  {
    'author': 'Carlos H',
    'title': 'First post title',
    'content': 'First post content',
    'date': 'Jul 17 2020'
  },
  {
    'author': 'Carlos H',
    'title': 'Second post title',
    'content': 'Second post content',
    'date': 'Jul 17 2020'
  }
]

@app.route("/")
@app.route("/home")
def hello():
  return render_template('home.html', posts=posts)

@app.route("/about")
def about():
  return render_template('about.html', title='About')

if __name__ == "__main__":
  app.run(debug=True)