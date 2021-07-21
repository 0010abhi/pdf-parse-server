from flask import Flask, jsonify,json
from flask_cors import CORS, cross_origin
from google.cloud import documentai, documentai_v1beta2 as documentai2, documentai_v1beta3 as documentai3
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
    """
        This function Returns all text in document.

    """
    project_id= 'warm-abacus-319311'
    location = 'us' # Format is 'us' or 'eu'
    processor_id = 'ce5a599cbf3d5513' #  Create processor in Cloud Console
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
    """
        This function returns all form fields in the document. 
    """
    project_id= 'warm-abacus-319311'
    location = 'us' # Format is 'us' or 'eu'
    processor_id = 'ce5a599cbf3d5513' #  Create processor in Cloud Console
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
    data = []
    for page in document_pages:
        print("Page Number:{}".format(page.page_number))
        for form_field in page.form_fields:
            fieldName=get_text(form_field.field_name,document)
            nameConfidence = round(form_field.field_name.confidence,4)
            fieldValue = get_text(form_field.field_value,document)
            valueConfidence = round(form_field.field_value.confidence,4)
            print(fieldName+fieldValue +"  (Confidence Scores: "+str(nameConfidence)+", "+str(valueConfidence)+")")
            temp = {"fieldName":fieldName, "nameCondidence":nameConfidence,
                    "fieldValue":fieldValue, "valueConfidence":valueConfidence}
            data.append(temp)
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

"""
*************************************************************************************
    Below is API for 2nd pdf. 
*************************************************************************************
"""

# 2nd parse table
@app.route('/parsetable2', methods=['GET'])
def parse_table2(
    project_id="warm-abacus-319311",
    #input_uri="gs://pdf-parser-4fb89.appspot.com/report2.pdf",
    input_uri = "gs://khatta-pani-pdf/report1.pdf",
    
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
                vertices=[
                    documentai2.types.geometry.Vertex(x=0, y=0),
                    documentai2.types.geometry.Vertex(x=0, y=1896),
                    documentai2.types.geometry.Vertex(x=1896, y=1896),
                    documentai2.types.geometry.Vertex(x=1896, y=0)
                    
                ],
                # Define a polygon around tables to detect
                # Each vertice coordinate must be a number between 0 and 1
                # normalized_vertices=[
                #     # Top left
                #     documentai2.types.geometry.NormalizedVertex(x=0, y=0),
                #     # Top right
                #     documentai2.types.geometry.NormalizedVertex(x=1, y=0),
                #     # Bottom right
                #     documentai2.types.geometry.NormalizedVertex(x=1, y=1),
                #     # Bottom left
                #     documentai2.types.geometry.NormalizedVertex(x=0, y=1),
                # ]
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
    entities = document.entities

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
    
    def _get_vertex_text(el):
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

    def _get_vertex_cell_data(el):
        response = []
        for cell in el:
            response.append(_get_vertex_text(cell.layout))
        return response

    data = []
    #print("document text", document.text)
    for page in document.pages:
        #print("Page number: {}".format(page.page_number)) 
        #print("Bounding box: {}".format(page.bounding_box)) 
        # if page_number==2
        #print("page", page)
        #print("table*********", page.tables)
        if page.page_number==2:
            lines = (_get_text(page.layout))
            print(page.layout)
            temp = {"pageNumber":page.page_number, "data":[]}
            for table_num, table in enumerate(page.tables):
                #print("Table {}: ".format(table))
                temp2= {"tableNumber":table_num, "header":[], "body":[]}
                
                for row_num, row in enumerate(table.header_rows):
                    
                    for cell in row.cells:
                        temp2["header"].append(_get_text(cell.layout))
                    #cells = "\t".join([_get_text(cell.layout) for cell in row.cells])
                    #print("Header Row {}: {}".format(row_num, cells))
                    #temp["header"].append({"rowNum":row_num, "cellData":_get_cell_data(cells)})
                for row_num, row in enumerate(table.body_rows):
                    temp2["body"].append(_get_cell_data(row.cells))
                        
                    # cells = "\t".join([_get_text(cell.layout) for cell in row.cells])
                    # print("Row {}: {}".format(row_num, cells))
                    # temp["body"].append({"rowNum":row_num, "cellData":_get_cell_data(cells)})
                temp["data"].append(temp2)
            data.append(temp)
            # t = []
            # for entity in entities:
            #     entity_type = entity.type_
            #     value = entity.mention_text
            #     confience = round(entity.confidence,4)
            #     t.append({"entityType":entity_type,"entityValue": value,"entityConfidence": confience
            #     })


    # Grab each key/value pair and their corresponding confidence scores.

    
    #print(lines)
            
    return jsonify({"data":data, "lines":lines})




