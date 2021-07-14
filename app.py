from flask import Flask, jsonify
from flask_cors import CORS, cross_origin
from google.cloud import documentai

app = Flask(__name__)

cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# TODO(developer): Uncomment these variables before running the sample.
@app.route('/',)
@cross_origin()
def quickstart():
    project_id= 'warm-abacus-319311'
    location = 'us' # Format is 'us' or 'eu'
    processor_id = '3b40807604c7068b' #  Create processor in Cloud Console
    file_path = './report1.pdf'
    # You must set the api_endpoint if you use a location other than 'us', e.g.:
    # opts = {}
    # if location == "eu":
    #     opts = {"api_endpoint": "eu-documentai.googleapis.com"}
    client = documentai.DocumentProcessorServiceClient()

    # The full resource name of the processor, e.g.:
    # projects/project-id/locations/location/processor/processor-id
    # You must create new processors in the Cloud Console first
    name = f"projects/{project_id}/locations/{location}/processors/{processor_id}"
    print("name", name)
    # Read the file into memory
    with open(file_path, "rb") as image:
        image_content = image.read()

    document = {"content": image_content, "mime_type": "application/pdf"}

    # Configure the process request
    request = {"name": name, "raw_document": document}
    result = client.process_document(request=request)
    document = result.document

    document_pages = document.pages

    # For a full list of Document object attributes, please reference this page: https://googleapis.dev/python/documentai/latest/_modules/google/cloud/documentai_v1beta3/types/document.html#Document

    # Read the text recognition output from the processor
    print("The document contains the following paragraphs:")
    data = []
    
    for page in document_pages:
        paragraphs = page.paragraphs
        print(paragraphs)
        for paragraph in paragraphs:
            # print(paragraph)
            paragraph_text = get_text(paragraph.layout, document)
            # print(f"Paragraph text: {paragraph_text}")
            data.append(paragraph_text)
    
    return jsonify(data)


def get_text(doc_element: dict, document: dict):
    """
    Document AI identifies form fields by their offsets
    in document text. This function converts offsets
    to text snippets.
    """
    response = ""
    # If a text segment spans several lines, it will
    # be stored in different text segments.
    for segment in doc_element.text_anchor.text_segments:
        start_index = (
            int(segment.start_index)
            if segment in doc_element.text_anchor.text_segments
            else 0
        )
        end_index = int(segment.end_index)
        response += document.text[start_index:end_index]
    return response
