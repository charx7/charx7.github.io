import markdown
import os

CONTENT_PATH = "content/blog/"

def get_blog_posts():
  files_list = os.listdir(CONTENT_PATH)
  
  blog_posts_dict_list = []
  for file in files_list:
    FILE_PATH = CONTENT_PATH + file

    blog_posts_dict_list.append(transform_content(FILE_PATH))

  return blog_posts_dict_list

def transform_content(PATH_TO_CONTENT):
  # open the md file and transform into html
  with open(PATH_TO_CONTENT, "r") as file:    
    content_file = file.read()
    # create the md obj
    md = markdown.Markdown(extensions = ["fenced_code", "codehilite", "toc", 'meta'])
    
    html = md.convert(content_file)
    
    # dict comprehension for extracting the content not in a list format
    metadata_dict = {key:value[0] for (key, value) in md.Meta.items()}
    
    print(md.Meta)
    # here the ** are used to extend the dict returned by md.Meta the metadata info    
    return {
      **metadata_dict,
      "html": html
    }
