from typing import Dict, List
from .dialogue import Dialogue

class PromptComposer():
    """
    TODO
    """
    def __init__(self, 
                #  prompt: str,
                 dialogue: Dialogue,
                 model: str):
        self.dialogue    = dialogue
        self.model       = model
        self.syst_prompt = None


    def set_system_prompt(self, system_prompt: str) -> None:
        self.syst_prompt = system_prompt


    def get_full_prompt(self, prompt: str = ""):
        """
        TODO
        """
        if prompt == "":
            if self.syst_prompt is None:
                raise ValueError("No prompt has been set!")
            prompt = self.syst_prompt

        if self.model == "OpenAI":
            syst_prompt_dict = {
                'role': 'system',
                'content': self.syst_prompt}

            return [syst_prompt_dict] + self.dialogue.openai_chat

        else:
            raise ValueError("Unexpected model: " + self.model)
