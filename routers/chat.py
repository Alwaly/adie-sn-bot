from fastapi import APIRouter, UploadFile, HTTPException
from databases.models.auth import *
from schemas import Response
from .utils import documents, collection_maker, file_saver, loader, inserter, make_embedding, chatter, searcher
import uuid
import os

from spire.doc import *
from spire.doc.common import *

router = APIRouter(
    prefix="/chat",
    tags=['Chats'],
    responses={200: {"description": "This is for exchages with the chatbot"}},
)

@router.post("/add_machine_discussion",response_model=Response)
async def add_discussion(discussion: Message):   
    collection = "senegal_numerique_bot"

    context = await searcher(discussion.content, collection)
    
    chat_response = chatter(discussion.content, context)
    return Response(status=200, message=chat_response)


@router.post("/add_documents",response_model=Response)
async def create_document(files: list[UploadFile]):
    i = 0
    textes = []
    for file in files:
        name = file_saver(file)
        content = loader(name)
        if content == None:
            os.remove(name)
            raise HTTPException(status_code=400, detail="Invalid file type")

        textes.extend(content)
        if os.path.exists(name):
            os.remove(name)
        i = i+1
    

    for text in textes:
        id = str(uuid.uuid1())
        elt= dict({
            "fict_id": id,
            "value": text
        })
        inserted = documents.insert_one(elt)
        try:
            inserter("senegal_numerique_bot", make_embedding(text), id)
        except:
            collection_maker("senegal_numerique_bot")
            inserter("senegal_numerique_bot", make_embedding(text), id)

    return Response(status=200, message="document added successfully")
