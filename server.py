# Importing flask module in the project is mandatory
# An object of Flask class is our WSGI application.

import os
import elasticsearch
import json
import ipdb
from config import config

from flask import Flask
from flask_cors import CORS, cross_origin
from flask import jsonify, request
from flask import Response


from langchain import ElasticVectorSearch
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import ChatVectorDBChain
from langchain.llms import OpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter, TokenTextSplitter

import base64
import io
from PyPDF2 import PdfReader

app = Flask(__name__)
cors = CORS(app)

es = None
embedding = None
db = None
model_qa = None

chat_memory = {}


def start_connection():
	global es
	global embedding
	global db
	global model_qa

	es = elasticsearch.Elasticsearch(
		hosts = config['host'],
		basic_auth = (config['auth'][0]['username'], config['auth'][0]['password'])
	)
	# es.add_texts()
	os.environ["OPENAI_API_KEY"] = config["Open-AI Key"]
	embedding = OpenAIEmbeddings()

	db = ElasticVectorSearch(elasticsearch_url=f"{config['auth'][0]['username']}:{config['auth'][0]['password']}@{config['host']}", index_name="search_vector", embedding=embedding)
	# db



def return_response(query, index):
	db.index_name = index
	if index not in chat_memory:
		chat_memory[index] = []

	# ipdb.set_trace()

	model_qa = ChatVectorDBChain.from_llm(OpenAI(temperature=0, model_name="gpt-3.5-turbo"), db, return_source_documents=True)
	result = model_qa({"question": query, "chat_history": chat_memory[index]})

	chat_memory[index].append((query, result['answer']))
	

	response = {
		"answer" : result['answer'],
		"source_documents" : [
			{
				"content" : result['source_documents'][i].page_content,
				"metadata" : result['source_documents'][i].metadata
			}

			for i in range(len(result['source_documents']))	
		]
	}
	print(response)

	return response

def upload_docs(text, index, file_name):
	global embedding
	global db

	text.replace('\n', '')
	text.replace('\t', '')

	token_doc = RecursiveCharacterTextSplitter(chunk_size=1000).split_text(text)

	# ipdb.set_trace()
	db.index_name = index
	db.add_texts(texts = token_doc, embedding = embedding, index_name = index, metadatas=[{"name" : file_name, "type" : index.split('_')}]*len(token_doc))
	

@app.route('/addFiles', methods = ['POST'])
@cross_origin()
def add_files():
	try:
		file_list = json.loads(request.data)
		file = json.loads(file_list['data'])['file']

		buffer=base64.b64decode(file)
		f=io.BytesIO(buffer)
		reader = PdfReader(f)

		content = ''

		for page in range(len(reader.pages)):
			content += reader.pages[page].extract_text()

		# ipdb.set_trace()
		upload_docs(content, file_list['index'], file_list['name'])

	except Exception as e:
		print(e)
		return Response(status=404, mimetype='application/json')


	# print(request)
	# ipdb.set_trace()
	return Response(status=201, mimetype='application/json')

@app.route('/eraseIndex', methods = ['POST'])
@cross_origin()
def erase_index():
	# print(request)
	req = (json.loads(request.data)['name'])
	checkIndexExists = (es.indices.exists(index = req))

	# ipdb.set_trace()

	if(checkIndexExists.body == True):
		resp = es.indices.delete_alias(index = req, name = "romTalk")
		return {'status_code' : 200, 'message' : resp.body['acknowledged']}
	else:
		print("doesnt exists")
		return ({'status_code' : 404, "message" : "Index doesn't exist"})


@app.route('/get_indices')
@cross_origin()
def get_indices():
	if(es is None):
		jsonify({'errorCode' : 404, 'message' : 'Route not found'}) 
	return [{"name" : index} for index in list(es.indices.get_alias(name = config["application_name"]).keys())]

@app.route('/add_index')
@cross_origin()
def add_index():
	req = (request.args.to_dict())
	print(req.get("name"))
	
	checkIndexExists = (es.indices.exists(index = req['name']))
	if(checkIndexExists.body == True):
		res_alias = es.indices.put_alias(index = req["name"], name = "romTalk")
		if(res_alias['acknowledged']):
			return res_alias.raw
		return res_alias.raw

	res_insert = es.indices.create(index = req["name"], mappings = config['mapping'])

	if(res_insert['acknowledged']):
		res_alias = es.indices.put_alias(index = req["name"], name = "romTalk")
		if(res_alias['acknowledged']):
			return res_alias.raw
		return res_alias.raw
	return res_insert.raw

@app.route('/createResponse')
@cross_origin()
def create_response():
	req = (request.args.to_dict())
	print(req['question'])

	return return_response(req['question'], req['index'])

@app.route('/')
@cross_origin()
def hello_world():
	return 'Hello World'


if __name__ == '__main__':
	start_connection()
	app.run()
