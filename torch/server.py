import os
from flask import Flask, send_from_directory, jsonify, make_response, request
from flask_cors import CORS
from pathlib import Path
import requests
from bs4 import BeautifulSoup, NavigableString, Doctype
from sentence_transformers import SentenceTransformer
import torch
import html
# from nltk.tokenize import sent_tokenize
# import nltk
# nltk.download('punkt')

app = Flask(__name__, static_folder="dist")
CORS(app)

@app.route("/test", defaults={"path": ""})
@app.route("/test/<path:path>")
def serve_files_in_folder(path):
    return send_from_directory("test", path)

@app.route("/api/test")
def get_folders_with_files():
    folder_path = "test"
    folders = []

    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        if os.path.isdir(item_path):
            files = [{"name": file, "url": f"http://localhost:3000/test/{item}/{file}"} for file in os.listdir(item_path)]
            folders.append({"name": item, "files": files})

    response = make_response(jsonify({"folders": folders}))
    response.headers['Content-Type'] = 'application/json'
    return response

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_vue_app(path):
    return send_from_directory(app.static_folder, "index.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(port=port)

# def extract_text_from_html(html_content):
#     soup = BeautifulSoup(html_content, 'lxml')
#     text = soup.get_text(separator=' ')
#     return text
# def highlight_text(text, color):
#     return f'{text}'
def highlight_html_sentence(sentence, color):
    return f'<span style="background-color: {color}">{sentence}</span>'

model_name = "all-MiniLM-L6-v2"
model = SentenceTransformer(model_name)

def cosine_similarity(vec1, vec2):
    return torch.nn.functional.cosine_similarity(vec1, vec2, dim=-1).item()

def encode(text):
    return model.encode([text], convert_to_tensor=True)

def compare_and_highlight(html1, html2, similarity_threshold=0.68):
    soup1 = BeautifulSoup(html1, "html.parser")
    soup2 = BeautifulSoup(html2, "html.parser")

    def iterate_text_nodes(soup):
        for tag in soup.descendants:
            if not isinstance(tag, Doctype) and isinstance(tag, NavigableString) and tag.strip():
                yield tag

    def highlight_text_node(node, soup, color):
        if node is not None:
            highlighted_text = highlight_html_sentence(str(node), color)
            new_soup = BeautifulSoup(highlighted_text, "html.parser")
            new_tag = soup.new_tag(new_soup.span.name)
            new_tag.string = new_soup.span.string
            new_tag['style'] = new_soup.span['style']
            node.replace_with(new_tag)

    text_nodes1 = list(iterate_text_nodes(soup1))
    text_nodes2 = list(iterate_text_nodes(soup2))

    for text_node1 in text_nodes1:
        max_similarity = 0
        # max_similarity_text_node = None
        for text_node2 in text_nodes2:
            vec1 = encode(text_node1)
            vec2 = encode(text_node2)

            similarity = cosine_similarity(vec1, vec2)

            if similarity > max_similarity:
                max_similarity = similarity
                # max_similarity_text_node = text_node2

        if max_similarity <= similarity_threshold:
            highlight_text_node(text_node1, soup1, "orange")

    for text_node2 in text_nodes2:
        max_similarity = 0
        # max_similarity_text_node = None
        for text_node1 in text_nodes1:
            vec2 = encode(text_node2)
            vec1 = encode(text_node1)
            similarity = cosine_similarity(vec2, vec1)

            if similarity > max_similarity:
                max_similarity = similarity
                # max_similarity_text_node = text_node1

        if max_similarity <= similarity_threshold:
            highlight_text_node(text_node2, soup2, "orange")

    highlighted_html1 = str(soup1)
    highlighted_html2 = str(soup2)

    return highlighted_html1, highlighted_html2

@app.route('/api/compare', methods=['POST'])
def compare_files():
    data = request.get_json()
    html1 = data.get('html1')
    html2 = data.get('html2')

    if not html1 or not html2:
        return jsonify({'error': 'Both html1 and html2 are required'}), 400

    highlighted_html1, highlighted_html2 = compare_and_highlight(html1, html2)
    return jsonify({
        'highlightedHtml1': highlighted_html1,
        'highlightedHtml2': highlighted_html2
    })


