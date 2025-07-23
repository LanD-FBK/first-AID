import os
from fastapi import HTTPException, status
import math
from tools import chunker, dialogue, retrieval, openai_gpt, span
import json
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ParseError

with open('keys.json') as keys_file:
    keys = json.load(keys_file)

with open('methods_full_dialogue/prompts.json') as keys_file:
    prompts = json.load(keys_file)

def get_complete_generation_options():
    generation_options = [
        {
            "generation_method": "demo",
            "description": "Generates a dialogue with an assistant and a user. Ground text is only provided on Assistant's turns.",
            "roles": [
                {
                    "label": "speaker_1",
                    "name": "User",
                    "ground": False
                },
                {
                    "label": "speaker_2",
                    "name": "Assistant",
                    "ground": True
                }
            ]
        }
    ]
    return generation_options



def generate_dialogue_complete(generation_option, *args, **kwargs):
    try:
        # Get the function object from the global namespace
        func = globals()[generation_option]
        # Call the function with the provided arguments and return the result
        return func(*args, **kwargs)
    except KeyError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Generation option {generation_option} not found.")
        
    except TypeError as e:
        return str(e)

def demo(documents_list, num_turns):
    return(demo_full(documents_list, num_turns, "English"))


def demo_full (documents_list, num_turns, language):
# def demo (documents_list, num_turns):
    language = "English"
    roles = {
        "speaker_1": "User",
        "speaker_2": "Assistant",
        "User": "speaker_1",
        "Assistant": "speaker_2"
        } 
    ground_required_dict =  {
        "speaker_1": False,
        "speaker_2": True
        } 
    if not num_turns:
        num_turns = 6
    

    
    chunks = chunker.Chunker_SaT(
            documents_list  = documents_list, 
            language = language,
            window_size = 1
            )    

    generator = openai_gpt.GenerationModelChat(
        access_token = keys['DEMO_KEY']
        )
 
    retr = retrieval.Retriever_bm25(
        knowledge_base=chunks,
        name="BM25",
        top_k=3
        )
    
    prompt = prompts["DEMO"]
    prompt = prompt.replace("<LANGUAGE>", language)
    prompt = prompt.replace("<TURNS_NUMBER>", str(num_turns))
    prompt = prompt.replace("<SPEAKER_1>", roles["speaker_1"])
    prompt = prompt.replace("<SPEAKER_2>", roles["speaker_2"])
    prompt = "\n\n".join(documents_list) + prompt
    
    question_prompt = []
    sys_prompt = {'role': 'system',
                    'content': prompt}
    question_prompt.append(sys_prompt)
    generated_text = generator.generate_text(question_prompt)
    generated_text = generated_text.replace("```json", "")
    generated_text = generated_text.replace("```", "")
    data = json.loads(generated_text)

    turns_list = []

    for turn in data["dialogue"]:
        turn_dict = dict()
        turn_dict["ground"] =  []
        speaker_id = roles[turn["speaker"]]
        if ground_required_dict[speaker_id]: 
            query = turn["text"]
            grounds = retr.retrieve(query)
            for ground in grounds:
                ground_info = dict()
                index_start, index_end = span.find_indexes(documents_list[ground.metadata["document_id"]],ground.text)
                ground_info["text"] =  ground.text
                ground_info["file_index"] = ground.metadata["document_id"]
                ground_info["offset_start"] = index_start
                ground_info["offset_end"] = index_end
                turn_dict["ground"].append(ground_info)
             
        turn_dict["speaker"] =  speaker_id
        turn_dict["turn_text"] = turn["text"]
        turns_list.append(turn_dict)
    
    return(turns_list)

