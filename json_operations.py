import json
from typing import Union, Any, Dict, List
from utility import Utility
from string_builder import StringBuilder
import re
from enum import Enum

# Enum for distinguishing between JSON types (List or Dict)
class JsonType(Enum):
    LIST = 1
    DICT = 2

class JsonOperations:
    """
    A utility class that handles operations related to JSON data, such as 
    traversing, updating, recovering, and formatting JSON structures. It also 
    supports working with nested structures and ensures that the data adheres 
    to specific token limits set by the utility class.
    """    
    def __init__(self, data: Union[List, Dict]):
        """
        Initializes the JsonOperations instance with the provided JSON data.

        Args:
            data (Union[List, Dict]): The input data, which can be either a list or dictionary.
        """        
        self.data = data
        self.utility = Utility()
        self.json_list_dict = {}
        self.string_builder = StringBuilder(delimiter=self.utility.get_delimiter())
        self.max_token = self.utility.get_max_token()
        self.model_name = self.utility.get_model_name()
        self.json_type = JsonType.DICT if isinstance(self.data, dict) else JsonType.LIST
        if self.json_type is JsonType.LIST:
            self.data = {self.utility.get_dummy_placeholder() : self.data}

    def json_traverse(self, json_obj):  
        """
        Recursively traverses the JSON object to identify lists that exceed 
        the maximum token limit and store them in the `json_list_dict` with 
        their key chain.

        Args:
            json_obj (dict or list): The JSON object (either a dictionary or list) to traverse.

        Returns:
            Dict: A dictionary containing key chains and lists that exceed token limits.
        """             
        if isinstance(json_obj, dict):
            for key, value in json_obj.items():
                self.string_builder.add(key)
                self.json_traverse(value)
                self.string_builder.pop()
        elif isinstance(json_obj, list):
            serialized_json = json.dumps(json_obj, ensure_ascii=False)
            if self.utility.num_tokens_from_string(serialized_json, self.model_name) > self.max_token:
                key_chain = self.string_builder.get()
                self.json_list_dict[key_chain] = json_obj
                JsonOperations.update_value(key_chain, self.utility.get_dummy_placeholder(), self.data)
        return self.json_list_dict
    
    @staticmethod
    def update_value(key_chain: str, new_value: Any, base: Dict) -> None:
        """
        Updates a value in the base dictionary using a key chain (e.g., '/key1/key2').

        Args:
            key_chain (str): A string representing the key path to update.
            new_value (Any): The new value to set at the key chain.
            base (Dict): The base dictionary in which the value will be updated.
        """        
        keys = key_chain.split('/')  
        d = base
        for key in keys[:-1]:
            d = d.get(key, {})
        d[keys[-1]] = new_value    
    
    @staticmethod
    def json_recover(data: Dict) -> Dict:
        """
        Recovers the original JSON structure by replacing placeholders with actual lists.

        Args:
            data (Dict): A dictionary containing key chains and lists that were serialized.

        Returns:
            Dict: The recovered JSON object with lists properly inserted.
        """        
        base = json.loads(data["/"][0])
        data.pop("/")
        for key_chain in data.keys():
            updated_list = []
            n = len(data[key_chain])
            for index in range(n):
                updated_list.append(data[key_chain][index])
            base[key_chain] = updated_list
            JsonOperations.update_value(key_chain, updated_list, base)
        json_object = JsonOperations.to_json_object_formatted(base)
        return json_object
    
    @staticmethod
    def to_json_object_formatted(input_dict: Dict) -> Dict:
        """
        Converts the input dictionary into a properly formatted JSON object, 
        cleaning up escape sequences and extra spaces.

        Args:
            input_dict (Dict): The dictionary to be converted into a formatted JSON object.

        Returns:
            Dict: A formatted JSON object.
        """        
        json_string = JsonOperations.to_json_string(input_dict, None).replace("\\n", "").replace("\\\"", "\"").replace("\u00e2\u20ac\u201d", "–")
        cleaned_string = re.sub(r'\s+', ' ', json_string).strip()
        s = re.sub(r'"{(.*?)}"', r'{\1}', cleaned_string)
        json_object = json.loads(s)
        utility = Utility()
        return json_object if utility.get_dummy_placeholder() not in json_object else json_object[utility.get_dummy_placeholder()]
    
    @staticmethod
    def to_json_string(input_dict: Dict, indent: int = 4) -> str:
        """
        Converts a dictionary to a JSON string with optional indentation.

        Args:
            input_dict (Dict): The dictionary to be converted into a JSON string.
            indent (int): The number of spaces to use for indentation. Defaults to 4.

        Returns:
            str: The JSON string representation of the input dictionary.
        """        
        return json.dumps(input_dict, indent=indent, ensure_ascii=False)   