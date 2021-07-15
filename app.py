from flask import Flask, jsonify,json
from flask_cors import CORS, cross_origin
from google.cloud import documentai, documentai_v1beta2 as documentai2
import os
import re


app = Flask(__name__)

cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

credential_path = "./warm-abacus-319311-0dbe727044df.json"
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path

# TODO(developer): Uncomment these variables before running the sample.
@app.route('/ocr',methods = ['GET'])
@cross_origin()
def quickstart():
    project_id= 'warm-abacus-319311'
    location = 'us' # Format is 'us' or 'eu'
    processor_id = '3b40807604c7068b' #  Create processor in Cloud Console
    input_uri = "gs://khatta-pani-pdf/report2.pdf"
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

    #table parser

    # For a full list of Document object attributes, please reference this page: https://googleapis.dev/python/documentai/latest/_modules/google/cloud/documentai_v1beta3/types/document.html#Document

    # Read the text recognition output from the processor
    print("The document contains the following paragraphs:")
    data = []

    for page in document_pages:
        
        paragraphs = page.paragraphs
        #print(paragraphs)
        for paragraph in paragraphs:
            print(paragraph)
            paragraph_text = get_text(paragraph.layout, document)
            #datas["paragraph"].append(paragraph_text)
            #print(f"Paragraph text: {paragraph_text}")
            #temp = {"paragraph text" : paragraph_text}
            data.append(paragraph_text)
        #page_count += 1; 
        #data.append(datas)
    return jsonify(data)
    
@app.route('/ocr2',methods = ['GET'])
@cross_origin()
def quickstart2():
    project_id= 'warm-abacus-319311'
    location = 'us' # Format is 'us' or 'eu'
    processor_id = '3b40807604c7068b' #  Create processor in Cloud Console
    file_path ='./report1.pdf'
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

    #table parser

    # For a full list of Document object attributes, please reference this page: https://googleapis.dev/python/documentai/latest/_modules/google/cloud/documentai_v1beta3/types/document.html#Document

    # Read the text recognition output from the processor
    print("The document contains the following paragraphs:")
    data = []

    for page in document_pages:
        
        paragraphs = page.paragraphs
        #print(paragraphs)
        for paragraph in paragraphs:
            print(paragraph)
            paragraph_text = get_text(paragraph.layout, document)
            #datas["paragraph"].append(paragraph_text)
            #print(f"Paragraph text: {paragraph_text}")
            #temp = {"paragraph text" : paragraph_text}
            data.append(paragraph_text)
        #page_count += 1; 
        #data.append(datas)
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


@app.route('/formfields', methods=['GET'])
def form_fields():
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
    formdata = []   # all data , form parse , table parse

    for page in document_pages:
        print("Page Number:{}".format(page.page_number))
        for form_field in page.form_fields:
            fieldName=get_text(form_field.field_name,document)
            nameConfidence = round(form_field.field_name.confidence,4)
            fieldValue = get_text(form_field.field_value,document)
            valueConfidence = round(form_field.field_value.confidence,4)
            print(fieldName+fieldValue +"  (Confidence Scores: "+str(nameConfidence)+", "+str(valueConfidence)+")")
            formdata.append({fieldName:fieldValue})
    return jsonify(formdata)







@app.route('/parsetable-extended', methods=['GET'])
def parse_table_extended(
    project_id='warm-abacus-319311',
    input_uri="gs://khatta-pani-pdf/report2.pdf"
):
    """Parse a form"""

    client = documentai2.DocumentUnderstandingServiceClient()

    gcs_source = documentai2.types.GcsSource(uri=input_uri)

    # mime_type can be application/pdf, image/tiff,
    # and image/gif, or application/json
    input_config = documentai2.types.InputConfig(
        gcs_source=gcs_source, mime_type="application/pdf"
    )

    # Improve table parsing results by providing bounding boxes
    # specifying where the box appears in the document (optional)
    table_bound_hints = [
        documentai2.types.TableBoundHint(
            page_number=1,
            bounding_box=documentai2.types.BoundingPoly(
                # Define a polygon around tables to detect
                # Each vertice coordinate must be a number between 0 and 1
                normalized_vertices=[
                    # Top left
                    documentai2.types.geometry.NormalizedVertex(x=0, y=0),
                    # Top right
                    documentai2.types.geometry.NormalizedVertex(x=1, y=0),
                    # Bottom right
                    documentai2.types.geometry.NormalizedVertex(x=1, y=1),
                    # Bottom left
                    documentai2.types.geometry.NormalizedVertex(x=0, y=1),
                ]
            ),
        )
    ]

    # Setting enabled=True enables form extraction
    table_extraction_params = documentai2.types.TableExtractionParams(
        enabled=True, table_bound_hints=table_bound_hints
    )

    # Location can be 'us' or 'eu'
    parent = "projects/{}/locations/us".format(project_id)
    request = documentai2.types.ProcessDocumentRequest(
        parent=parent,
        input_config=input_config,
        table_extraction_params=table_extraction_params,
    )

    document = client.process_document(request=request)

    def _get_text(el):
        """Convert text offset indexes into text snippets."""
        response = ""
        # If a text segment spans several lines, it will
        # be stored in different text segments.
        for segment in el.text_anchor.text_segments:
            start_index = segment.start_index
            end_index = segment.end_index
            response += document.text[start_index:end_index]
        return response

    data = []
        

    for page in document.pages:
        print("Page number: {}".format(page.page_number))
        for table_num, table in enumerate(page.tables):
            temp= {"tableNumber": table_num, "header":[], "body":[]}
            print("Table {}: ".format(table_num))
            for row_num, row in enumerate(table.header_rows):
                cells = "\t".join([_get_text(cell.layout) for cell in row.cells])
                print("Header Row {}: {}".format(row_num, cells))
                temp["header"].append({"rowNumber":row_num, "rowData":cells})
                # temp["header"]["rowNumber"] = row_num
                # temp["header"]["rowData"] = cells
            for row_num, row in enumerate(table.body_rows):
                cells = "\t".join([_get_text(cell.layout) for cell in row.cells])
                print("Row {}: {}".format(row_num, cells))
                # temp["body"]["rowNumber"] = row_num
                # temp["body"]["rowData"] = cells
                # {"rowNumber":"", "rowData":""}
                # {"rowNumber":"", "rowData":""}
                temp["body"].append({"rowNumber":row_num, "rowData":cells})
        data.append(temp)

    return jsonify(data)



@app.route('/parsetable', methods=['GET'])
def parse_table(
    project_id='warm-abacus-319311',
    input_uri="gs://khatta-pani-pdf/report2.pdf"
):
    """Parse a form"""

    client = documentai2.DocumentUnderstandingServiceClient()

    gcs_source = documentai2.types.GcsSource(uri=input_uri)

    # mime_type can be application/pdf, image/tiff,
    # and image/gif, or application/json
    input_config = documentai2.types.InputConfig(
        gcs_source=gcs_source, mime_type="application/pdf"
    )

    # Improve table parsing results by providing bounding boxes
    # specifying where the box appears in the document (optional)
    table_bound_hints = [
        documentai2.types.TableBoundHint(
            page_number=1,
            bounding_box=documentai2.types.BoundingPoly(
                # Define a polygon around tables to detect
                # Each vertice coordinate must be a number between 0 and 1
                normalized_vertices=[
                    # Top left
                    documentai2.types.geometry.NormalizedVertex(x=0, y=0),
                    # Top right
                    documentai2.types.geometry.NormalizedVertex(x=1, y=0),
                    # Bottom right
                    documentai2.types.geometry.NormalizedVertex(x=1, y=1),
                    # Bottom left
                    documentai2.types.geometry.NormalizedVertex(x=0, y=1),
                ]
            ),
        )
    ]

    # Setting enabled=True enables form extraction
    table_extraction_params = documentai2.types.TableExtractionParams(
        enabled=True, table_bound_hints=table_bound_hints
    )

    # Location can be 'us' or 'eu'
    parent = "projects/{}/locations/us".format(project_id)
    request = documentai2.types.ProcessDocumentRequest(
        parent=parent,
        input_config=input_config,
        table_extraction_params=table_extraction_params,
    )

    document = client.process_document(request=request)

    def _get_text(el):
        """Convert text offset indexes into text snippets."""
        response = ""
        # If a text segment spans several lines, it will
        # be stored in different text segments.
        for segment in el.text_anchor.text_segments:
            start_index = segment.start_index
            end_index = segment.end_index
            response += document.text[start_index:end_index]
        return response

    def _get_cell_data(el):
        response = []
        for cell in el:
            response.append(_get_text(cell.layout))
        return response


    data = []
        

    for page in document.pages:
        print("Page number: {}".format(page.page_number))
        for table_num, table in enumerate(page.tables):
            temp= {"tableNumber": table_num, "header":[], "body":[]}
            print("Table {}: ".format(table_num))
            for row_num, row in enumerate(table.header_rows):
                #cells = "\t".join([_get_text(cell.layout) for cell in row.cells])
                print(row.cells)
                for cell in row.cells:
                    #print("Header Row {}: {}".format(row_num, cell))
                    temp["header"].append(_get_text(cell.layout))
                    # temp["header"]["rowNumber"] = row_num
                    # temp["header"]["rowData"] = cells
            for row_num, row in enumerate(table.body_rows):
                    #cells = "\t".join([_get_text(cell.layout) for cell in row.cells])
                
                    #print("Row {}: {}".format(row_num, cell))
                    # temp["body"]["rowNumber"] = row_num
                    # temp["body"]["rowData"] = cells
                    # {"rowNumber":"", "rowData":""}
                    # {"rowNumber":"", "rowData":""}
                    # headerlength = len(temp["header"])
                    # bodylength = len(temp["body"])
                    # tempdata = []
                    # tempdata.append(_get_text(cell.layout))
                temp["body"].append(_get_cell_data(row.cells))
                   
        data.append(temp)

    return jsonify(data)

    