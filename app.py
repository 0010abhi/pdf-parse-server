from datetime import datetime
from flask import Flask, jsonify,json, request
from flask_cors import CORS, cross_origin
from google.cloud import storage, documentai, documentai_v1beta2 as documentai2, documentai_v1beta3 as documentai3
import os
import re
import base64
import uuid
import datetime

"""
MAKE FILE NAME UNIQUE UUID, HOW TO SEE PUBLIC URL , don't make multi-array. """


app = Flask(__name__)

cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
credential_path = "./warm-abacus-319311-0dbe727044df.json"
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path
bucket_name = 'khatta-pani-pdf'

# @app.route('/parse-pdf', methods=['POST'])
# @cross_origin()
# def parse_pdf():
#     try:
#         file_gs_url = request.json["gcsUrl"]
#         file_type = request.json["fileType"]
#         if not file_gs_url or not file_type:
#             return jsonify({"result":"Either gsUrl or fileType is wrong."})
#         if file_type==1:
#             parser_type_one(input_uri = file_gs_url)
#         if file_type==2:
#             parser_type_two(input_uri=file_gs_url)
#         return jsonify({"result":""})
#     except Exception as e:
#         print("parse-pdf Exception error", e)
#         return jsonify({"result":"error"})


@app.route('/upload/<path_param>', methods=['POST'])
@cross_origin()
def upload(path_param):
    """Process the uploaded file and upload it to Google Cloud Storage."""
    try:
        uploaded_file = request.files.get('report_file')
        #print("uploaded file", uploaded_file.filename, " ", uploaded_file.content_type)
    
        # (a, b, c) = uploaded_file
        # print("a", a, "b", b)
        if not uploaded_file:
            return jsonify({"error":"No file uploaded."})

        # Create a Cloud Storage client.
        gcs = storage.Client()

        # Get the bucket that the file will be uploaded to.
        bucket = gcs.get_bucket(bucket_name)

        # Create a new blob and upload the file's content.
        file_uuid = str(uuid.uuid4())
        uploaded_file.filename = file_uuid+".pdf"
        blob = bucket.blob(uploaded_file.filename)
        #print(uploaded_file.filename)
        blob.upload_from_string(
            uploaded_file.read(),
            content_type=uploaded_file.content_type
        )
        #print('bucket', blob.bucket.name, 'name', blob.name)

        public_url = blob.public_url
        gs_url = "gs://"+blob.bucket.name+"/"+blob.name
        file_type = path_param
        created_at = datetime.datetime.now()
        result = {"fileId":file_uuid , "publicUrl":public_url, "gcsUrl":str(gs_url), "fileType":file_type, "createdAt":created_at, "updatedAt":""}

        # The public URL can be used to directly access the uploaded file via HTTP.
        return jsonify(result)
    except Exception as e:
        print("File Upload Excetion error", e)
        return jsonify({"result": "error"})

@app.route('/file_list', methods=['GET'])
@cross_origin()
def file_list():
    """
        This Function return all Files Names which are present in Bucket. 

    """
    try:
        storage_client = storage.Client()

        # Note: Client.list_blobs requires at least package version 1.17.0.
        blobs = storage_client.list_blobs(bucket_name)
        files_in_bucket = []
        for blob in blobs:
            files_in_bucket.append(blob.name)

        return jsonify({"Bucket List":files_in_bucket})
    except Exception as e:
        print("File List Exception error", e)
        return jsonify({"result":"error"})

# TODO(developer): Uncomment these variables before running the sample.
# @app.route('/ocr',methods = ['GET'])
# @cross_origin()
# def quickstart():
#     """
#         This function Returns all text in document.

#     """
#     try:
#         project_id= 'warm-abacus-319311'
#         location = 'us' # Format is 'us' or 'eu'
#         processor_id = 'ce5a599cbf3d5513' #  Create processor in Cloud Console
#         file_path ='./report1.pdf'
#         # You must set the api_endpoint if you use a location other than 'us', e.g.:
#         # opts = {}
#         # if location == "eu":
#         #     opts = {"api_endpoint": "eu-documentai.googleapis.com"}
#         client = documentai.DocumentProcessorServiceClient()

#         # The full resource name of the processor, e.g.:
#         # projects/project-id/locations/location/processor/processor-id
#         # You must create new processors in the Cloud Console first
#         name = f"projects/{project_id}/locations/{location}/processors/{processor_id}"
#         print("name", name)
#         # Read the file into memory
#         with open(file_path, "rb") as image:
#             image_content = image.read()

#         document = {"content": image_content, "mime_type": "application/pdf"}

#         # Configure the process request
#         request = {"name": name, "raw_document": document}
#         result = client.process_document(request=request)
#         document = result.document

#         document_pages = document.pages

#         #table parser

#         # For a full list of Document object attributes, please reference this page: https://googleapis.dev/python/documentai/latest/_modules/google/cloud/documentai_v1beta3/types/document.html#Document

#         # Read the text recognition output from the processor
#         print("The document contains the following paragraphs:")
#         data = []

#         for page in document_pages:
            
#             paragraphs = page.paragraphs
#             #print(paragraphs)
#             for paragraph in paragraphs:
#                 print(paragraph)
#                 paragraph_text = get_text(paragraph.layout, document)
#                 #datas["paragraph"].append(paragraph_text)
#                 #print(f"Paragraph text: {paragraph_text}")
#                 #temp = {"paragraph text" : paragraph_text}
#                 data.append(paragraph_text)
#             #page_count += 1; 
#             #data.append(datas)
#         return jsonify(data)
#     except Exception as e:
#         print("OCR Exception error", e)
#         return jsonify({"result":"error"})

# def get_text(doc_element: dict, document: dict):
#     """
#     Document AI identifies form fields by their offsets
#     in document text. This function converts offsets
#     to text snippets.
#     """
#     response = ""
#     # If a text segment spans several lines, it will
#     # be stored in different text segments.
#     for segment in doc_element.text_anchor.text_segments:
#         start_index = (
#             int(segment.start_index)
#             if segment in doc_element.text_anchor.text_segments
#             else 0
#         )
#         end_index = int(segment.end_index)
#         response += document.text[start_index:end_index]
#     return response


# @app.route('/formfields', methods=['GET'])
# @cross_origin()
# def form_fields():
#     """
#         This function returns all form fields in the document. 
#     """
#     try:
#         project_id= 'warm-abacus-319311'
#         location = 'us' # Format is 'us' or 'eu'
#         processor_id = 'ce5a599cbf3d5513' #  Create processor in Cloud Console
#         file_path = './report1.pdf'
#         # You must set the api_endpoint if you use a location other than 'us', e.g.:
#         # opts = {}
#         # if location == "eu":
#         #     opts = {"api_endpoint": "eu-documentai.googleapis.com"}
#         client = documentai.DocumentProcessorServiceClient()

#         # The full resource name of the processor, e.g.:
#         # projects/project-id/locations/location/processor/processor-id
#         # You must create new processors in the Cloud Console first
#         name = f"projects/{project_id}/locations/{location}/processors/{processor_id}"
#         print("name", name)
#         # Read the file into memory
#         with open(file_path, "rb") as image:
#             image_content = image.read()

#         document = {"content": image_content, "mime_type": "application/pdf"}

#         # Configure the process request
#         request = {"name": name, "raw_document": document}
#         result = client.process_document(request=request)
#         document = result.document

#         document_pages = document.pages
#         data = []
#         for page in document_pages:
#             print("Page Number:{}".format(page.page_number))
#             for form_field in page.form_fields:
#                 fieldName=get_text(form_field.field_name,document)
#                 nameConfidence = round(form_field.field_name.confidence,4)
#                 fieldValue = get_text(form_field.field_value,document)
#                 valueConfidence = round(form_field.field_value.confidence,4)
#                 print(fieldName+fieldValue +"  (Confidence Scores: "+str(nameConfidence)+", "+str(valueConfidence)+")")
#                 temp = {"fieldName":fieldName, "nameCondidence":nameConfidence,
#                         "fieldValue":fieldValue, "valueConfidence":valueConfidence}
#                 data.append(temp)
#         return jsonify(data)
#     except Exception as e:
#         print("Form Fields Exception error", e)
#         return jsonify({"result":"error"})

# def get_text(doc_element: dict, document: dict):
#     """
#     Document AI identifies form fields by their offsets
#     in document text. This function converts offsets
#     to text snippets.
#     """
#     response = ""
#     # If a text segment spans several lines, it will
#     # be stored in different text segments.
#     for segment in doc_element.text_anchor.text_segments:
#         start_index = (
#             int(segment.start_index)
#             if segment in doc_element.text_anchor.text_segments
#             else 0
#         )
#         end_index = int(segment.end_index)
#         response += document.text[start_index:end_index]
#     return response


@app.route('/parser-type-one', methods=['POST'])
@cross_origin()
def parser_type_one(
    project_id='warm-abacus-319311',
    #input_uri="gs://khatta-pani-pdf/report2.pdf"
    #input_uri = "gs://pdf-parser-4fb89.appspot.com/file_110.pdf"
    input_uri = ""
    #input_uri = request.headers.get('file_url')
):
    """Parse a form"""
    try:
        client = documentai2.DocumentUnderstandingServiceClient()
        input_uri = request.json["gcsUrl"]
        if not input_uri or len(input_uri)==0:
            return jsonify({"error":"Please provide gs url. "})
        gcs_source = documentai2.types.GcsSource(uri=input_uri)

        # mime_type can be application/pdf, image/tiff,
        # and image/gif, or application/json
        #contents = request.json['contents']


        #contents = request.json['contents']
        #sample_string_bytes = sample_string.encode()
    
        #base64_bytes = base64.b64encode(sample_string_bytes) 
        #print("bse64: ", base64_bytes)   

        input_config = documentai2.types.InputConfig(
            gcs_source=gcs_source, 
            mime_type="application/pdf"#, contents= contents
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
        _request = documentai2.types.ProcessDocumentRequest(
            parent=parent,
            input_config=input_config,
            table_extraction_params=table_extraction_params,
        )

        document = client.process_document(request=_request)

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
        #return_data = []

        for page in document.pages:
            #print("Page number: {}".format(page.page_number))
            page_data = {"pageNumber":page.page_number, "data":[]}
            if page.page_number==2:
                for table_num, table in enumerate(page.tables):
                    temp= {"tableNumber": table_num, "header":[], "body":[]}
                    temp_header_list = []
                    temp_body_list = []
                    #print("Table {}: ".format(table_num))
                    for row_num, row in enumerate(table.header_rows):
                        cells = "\t".join([_get_text(cell.layout) for cell in row.cells])
                        #print("Header Row {}: {}".format(row_num, cells))
                        #print("before")
                        temp_header_list.append({"rowNumber":row_num, "rowData":cells})
                        header_list = temp_header_list[0]["rowData"].split("\t")
                        #print(header_list)
                        for header_name in header_list:
                            header_data = {"title":header_name.replace("\n", "").strip() , "key": header_name.lower().replace(" ", "").replace("\n", "").replace("($)", "").strip()}
                        # temp["header"]["rowNumber"] = row_num
                        # # temp["header"]["rowData"] = cells
                        #     temp["header"].append(header_data)
                            temp["header"].append(header_data)
                    for row_num, row in enumerate(table.body_rows):
                        cells = "\t".join([_get_text(cell.layout) for cell in row.cells])
                        #print("Row {}: {}".format(row_num, cells))
                        # temp["body"]["rowNumber"] = row_num
                        # temp["body"]["rowData"] = cells
                        # {"rowNumber":"", "rowData":""}
                        # {"rowNumber":"", "rowData":""}

                        temp_body_list.append({"rowNumber":row_num, "rowData":cells})
                        body_list = []
                        body_list_obj_list = []
                        for i in range(len(temp_body_list)):
                            body_list = temp_body_list[i]["rowData"].split("\t")
                            body_list_obj = {}
                            for j in range(len(body_list)):
                                body_list_obj[temp["header"][j]["key"]] = body_list[j].replace("\n", "")
                        
                        
                        temp["body"].append(body_list_obj)
                        # temp_body_list.append({"rowNumber":row_num, "rowData":cells})

                        # body_list = temp_body_list[row_num]["rowData"].split("\t")
                        # #print(header_list)
                        # for body_name in body_list:
                        #     body_data = {temp["header"][i]:body_name , "key": body_name.lower().replace(" ", "").replace("\n", "").replace("($)", "").strip()}
                        # # temp["header"]["rowNumber"] = row_num
                        # # # temp["header"]["rowData"] = cells
                        # #     temp["header"].append(header_data)
                        #     temp["body"].append(body_data)

                        #print(temp["header"]["rowData"][row_num].split("\n"))
                page_data["data"].append(temp)
                data.append(page_data)
        return jsonify(data)
    except Exception as e:
        print("Parse-type-one Exception error : ", e)
        return jsonify({"result":str(e)})



# @app.route('/parsetable', methods=['GET'])
# @cross_origin()
# def parse_table(
#     project_id='warm-abacus-319311',
#     input_uri=""
# ):
#     """Parse a form"""
#     try:
#         client = documentai2.DocumentUnderstandingServiceClient()
#         input_uri = request.json["myFileUrl"]
#         if not input_uri or len(input_uri)==0:
#             return jsonify({"error":"Please provide gs url. "})
#         gcs_source = documentai2.types.GcsSource(uri=input_uri)

#         # mime_type can be application/pdf, image/tiff,
#         # and image/gif, or application/json
#         input_config = documentai2.types.InputConfig(
#             gcs_source=gcs_source, mime_type="application/pdf"
#         )

#         # Improve table parsing results by providing bounding boxes
#         # specifying where the box appears in the document (optional)
#         table_bound_hints = [
#             documentai2.types.TableBoundHint(
#                 page_number=1,
#                 bounding_box=documentai2.types.BoundingPoly(
#                     # Define a polygon around tables to detect
#                     # Each vertice coordinate must be a number between 0 and 1
#                     normalized_vertices=[
#                         # Top left
#                         documentai2.types.geometry.NormalizedVertex(x=0, y=0),
#                         # Top right
#                         documentai2.types.geometry.NormalizedVertex(x=1, y=0),
#                         # Bottom right
#                         documentai2.types.geometry.NormalizedVertex(x=1, y=1),
#                         # Bottom left
#                         documentai2.types.geometry.NormalizedVertex(x=0, y=1),
#                     ]
#                 ),
#             )
#         ]

#         # Setting enabled=True enables form extraction
#         table_extraction_params = documentai2.types.TableExtractionParams(
#             enabled=True, table_bound_hints=table_bound_hints
#         )

#         # Location can be 'us' or 'eu'
#         parent = "projects/{}/locations/us".format(project_id)
#         _request = documentai2.types.ProcessDocumentRequest(
#             parent=parent,
#             input_config=input_config,
#             table_extraction_params=table_extraction_params,
#         )

#         document = client.process_document(request=_request)

#         def _get_text(el):
#             """Convert text offset indexes into text snippets."""
#             response = ""
#             # If a text segment spans several lines, it will
#             # be stored in different text segments.
#             for segment in el.text_anchor.text_segments:
#                 start_index = segment.start_index
#                 end_index = segment.end_index
#                 response += document.text[start_index:end_index]
#             return response

#         def _get_cell_data(el):
#             response = []
#             for cell in el:
#                 response.append(_get_text(cell.layout))
#             return response

#         data = []
        
#         for page in document.pages:
#             print("Page number: {}".format(page.page_number))
#             for table_num, table in enumerate(page.tables):
#                 temp= {"tableNumber": table_num, "header":[], "body":[]}
#                 print("Table {}: ".format(table_num))
#                 for row_num, row in enumerate(table.header_rows):
#                     #cells = "\t".join([_get_text(cell.layout) for cell in row.cells])
#                     print(row.cells)
#                     for cell in row.cells:
#                         #print("Header Row {}: {}".format(row_num, cell))
#                         temp["header"].append(_get_text(cell.layout))
#                         # temp["header"]["rowNumber"] = row_num
#                         # temp["header"]["rowData"] = cells
#                 for row_num, row in enumerate(table.body_rows):
#                         #cells = "\t".join([_get_text(cell.layout) for cell in row.cells])
                    
#                         #print("Row {}: {}".format(row_num, cell))
#                         # temp["body"]["rowNumber"] = row_num
#                         # temp["body"]["rowData"] = cells
#                         # {"rowNumber":"", "rowData":""}
#                         # {"rowNumber":"", "rowData":""}
#                         # headerlength = len(temp["header"])
#                         # bodylength = len(temp["body"])
#                         # tempdata = []
#                         # tempdata.append(_get_text(cell.layout))
#                     temp["body"].append(_get_cell_data(row.cells))
                    
#             data.append(temp)

#         return jsonify(data)
#     except Exception as e:
#         print("ParseTable Exception error", e)
#         jsonify({"result":"error"})

"""
*************************************************************************************
    Below is API for 2nd pdf. 
*************************************************************************************
"""

# 2nd parse table
@app.route('/parser-type-two-extended', methods=['POST'])
@cross_origin()
def parser_type_two_extended(
    project_id="warm-abacus-319311",
    #input_uri="gs://pdf-parser-4fb89.appspot.com/report2.pdf",
    input_uri = "",
    
):
    """Parse a form"""
    try:
        client = documentai2.DocumentUnderstandingServiceClient()
        input_uri = request.json["gcsUrl"]
        if not input_uri or len(input_uri)==0:
            return jsonify({"error":"Please provide gs url. "})
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
        _request = documentai2.types.ProcessDocumentRequest(
            parent=parent,
            input_config=input_config,
            table_extraction_params=table_extraction_params,
        )

        document = client.process_document(request=_request)
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

        def _get_cell_data(el):
            response = []
            for cell in el:
                response.append(_get_text(cell.layout))
            return response

        def _get_text_from_sorted_arr_tables(start_index, end_index):
            """Convert text offset indexes into text snippets."""
            response = []
            # If a text segment spans several lines, it will
            # be stored in different text segments.
            response.append(document.text[start_index:end_index])
            return response

        def _get_data_from_page_start_to_table_start(page_layout, table_layout):
            #arr = []
            arr_page = []
            arr_tables = []
            for segment in page_layout.text_anchor.text_segments:
                start_index = segment.start_index
                end_index = segment.end_index
                if(start_index not in arr_page):
                    arr_page.append(start_index)
                if(end_index not in arr_page):
                    arr_page.append(end_index)
            #print("Page arguments", arr_page)
            for segment in table_layout.text_anchor.text_segments:
                start_index = segment.start_index
                end_index = segment.end_index
                arr_tables.append([start_index, end_index])
            sorted_arr_tables = sorted(arr_tables, key=lambda x: x[1])
            #print("Table arguments", sorted_arr_tables)



            resultant_arr = []
            page_first_table = [arr_page[0], arr_tables[0][0]]
            page_last_table = [arr_tables[len(arr_tables)-1][1], arr_page[1]]
            resultant_arr.append(page_first_table)
            for i in range(1, len(sorted_arr_tables)):
                resultant_arr.append([sorted_arr_tables[i-1][1], sorted_arr_tables[i][0]])
                # add start index of page
            resultant_arr.append(page_last_table)
            #print("resultant array is : ", resultant_arr)

            #for i in resultant_arr:
            #print("gettext_resultant",_get_text_from_sorted_arr_tables(i[0], i[1]))
            
            return resultant_arr
        # take all lines above, between and below the table
        # take{ page_start_index to 1st_table_s_i, 1st_table_end_ind to 2nd_table_start_ind, ..}

        data = []
        arr_data = []
        data_except_tables = []
        #print("document text", document.text)
        for page in document.pages:
            #print("Page number: {}".format(page.page_number)) 
            #print("Bounding box: {}".format(page.bounding_box)) 
            # if page_number==2
            #print("page", page)
            #print("table*********", page.tables)
            if page.page_number==2:
                #lines = (_get_text(page.layout))
                temp = {"pageNumber":page.page_number, "data":[]}
                #print("Page ", page.page_number, " : " , page.tables)
                for table_num, table in enumerate(page.tables):
                    arr_data = _get_data_from_page_start_to_table_start(page.layout,table.layout )
                    #print("Table {}: ".format(table))
                    #print("page", page.layout.text_anchor.text_segments)
                    #print("table", table.layout.text_anchor.text_segments)
                    temp2= {"tableNumber":table_num, "header":[], "body":[]}
                    
                    header_list = []
                    for row_num, row in enumerate(table.header_rows):
                        for cell in row.cells:
                            temp2["header"].append(_get_text(cell.layout))
                        #     header_list.append(_get_text(cell.layout))
                        # obj = {}
                        # for item in header_list:
                        #     print("item", item)
                        #     obj["title"] = item
                        #     obj["key"] = item.lower().replace(" ", "").replace("\n", "").replace("($)", "").strip()
                        #     temp2["header"].append(json.dumps(obj))
                        #print(row_num , " " , header_list)
                        # obj = {}
                        # for item in temp2["header"]:
                        #     obj["title"] = item
                        #     obj["key"] = item.lower().replace(" ", "").replace("\n", "").replace("($)", "").strip()
                        #     temp2["header"].append(obj)
                            #print(item , " ", type(item))
                            #header_list.append(_get_text(cell.layout))
                            # header_list_obj = {}
                            # for item in header_list:
                            #     header_list_obj["title"] = item
                            #     header_list_obj["key"] = item.lower().replace(" ", "").replace("\n", "").replace("($)", "").strip()
                            # temp2["header"].append(header_list_obj)
                            # print("before")
                            # print("header" , header_list)
                        
                            # print("after")
                        # obj  ={}
                        # for i in range(len(header_list)):
                        #     #obj = {"title":item, "key":item.lower().replace(" ", "").replace("\n", "").replace("($)", "").strip()}
                        #     obj["title"] = header_list[i]
                        #     obj["key"] = header_list[i].lower().replace(" ", "").replace("\n", "").replace("($)", "").strip()
                        #     temp2["header"].append(obj)
                        #cells = "\t".join([_get_text(cell.layout) for cell in row.cells])
                        #print("Header Row {}: {}".format(row_num, cells))
                        #temp["header"].append({"rowNum":row_num, "cellData":_get_cell_data(cells)})
                    #temp_body_list_obj = []
                    for row_num, row in enumerate(table.body_rows):
                        #temp2["body"].append(_get_cell_data(row.cells))
                        temp_list = _get_cell_data(row.cells)
                        body_list_obj = {}
                        for i in range(len(temp2)):
                            body_list_obj[temp2["header"][i]] = temp_list[i]

                        temp2["body"].append(body_list_obj)
                    #print("body", temp2["body"])
                        # cells = "\t".join([_get_text(cell.layout) for cell in row.cells])
                        # print("Row {}: {}".format(row_num, cells))
                        # temp["body"].append({"rowNum":row_num, "cellData":_get_cell_data(cells)})
                    temp["data"].append(temp2)
                    for i in arr_data:
                        data_except_tables.append(_get_text_from_sorted_arr_tables(i[0], i[1]))
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
                
        return jsonify({"data":data, "dataExceptFromTable":data_except_tables, "dataExceptFromTableArray":arr_data, "pageStartEndIndex":[arr_data[0][0], arr_data[len(arr_data)-1][1]]})
    except Exception as e:
        print("ParseTable2 Exception error : ", e)
        return jsonify({"resutl":str(e)})



@app.route('/parser-type-two', methods=['POST'])
@cross_origin()
def parser_type_two(
    project_id="warm-abacus-319311",
    #input_uri="gs://pdf-parser-4fb89.appspot.com/report2.pdf",
    input_uri = "",
    
):
    """Parse a form"""
    try:
        client = documentai2.DocumentUnderstandingServiceClient()
        input_uri = request.json["gcsUrl"]
        if not input_uri or len(input_uri)==0:
            return jsonify({"error":"Please provide gs url. "})
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
        _request = documentai2.types.ProcessDocumentRequest(
            parent=parent,
            input_config=input_config,
            table_extraction_params=table_extraction_params,
        )

        document = client.process_document(request=_request)
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

        def _get_cell_data(el):
            response = []
            for cell in el:
                response.append(_get_text(cell.layout))
            return response

        def _get_text_from_sorted_arr_tables(start_index, end_index):
            """Convert text offset indexes into text snippets."""
            response = []
            # If a text segment spans several lines, it will
            # be stored in different text segments.
            response.append(document.text[start_index:end_index])
            return response

        def _get_data_from_page_start_to_table_start(page_layout, table_layout):
            #arr = []
            arr_page = []
            arr_tables = []
            for segment in page_layout.text_anchor.text_segments:
                start_index = segment.start_index
                end_index = segment.end_index
                if(start_index not in arr_page):
                    arr_page.append(start_index)
                if(end_index not in arr_page):
                    arr_page.append(end_index)
            #print("Page arguments", arr_page)
            for segment in table_layout.text_anchor.text_segments:
                start_index = segment.start_index
                end_index = segment.end_index
                arr_tables.append([start_index, end_index])
            sorted_arr_tables = sorted(arr_tables, key=lambda x: x[1])
            #print("Table arguments", sorted_arr_tables)



            resultant_arr = []
            page_first_table = [arr_page[0], arr_tables[0][0]]
            page_last_table = [arr_tables[len(arr_tables)-1][1], arr_page[1]]
            resultant_arr.append(page_first_table)
            for i in range(1, len(sorted_arr_tables)):
                resultant_arr.append([sorted_arr_tables[i-1][1], sorted_arr_tables[i][0]])
                # add start index of page
            resultant_arr.append(page_last_table)
            #print("resultant array is : ", resultant_arr)

            #for i in resultant_arr:
            #print("gettext_resultant",_get_text_from_sorted_arr_tables(i[0], i[1]))
            
            return resultant_arr
        # take all lines above, between and below the table
        # take{ page_start_index to 1st_table_s_i, 1st_table_end_ind to 2nd_table_start_ind, ..}

        #data = []
        arr_data = []
        data_except_tables = []
        temp_return  = []
        #print("document text", document.text)
        for page in document.pages:
            temp ={"pageNumber":page.page_number, "data" :[]}
            #print("Page number: {}".format(page.page_number)) 
            #print("Bounding box: {}".format(page.bounding_box)) 
            # if page_number==2
            #print("page", page)
            #print("table*********", page.tables)
            #temp["pageNumber"] = page.page_number
            if page.page_number==2:
                #lines = (_get_text(page.layout))
                #temp = {"pageNumber":page.page_number, "data":[]}
                #print("Page ", page.page_number, " : " , page.tables)
                for table_num, table in enumerate(page.tables):
                    arr_data = _get_data_from_page_start_to_table_start(page.layout,table.layout )
                    #print("Table {}: ".format(table))
                    #print("page", page.layout.text_anchor.text_segments)
                    #print("table", table.layout.text_anchor.text_segments)
                    temp2= {"tableNumber":table_num, "header":[], "body":[]}
                    #temp[page.page_number] = {}
                    header_list = []
                    for row_num, row in enumerate(table.header_rows):
                        for cell in row.cells:
                            #temp2["header"].append(_get_text(cell.layout))
                            header_list.append(_get_text(cell.layout))
                        #obj = {}
                        for i in range(len(header_list)):
                            header_list[i] = header_list[i].replace("\n", "").strip()
                            title = header_list[i]
                            key = header_list[i].lower().replace(" ", "").replace("\n", "").replace("($)", "").strip()
                            temp2["header"].append({"title":title, "key":key})
                        #     header_list.append(_get_text(cell.layout))
                        # obj = {}
                        # for item in header_list:
                        #     print("item", item)
                        #     obj["title"] = item
                        #     obj["key"] = item.lower().replace(" ", "").replace("\n", "").replace("($)", "").strip()
                        #     temp2["header"].append(json.dumps(obj))
                        #print(row_num , " " , header_list)
                        # obj = {}
                        # for item in temp2["header"]:
                        #     obj["title"] = item
                        #     obj["key"] = item.lower().replace(" ", "").replace("\n", "").replace("($)", "").strip()
                        #     temp2["header"].append(obj)
                            #print(item , " ", type(item))
                            #header_list.append(_get_text(cell.layout))
                            # header_list_obj = {}
                            # for item in header_list:
                            #     header_list_obj["title"] = item
                            #     header_list_obj["key"] = item.lower().replace(" ", "").replace("\n", "").replace("($)", "").strip()
                            # temp2["header"].append(header_list_obj)
                            # print("before")
                            # print("header" , header_list)
                        
                            # print("after")
                        # obj  ={}
                        # for i in range(len(header_list)):
                        #     #obj = {"title":item, "key":item.lower().replace(" ", "").replace("\n", "").replace("($)", "").strip()}
                        #     obj["title"] = header_list[i]
                        #     obj["key"] = header_list[i].lower().replace(" ", "").replace("\n", "").replace("($)", "").strip()
                        #     temp2["header"].append(obj)
                        #cells = "\t".join([_get_text(cell.layout) for cell in row.cells])
                        #print("Header Row {}: {}".format(row_num, cells))
                        #temp["header"].append({"rowNum":row_num, "cellData":_get_cell_data(cells)})
                    #temp_body_list_obj = []
                    for row_num, row in enumerate(table.body_rows):
                        #temp2["body"].append(_get_cell_data(row.cells))
                        temp_list = _get_cell_data(row.cells)
                        body_list_obj = {}
                        for i in range(len(temp2)):
                            body_list_obj[temp2["header"][i]["key"]] = temp_list[i].replace("\n","")

                        temp2["body"].append(body_list_obj)
                    #print("body", temp2["body"])
                        # cells = "\t".join([_get_text(cell.layout) for cell in row.cells])
                        # print("Row {}: {}".format(row_num, cells))
                        # temp["body"].append({"rowNum":row_num, "cellData":_get_cell_data(cells)})
                    temp["data"].append(temp2)
                    #print(temp)
                    for i in arr_data:
                        data_except_tables.append(_get_text_from_sorted_arr_tables(i[0], i[1]))
                temp_return.append(temp)
                #temp["data"].append(temp2)
                # t = []
                # for entity in entities:
                #     entity_type = entity.type_
                #     value = entity.mention_text
                #     confience = round(entity.confidence,4)
                #     t.append({"entityType":entity_type,"entityValue": value,"entityConfidence": confience
                #     })


        # Grab each key/value pair and their corresponding confidence scores.

        
        #print(lines)
                
        #return jsonify(data)
        return jsonify(temp_return)
    except Exception as e:
        print("ParseTable2 Exception error : ", e)
        return jsonify({"Error : ":str(e)})

