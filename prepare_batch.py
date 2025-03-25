from typing import Union, Optional, List, Tuple
from json_operations import JsonOperations
from utility import Utility
from string_builder import StringBuilder

class PrepareBatch:
    """
    A class to prepare batch messages and input lists for API calls. It handles 
    the generation of batch messages, manages data traversal, and formats 
    requests for use with a machine learning model. This class operates 
    on JSON-like data structures (list or dictionary) and supports message 
    preparation and saving to a file.
    """    
    def __init__(self, data: Union[list, dict], instructions: str = ""):
        """
        Initializes the PrepareBatch instance with the provided data and instructions.

        Args:
            data (Union[list, dict]): The data to be processed into batch messages.
            instructions (str): Additional instructions to be included in the batch messages.
        """        
        self.json_operations = JsonOperations(data)
        self.data = self.json_operations.data
        self.utility = Utility()
        self.instructions = instructions
        self.model_name = self.utility.get_model_name()

    def create_batch_message(self, system_content: str, user_content: str, custom_id: str)-> Optional[str]:
        """
        Creates a single batch message in the required format for the API request.

        Args:
            system_content (str): The system's message content (often instructions or metadata).
            user_content (str): The user's message content (input data).
            custom_id (str): A custom identifier for the batch message.

        Returns:
            Optional[str]: The batch message as a JSON string, or None if invalid.
        """
        # Prepare the system and user messages        
        system_message = {
            "role": "system",
            "content": system_content
        }

        user_message = {
            "role": "user",
            "content": user_content
        }

        num_tokens = self.utility.num_tokens_from_string(system_content, self.model_name)

        # Define the request body with model and messages
        request_body = {
            "model": self.model_name,
            "messages": [system_message, user_message],
            "max_tokens": num_tokens*3
        }

        # Create the final message dictionary with custom_id, method, and url
        message_dict = {
            "custom_id": custom_id,
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": request_body
        }
        
        return JsonOperations.to_json_string(message_dict, indent=None)
    
    def batch_lists(self):
        """
        Prepares a batch of messages for the entire data set, including the root data 
        and its nested elements, formatted as per API request standards.

        Returns:
            str: A string containing the full batch of messages, ready for sending.
        """        
        list_dic = self.json_operations.json_traverse(self.data)
        string_builder = StringBuilder(delimiter="\n")
        main_input = self.create_batch_message(JsonOperations.to_json_string(self.data), self.instructions, "/")
        string_builder.add(main_input)

        for custom_id, list_data in list_dic.items():
            i = 0
            for d in list_data:
                current_message = self.create_batch_message(JsonOperations.to_json_string(d), 
                                                            self.instructions,
                                                            custom_id + "/" + str(i))
                string_builder.add(current_message)
                i += 1

        string_builder.add("")
        return string_builder.get()
    
    def write_batch_to_file(self):
        """
        Writes the generated batch of messages to a file as a string.
        The file path is retrieved from the utility class.

        This method ensures that all generated messages are saved to disk for further use.
        """        
        batch_string = self.batch_lists()
        file_path = self.utility.get_batch_file_path()
        self.utility.write_file(file_path, batch_string)

    def prepare_tuple_for_input_list(self, data: dict, full_key_sequence: str, index: int) -> Tuple:
        """
        Prepares a tuple of information to be added to the input list, which contains 
        the system content, token count, and other metadata.

        Args:
            data (dict): The data (usually a dictionary) to be processed.
            full_key_sequence (str): The key sequence representing the full path to the data.
            index (int): The index of the current item in the list.

        Returns:
            Tuple: A tuple containing (full_key_sequence, index, system_content, num_tokens).
        """        
        system_content = JsonOperations.to_json_string(data)
        num_tokens = self.utility.num_tokens_from_string(system_content, self.model_name)
        return (full_key_sequence, index, system_content, num_tokens*3)

    def create_input_list(self) -> List:
        """
        Creates a list of tuples containing the necessary information for processing 
        each batch of data. This list will be used by the system to process 
        each item individually.

        Returns:
            List: A list of tuples ready for further processing in batch jobs.
        """        
        list_dic = self.json_operations.json_traverse(self.data)
        input_list = [self.prepare_tuple_for_input_list(self.data, "/", 0)]

        for key_sequence, list_data in list_dic.items():
            for index, current_data in enumerate(list_data):
                input_list.append(self.prepare_tuple_for_input_list(current_data, key_sequence, index))
        return input_list