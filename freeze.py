""" Flask freezer """
#from shutil import copyfile
from flask_frozen import Freezer
from flaskblog import app


Freezer = Freezer(app)


if __name__ == "__main__":
    Freezer.freeze()

    # copy the _redirects file to the /build path
    #copyfile("_redirects", "src/build/_redirects")
