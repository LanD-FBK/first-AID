import os
from tools import chunker, dialogue, retrieval, openai_gpt, span, prompt_composer
import json
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ParseError
from typing import Callable, Dict, List, Union

with open('keys.json') as keys_file:
    keys = json.load(keys_file)

with open('methods_dynamic_dialogue/prompts.json') as keys_file:
    prompts = json.load(keys_file)



def get_dynamic_generation_options():
    generation_options = [
        {
            "generation_method": "demo",
            "description": "Generates a dialogue with an assistant and a user. Ground text is only provided on Assistant's turns",
            "endpoint": "/dialogue_generation_dynamic/",
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


def generate_dialogue_dynamic(generation_opton, *args, **kwargs):
    try:
        # Get the function object from the global namespace
        func = globals()[generation_opton]
        # Call the function with the provided arguments and return the result
        return func(*args, **kwargs)
    except KeyError:
        return f"Generation option {generation_opton} not found."
    except TypeError as e:
        return str(e)


def demo(documents_list, dialogue_list, speaker, options_number, manual_selected_grounds):
    return(demo_dyn(documents_list, dialogue_list, speaker, options_number, manual_selected_grounds, "English"))

def demo_dyn (documents_list, dialogue_list, speaker, options_number, manual_selected_grounds, language):

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
    if not options_number:
        options_number = 1

    chunks = chunker.Chunker_SaT(
            documents_list  = documents_list, 
            language = language,
            window_size = 2
            ) 

    generator = openai_gpt.GenerationModelChat(
        # question_sys_prompt = "question_prompt",
        access_token = keys['DEMO_KEY']
        )
    
    dial= dialogue.Dialogue(turns = dialogue_list)
    

    retr = retrieval.Retriever_bm25(
        knowledge_base=chunks,
        name="BM25",
        top_k=3
        )

    
    
    # QUESTION
    if speaker == "speaker_1":
        question_prompt = []
        if dial.turn_numbers == 0:
            prompt = prompts["DEMO"]["FIRST_QUESTION"]["PROMPT"]
            prompt = prompt.replace("<LANGUAGE>", language)
            prompt = prompt.replace("<OPTIONS_NUMBER>", str(options_number))
            prompt = prompt.replace("<SPEAKER_1>", "Complainer")
            sys_prompt = {'role': 'system',
                            'content': prompt+"\n"+"<article>"+" ".join(documents_list)+"</article>"}
            question_prompt.append(sys_prompt)
        else:
            prompt = prompts["DEMO"]["QUESTION"]["PROMPT"]
            prompt = prompt.replace("<LANGUAGE>", language)
            prompt = prompt.replace("<OPTIONS_NUMBER>", str(options_number))
            prompt = prompt.replace("<SPEAKER_1>", roles["speaker_1"])
            prompt = prompt.replace("<LAST_TURN>", dial.get_last_turn())
            sys_prompt = {'role': 'system',
                        'content': prompt+" "+dial.dialogue_to_string()+"\n"+"<article>"+" ".join(documents_list)+"</article>"}
            question_prompt.append(sys_prompt)

        
    # ANSWER
    if speaker == "speaker_2":
        speaker2_prompt_list = []
        
        if len(manual_selected_grounds) > 0:
            chunks = []

        else:
            query = dial.get_last_turn()
            chunks = retr.retrieve(query)
        
        for ground in chunks:
            answer_prompt = []
            prompt = prompts["DEMO"]["ANSWER"]["FROM_GROUND"]   
            prompt = prompt.replace("<LANGUAGE>", language)
            prompt = prompt.replace("<OPTIONS_NUMBER>", str(options_number))
            prompt = prompt.replace("<SPEAKER_2>", roles["speaker_2"])
            prompt = prompt.replace("<LAST_QUESTION>", dial.get_last_turn())
            if len(manual_selected_grounds) > 0:
                prompt = prompt.replace("<GROUND_TEXT>", ground)
            else:
                prompt = prompt.replace("<GROUND_TEXT>", ground.text.strip())
            sys_prompt = {'role': 'system',
                            'content': prompt}
            answer_prompt.append(sys_prompt)
            speaker2_prompt_list.append(answer_prompt)
    
    # GENERATE
    generation_outputs = []
    if speaker == "speaker_1":    
        generated_text = generator.generate_text(question_prompt)
      
        generated_text = generated_text.replace("```json", "")
        generated_text = generated_text.replace("```", "")
        # print(generated_text)
        try:
            data = json.loads(generated_text)
            for message in data["messages"]:
                generation_outputs.append(message["text"])
        except:
            next_turns_candidates = []
            next_turns_candidates.append(
                {
                    "speaker": speaker,
                    "turn_text": "Unable to generate an answer. Please retry.",
                    "ground": []
                }        
            )
            return next_turns_candidates

    elif speaker == "speaker_2":    
        for p in speaker2_prompt_list:
            generated_text = generator.generate_text(p)
            generated_text = generated_text.replace("```json", "")
            generated_text = generated_text.replace("```", "")
            # print(generated_text)
            try:
                data = json.loads(generated_text)
                generation_outputs.append(data["messages"][0]["text"])
            except:
                next_turns_candidates = []
                next_turns_candidates.append(
                    {
                        "speaker": speaker,
                        "turn_text": "Unable to generate an answer. Please retry.",
                        "ground": []
                    }        
                )
                return next_turns_candidates



    next_turns_candidates = []
    
    for candidate_index, text_option in enumerate(generation_outputs):
        grounds_list = []
        if ground_required_dict[speaker]:
            if len(manual_selected_grounds) == 0:
                ground_info = dict()
                g_text =   chunks[candidate_index].text
                g_doc = chunks[candidate_index].metadata["document_id"]
                index_start, index_end = span.find_indexes(documents_list[g_doc],g_text)
                ground_info["text"] = g_text
                ground_info["file_index"] = g_doc
                ground_info["offset_start"] = index_start
                ground_info["offset_end"] = index_end
                grounds_list.append(ground_info)
            
            
        next_turns_candidates.append(
            
            {
                "speaker": speaker,
                "turn_text": text_option,
                "ground": grounds_list

                
            }        
        )


    return next_turns_candidates
    
