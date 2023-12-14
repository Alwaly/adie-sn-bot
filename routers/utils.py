from databases.database import documents
import os
import shutil
import re
from qdrant_client.http.models import PointStruct, Distance, VectorParams
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from llama_index.llms import ChatMessage, MessageRole
from llama_index.prompts import ChatPromptTemplate
import openai
from llama_index import VectorStoreIndex, SimpleDirectoryReader, ServiceContext
from llama_index.llms import OpenAI

chat_text_qa_msgs = [
    ChatMessage(
        role=MessageRole.SYSTEM,
        content=(
            "Tu es une Assistante de question réponse ton nom est Anta. Réponds toujours aux question en rapport avec l'ADIE, même si te context n'est pas util. Fais sentir que tu fais parti de l'ADIE, notes que l'ADIE s'appelle désormais Sénégal Numérique S.A"
        ),
    ),
    ChatMessage(
        role=MessageRole.USER,
        content=(
            "Context information is below.\n"
            "---------------------\n"
            "{context_str}\n"
            "---------------------\n"
            "Given the context information and not prior knowledge, "
            "answer the question: {query_str}\n"
        ),
    ),
]
text_qa_template = ChatPromptTemplate(chat_text_qa_msgs)

#pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

documents = documents()


openai.api_key = ""

service_context = ServiceContext.from_defaults(
    llm=OpenAI(model="gpt-3.5-turbo", temperature=0.1)
)


def chatter(question, context_):
  f = open("data/data.txt", "w")
  f.write(context_)
  f.close()
  documents = SimpleDirectoryReader("data").load_data()
  index = VectorStoreIndex.from_documents(
    documents, service_context=service_context
  )
  return str(index.as_query_engine(text_qa_template=text_qa_template).query(question))

def file_saver(file):
    upload_dir = os.path.join(os.getcwd(), "uploads")
    # Create the upload directory if it doesn't exist
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    # get the destination path
    dest = os.path.join(upload_dir, file.filename)

    # copy the file contents
    with open(dest, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return dest

def rep(input_string):
  return re.sub(r"[^a-zA-Z0-9\séêèà-ô]", " ", input_string)

def cleaner(texte):
    return rep(texte.lower()).replace("\n\n"," ").replace("\n"," ").replace("   "," ").replace("  "," ").replace("\t","")
    
def loader(file_name):
    with open(file_name, "r", encoding="utf-8") as f:
        text = f.read()
    data = cleaner(text).split(' ')
    datas = []
    k=0
    x = len(data)%100
    y = int(len(data)/100)
    if len(data)<=100:
        datas.append(" ".join(data))
    else:
        for i in range(100,len(data),100):
            if i == 100*y:
                datas.append(" ".join(data[k:i+x]))
            else:
                datas.append(" ".join(data[k:i]))
            k = i-10
    return datas

os.environ['CURL_CA_BUNDLE'] = ''
model_name = "all-MiniLM-L6-v2"
model  = SentenceTransformer(model_name)
client = QdrantClient(host="localhost", port=6333)
size = 500


def padd_vector(vect):
  padding_length = size - len(vect)
  vect = vect.tolist()
  vect.extend([0.0] * padding_length)
  
  return list(vect) 

def collection_maker(collection_name):
    client.recreate_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size = size, distance=Distance.DOT),
    )



def make_embedding(sentences):
    result = model.encode(sentences)
    return padd_vector(result)


def inserter(collection_name, text, id):
    payload = f"{id}"
    payload={"Id":payload}
    tex = text
    operation_info = client.upsert(
        collection_name=collection_name,
        wait=True,
        points=[
            PointStruct(id = id, vector=tex, payload=payload)
        ]
    )
    


def finder(text, collection_name):
    vector = make_embedding(text)
    search_result = client.search(
        collection_name= collection_name,
        query_vector=vector, 
        limit=10
    )
    return [dict(search_result[0])['id'], dict(search_result[1])['id'], dict(search_result[2])['id'], dict(search_result[3])['id'], dict(search_result[4])['id'], dict(search_result[5])['id'], dict(search_result[6])['id'], dict(search_result[7])['id'], dict(search_result[8])['id'], dict(search_result[9])['id']]
     

async def searcher(text, collection_name):
    ids = finder(text, collection_name)
    results = ""
    for id in ids:
        result = await documents.find_one({"fict_id":id})
        results = f"{results} {result['value']}"
    return results
