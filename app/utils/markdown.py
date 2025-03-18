from markdown import markdown
from bs4 import BeautifulSoup

allowed_html_elements = [
    "a", "b", "blockquote", "br", "code", "dd", "del", "details", "div", "dl", "dt", "em",
    "h1", "h2", "h3", "h4", "h5", "h6", "hr", "i", "ins", "kbd", "li", "ol", "p", "pre", "q",
    "rp", "rt", "ruby", "s", "samp", "source", "span", "strike", "strong", "sub", "summary",
    "sup", "table", "tbody", "td", "tfoot", "th", "thead", "tr", "ul", "var"
]

allowed_attributes = {
    "div": ["data-*", "class"]
}

def sanitize_html(input_html):
    soup = BeautifulSoup(input_html, "html.parser")

    for tag in soup.find_all(True):
        if tag.name not in allowed_html_elements:
            tag.decompose()
    
    for tag in soup.find_all(True):
        for attr in list(tag.attrs):
            if not any(attr.startswith(allowed) for allowed in allowed_attributes.get(tag.name, [])):
                del tag[attr]

    return str(soup)

def limited_markdown_plugin(content):
    parsed = markdown(content)
    soup = BeautifulSoup(parsed, "html.parser")

    for tag in soup.find_all():
        if tag.name not in ["p", "strong", "em", "code", "pre", "text", "inlineCode", "heading"]:
            tag.unwrap()

    return str(soup)

def process_content(input_content, sanitize=False, html=False):
    if html:
        sanitized_content = sanitize_html(input_content) if sanitize else input_content
        return sanitized_content

    return limited_markdown_plugin(input_content)
