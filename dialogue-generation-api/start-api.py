from fastapi import FastAPI, HTTPException, Depends
import uvicorn
import os
from dialogue_generators_complete import get_complete_generation_options, generate_dialogue_complete
from dialogue_generators_dynamic import get_dynamic_generation_options, generate_dialogue_dynamic
# from auth import app as auth_app, get_current_active_user, User
import time
import argparse
import json 
from typing import List, Optional, Dict
from pydantic import BaseModel

from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

parser = argparse.ArgumentParser()
parser.add_argument('--host', default="0.0.0.0")
parser.add_argument('--port', default=8013, type=int)
args = parser.parse_args()

# instantiate FastApi application
app = FastAPI(version="0.0.1")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=['access-control-allow-origin'],
)

# add authentication
# app.mount("/auth", auth_app)

# add endpoint status
# create_status_endpoint(app)

# create our home page route
@app.get('/')
async def version():
    return {"version": app.version}


class CompleteDialogueGenerationRequest(BaseModel):
    generation_mode: str
    documents: List[str]
    num_turns: Optional[int] = None
    # ground_required: Dict[str, bool]



class DynamicDialogueGenerationRequest(BaseModel):
    generation_mode: str
    documents: List[str]
    dialogue: List[dict]
    speaker: str
    options_number: int
    manual_selected_grounds: List[str]
    # ground_required: bool
    


# API METHODS

@app.get('/complete_generation')
def get_complete_list():
    start_time = time.time()  
    print(start_time, "Request complete generation options")
    return JSONResponse(content=get_complete_generation_options())
    # return json.dumps(get_complete_generation_options())



@app.post('/complete_generation')
def dialogue_generation_complete(request: CompleteDialogueGenerationRequest):
    start_time = time.time()      
    print(start_time, "Request dialogue generation")
    documents_list = request.documents
    # ground_required_dict = request.ground_required
    # return JSONResponse(content=get_complete_generation_options())
    return generate_dialogue_complete(request.generation_mode, documents_list, request.num_turns)


@app.get('/dynamic_generation')
def get_complete_list():
    start_time = time.time()  
    print(start_time, "Request complete generation options")
    return JSONResponse(content=get_dynamic_generation_options())
    # return json.dumps(get_dynamic_generation_options())



@app.post('/dynamic_generation')
def dialogue_generation_dynamic(request: DynamicDialogueGenerationRequest):
    start_time = time.time()
    print(start_time, "Request dialogue generation")
    documents_list = request.documents
    dialogue_list = request.dialogue
    grounds_list = request.manual_selected_grounds
    # return generate_dialogue_dynamic(request.generation_mode, documents_list, dialogue_list, request.speaker, request.options_number, request.ground_required)
    return generate_dialogue_dynamic(request.generation_mode, documents_list, dialogue_list, request.speaker, request.options_number, grounds_list)

if __name__ == '__main__':

    uvicorn.run("start-api:app", host=args.host, port=args.port)
