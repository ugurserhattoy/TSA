import markdown2

def read_md_file_to_html(path):
    with open(path, encoding="utf-8") as f:
        md_text = f.read()
    return markdown2.markdown(md_text)