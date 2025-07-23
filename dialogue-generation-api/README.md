# API-first-AID

**How to run**

Install requirements:

```
pip install -r requirements
```
Run the api. It is possible to had custom parameters `--host` (default="0.0.0.0") and `--port`(default=8013)

```
python start-api.py
```

# Endpoints
To communicate with the First-AID frontend the API has the following POST endpoints: `/complete_generation` to generate a full dialogue in one go and  `/dynamic_generation` that generates one turn at a time. This API provide an example of interaction with the front-end to show input and output formats. 
The complete generation and dynamic generation are handled by two separate files `dialogue_generators_complete.py` and `dialogue_generators_dynamic.py`.
You can add there you custom functions for dialogue generations

Each generation method need to be also added to `get_complete_generation_options` and `get_dynamic_generation_options` functions to appear in the interface dropdown menu. The list of available generation methods are returned trough GET andpoints `/complete_generation` and `/dynamic_generation`.
  


## Complete Dialogue Generation (/complete_generation)
This endpoint generates a full dialogue in one go.

Input JSON
The client sends a POST request to the /complete_generation endpoint with a JSON body like this. The generation_mode corresponds to a function in dialogue_generators_complete.py, documents is a list of source texts, and num_turns specifies the length of the dialogue.

```json
{
  "generation_mode": "demo",
  "documents": [
    "Full text of the source document 1",
    "Full text of the source document 2",
    "Full text of the source document 3"
  ],
  "num_turns": 4
}
```

Output JSON
The API responds with a JSON array, where each object represents a turn in the generated dialogue. If a turn is based on the provided documents, the ground array will contain the specific text snippet used.

```json
[
    {
        "ground": [],
        "speaker": "speaker_1",
        "turn_text": "Generated text for the first turn by speaker_1"
    },
    {
        "ground": [
            {
                "text": "The specific snippet from the source document that was used as a ground",
                "file_index": 0,
                "offset_start": 81,
                "offset_end": 156
            }
        ],
        "speaker": "speaker_2",
        "turn_text": "Generated response from speaker_2 based on the ground text"
    },
    {
        "ground": [],
        "speaker": "speaker_1",
        "turn_text": "Generated follow-up text from speaker_1"
    },
    {
        "ground": [
            {
                "text": "Another specific snippet from the source document used as a ground",
                "file_index": 0,
                "offset_start": 158,
                "offset_end": 221
            }
        ],
        "speaker": "speaker_2",
        "turn_text": "Another generated response from speaker_2 based on the new ground text"
    }
]
```

## Dynamic Dialogue Generation (/dynamic_generation)
This endpoint generates one turn at a time, allowing for interactive conversations.

Input JSON
The client sends a POST request to /dynamic_generation. This request includes the documents, the dialogue so far, which speaker should generate the next turn, and how many options_number to generate.

```json
{
  "generation_mode": "demol",
  "documents": [
    "Full text of a source document 1",
    "Full text of a source document 2",
    "Full text of a source document 3"
  ],
  "dialogue": [
    {
      "speaker": "speaker_1",
      "turn_text": "Text of the first turn from speaker_1"
    }
  ],
  "speaker": "speaker_2",
  "options_number": 2,
  "manual_selected_grounds": []
}
```

Output JSON
The API responds with a list of possible next turns. Each object is a candidate for the next turn in the dialogue. The ground array shows the source text that justifies the generated response.
```json
[
    {
        "speaker": "speaker_2",
        "turn_text": "First generated option for speaker_2's next turn",
        "ground": [
            {
                "text": "A snippet from the source document justifying the first option",
                "file_index": 0,
                "offset_start": 58,
                "offset_end": 196
            }
        ]
    },
    {
        "speaker": "speaker_2",
        "turn_text": "Second generated option for speaker_2's next turn",
        "ground": [
            {
                "text": "A different snippet from the source document justifying the second option",
                "file_index": 0,
                "offset_start": 718,
                "offset_end": 877
            }
        ]
    }
]
```