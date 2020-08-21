import markdown
import markdown.extensions.fenced_code
import markdown.extensions.codehilite

import os

CONTENT_PATH = "content/blog/"

# TODO refactor get_portlio_posts and get_blog_posts funcs into one
def get_portfolio_posts():
  '''
    Returns:
      (list(dict)): list of all written portfolio posts parsed into python
                    dictionaries.
  '''
  CONTENT_PATH = "content/portfolio/"

  files_list = os.listdir(CONTENT_PATH)
  
  portfolio_posts_dict_list = []
  for file in files_list:
    FILE_PATH = CONTENT_PATH + file

    portfolio_posts_dict_list.append(transform_content(FILE_PATH))

  return portfolio_posts_dict_list

def get_blog_posts():
  '''
    Returns:
      (list<dict>): list of all the written blog posts in dictonary format 
  '''
  files_list = os.listdir(CONTENT_PATH)
  
  blog_posts_dict_list = []
  for file in files_list:
    FILE_PATH = CONTENT_PATH + file

    blog_posts_dict_list.append(transform_content(FILE_PATH))

  return blog_posts_dict_list

def transform_content(PATH_TO_CONTENT):
  '''
    Parses the written markdown files on the content path and transforms them into
    a dictonary of the form:
    dict = {
      **metadata_keys: metadata_values,
      "html": parsed html value using python's Markdown package
    }

    *NOTE: Metadata keys are defined on the markdown files as
    ---
    key_name: value
    ---

    Returns:
      dict: A blog post parsed into a dictionary object 
  '''
  # open the md file and transform into html
  with open(PATH_TO_CONTENT, "r") as file:    
    content_file = file.read()
    # create the md obj
    md = markdown.Markdown(extensions = ["codehilite", "fenced_code", 'meta'])
    
    html = md.convert(content_file)
    
    # dict comprehension for extracting the content not in a list format
    metadata_dict = {key:value[0] for (key, value) in md.Meta.items()}
    
    print(md.Meta)
    # here the ** are used to extend the dict returned by md.Meta the metadata info    
    return {
      **metadata_dict,
      "html": html
    }
