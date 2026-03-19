import json



class Dialogue:
     def __init__(self, 
               turns = []):
        self.turns = turns
        self.turn_numbers = len(self.turns)
        self.dialogue_string= self.dialogue_to_string()
        self.openai_chat = self.get_openai_chat_format()

     def dialogue_to_string(self):
          dialogue_string = ""
          for turn in self.turns:
               dialogue_string = dialogue_string + turn["speaker"] + ": " + turn["turn_text"] + "\n"
          return(dialogue_string)
          
     def get_last_turn(self):
          try:
               return(self.turns[-1]["turn_text"])
          except:
               return("")
     def get_last_speaker(self):
          try:
               return(self.turns[-1]["speaker"])
          except:
               return("")
          
     def get_openai_chat_format(self):
          openai_chat = []

          if len(self.turns)> 0:
               for turn in self.turns:
                    
                    turn_dict = dict()

                    if turn["speaker"] == "speaker_1":
                         turn_dict["role"] = "user" 
                         turn_dict["content"] = turn["turn_text"]
                         openai_chat.append(turn_dict)

                    if turn["speaker"] == "speaker_2":
                         turn_dict["role"] = "assistant" 
                         turn_dict["content"] = turn["turn_text"]
                         openai_chat.append(turn_dict)          

          return(openai_chat)

     def __len__(self):
          return len(self.turns)
