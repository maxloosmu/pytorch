import os
from flask import Flask, send_from_directory, jsonify, make_response, request
from flask_cors import CORS
from pathlib import Path
import requests
from bs4 import BeautifulSoup, NavigableString, Doctype
from sentence_transformers import SentenceTransformer
import torch
import html

# Flask application setup with a static folder
app = Flask(__name__, static_folder="dist")
CORS(app)  # Enable Cross-Origin Resource Sharing (CORS) for all routes

# Route to serve files from the 'test' directory
@app.route("/test", defaults={"path": ""})
@app.route("/test/<path:path>")
def serve_files_in_folder(path):
    return send_from_directory("test", path)

# API endpoint to list folders and files in the 'test' directory
@app.route("/api/test")
def get_folders_with_files():
    folder_path = "test"
    folders = []

    # Loop through items in the folder_path
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        if os.path.isdir(item_path):  # Check if the item is a directory
            # List comprehension to create a list of files with their URLs
            files = [{"name": file, "url": f"http://localhost:3000/test/{item}/{file}"} for file in os.listdir(item_path)]
            folders.append({"name": item, "files": files})

    response = make_response(jsonify({"folders": folders}))
    response.headers['Content-Type'] = 'application/json'
    return response

# Route to serve the main Vue.js application
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_vue_app(path):
    return send_from_directory(app.static_folder, "index.html")

# Main function to run the Flask application
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(port=port)

# Function to highlight sentences in HTML content based on color
def highlight_html_sentence(sentence, color):
    return f'<span style="background-color: {color}">{sentence}</span>'

# Load a Sentence Transformer model for text encoding
model_name = "all-MiniLM-L6-v2"
model = SentenceTransformer(model_name)

# Function to compute cosine similarity between two vectors
def cosine_similarity(vec1, vec2):
    return torch.nn.functional.cosine_similarity(vec1, vec2, dim=-1).item()

# Function to encode text into vector form
def encode(text):
    return model.encode([text], convert_to_tensor=True)

# Function to compare two HTML documents and highlight differences
def compare_and_highlight(html1, html2, similarity_threshold=0.68):
    # Parse HTML content using BeautifulSoup for both documents
    soup1 = BeautifulSoup(html1, "html.parser")
    soup2 = BeautifulSoup(html2, "html.parser")

    # Generator function to iterate through text nodes in a BeautifulSoup object
    def iterate_text_nodes(soup):
        for tag in soup.descendants:  # Loop through all tags in the soup object
            # Yield text nodes that are not Doctype and are not empty
            if not isinstance(tag, Doctype) and isinstance(tag, NavigableString) and tag.strip():
                yield tag

    # Function to highlight a text node with specified color
    def highlight_text_node(node, soup, color):
        if node is not None:  # Ensure the node is not None
            # Generate highlighted HTML text for the node
            highlighted_text = highlight_html_sentence(str(node), color)
            # Parse the highlighted text into a new BeautifulSoup object
            new_soup = BeautifulSoup(highlighted_text, "html.parser")
            # Create a new tag in the original soup to replace the original text node
            new_tag = soup.new_tag(new_soup.span.name)
            new_tag.string = new_soup.span.string
            new_tag['style'] = new_soup.span['style']
            node.replace_with(new_tag)  # Replace the original node with the new highlighted node

    # Collect text nodes from both HTML documents
    text_nodes1 = list(iterate_text_nodes(soup1))
    text_nodes2 = list(iterate_text_nodes(soup2))

    # Compare each text node in the first document against nodes in the second document
    for text_node1 in text_nodes1:
        max_similarity = 0  # Initialize the maximum similarity found for the current node
        for text_node2 in text_nodes2:
            # Encode both text nodes into vectors
            vec1 = encode(text_node1)
            vec2 = encode(text_node2)
            # Calculate cosine similarity between the two vectors
            similarity = cosine_similarity(vec1, vec2)
            # Track the highest similarity found
            if similarity > max_similarity:
                max_similarity = similarity

        # If the highest similarity is below the threshold, highlight the node
        if max_similarity <= similarity_threshold:
            highlight_text_node(text_node1, soup1, "orange")

    # Repeat the process for the second document
    for text_node2 in text_nodes2:
        max_similarity = 0  # Initialize the maximum similarity found for the current node
        for text_node1 in text_nodes1:
            # Encode both text nodes into vectors
            vec2 = encode(text_node2)
            vec1 = encode(text_node1)
            # Calculate cosine similarity between the two vectors
            similarity = cosine_similarity(vec2, vec1)
            # Track the highest similarity found
            if similarity > max_similarity:
                max_similarity = similarity

        # If the highest similarity is below the threshold, highlight the node
        if max_similarity <= similarity_threshold:
            highlight_text_node(text_node2, soup2, "orange")

    # Convert the modified soups back to strings containing the highlighted HTML content
    highlighted_html1 = str(soup1)
    highlighted_html2 = str(soup2)
    return highlighted_html1, highlighted_html2

# API endpoint to compare two HTML documents and return highlighted differences
@app.route('/api/compare', methods=['POST'])
def compare_files():
    data = request.get_json()  # Retrieves JSON data sent with the POST request
    html1 = data.get('html1')  # Extracts HTML content from the received JSON
    html2 = data.get('html2')

    # Check if both HTML contents are provided
    if not html1 or not html2:
        return jsonify({'error': 'Both html1 and html2 are required'}), 400

    # Compare and highlight the differences between the two HTML contents
    highlighted_html1, highlighted_html2 = compare_and_highlight(html1, html2)

    # Return the comparison results as JSON
    return jsonify({
        'highlightedHtml1': highlighted_html1,
        'highlightedHtml2': highlighted_html2
    })

