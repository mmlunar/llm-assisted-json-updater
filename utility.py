import tiktoken
import json
from typing import Optional
import os

class Utility:
    """
    A singleton utility class responsible for managing configuration settings,
    token counting, and other helper functions needed across the application.
    """
    # Singleton instance reference    
    _instance = None

    def __new__(cls, config_file: str = './solution/python/config.json') -> 'Utility':
        """
        Ensures a single instance of the Utility class is created.

        Args:
            config_file (str): Path to the configuration file. Defaults to './solution/python/config.json'.
        
        Returns:
            Utility: The singleton instance of the Utility class.
        """        
        if cls._instance is None:
            cls._instance = super(Utility, cls).__new__(cls)
            cls._instance.config_file = config_file
            cls._instance.config_data = cls._instance.load_config()
        return cls._instance

    def load_config(self) -> dict:
        """
        Loads configuration data from the provided config file.

        Returns:
            dict: The loaded configuration data.
        """        
        try:
            with open(self.config_file, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            print(f"Config file '{self.config_file}' not found.")
            return {}
        except json.JSONDecodeError:
            print(f"Error decoding JSON from the config file '{self.config_file}'.")
            return {}

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Retrieves a configuration value for the given key.

        Args:
            key (str): The configuration key to look up.
            default (Optional[str]): The default value to return if the key is not found. Defaults to None.

        Returns:
            Optional[str]: The configuration value associated with the key, or the default value if not found.
        """        
        return self.config_data.get(key, default)

    def set(self, key: str, value: str) -> None:
        """
        Sets a configuration value for the given key and saves it to the config file.

        Args:
            key (str): The configuration key to update.
            value (str): The new value to assign to the key.
        """
        self.config_data[key] = value
        self.save_config()

    def save_config(self) -> None:
        """
        Saves the current configuration data to the config file.
        """        
        try:
            with open(self.config_file, 'w') as file:
                json.dump(self.config_data, file, indent=4)
        except IOError:
            print(f"Error saving to config file '{self.config_file}'.")

    def get_api_key(self) -> Optional[str]:
        """
        Retrieves the API key from the configuration.

        Returns:
            Optional[str]: The API key if it exists in the configuration, or None.
        """        
        return self.get("CANDIDATE_API_KEY")

    def get_max_token(self) -> Optional[int]:
        """
        Retrieves the maximum token count that we are allowing for the input from the configuration.

        Returns:
            Optional[int]: The maximum token count if it exists, or None.
        """    
        return self.get("max_token", default=None)

    def get_model_name(self) -> Optional[str]:
        """
        Retrieves the model name from the configuration.

        Returns:
            Optional[str]: The model name if it exists, or None.
        """        
        return self.get("model_name")

    def get_dummy_placeholder(self) -> Optional[str]:
        """
        Retrieves the dummy placeholder as a key/value for json objects text from the configuration.

        Returns:
            Optional[str]: The dummy placeholder if it exists, or None.
        """        
        return self.get("dummy_placeholder")
    
    def get_delimiter(self) -> Optional[str]:
        """
        Retrieves the default delimiter used in the configuration.

        Returns:
            Optional[str]: The delimiter if it exists, or None.
        """        
        return self.get("delimiter")
    
    def get_batch_file_path(self) -> Optional[str]:
        """
        Retrieves the path to the batch file from the configuration.

        Returns:
            Optional[str]: The batch file path if it exists, or None.
        """        
        return self.get("batch_file_path")
    
    def get_additional_instructions(self) -> Optional[str]:
        """
        Retrieves any additional instructions that should be appended to the input, 
        combining 'only_json_instruction' and 'no_change_case'.

        Returns:
            Optional[str]: The additional instructions as a string, or None.
        """        
        return self.get("only_json_instruction") + "\n" + self.get("no_change_case")
    
    def get_check_text(self) -> Optional[str]:
        """
        Retrieves the check text to use for validation from the configuration.

        Returns:
            Optional[str]: The check text if it exists, or None.
        """        
        return self.get("check_text")
    
    def num_tokens_from_string(self, input_string: str, model_name: str) -> int:
        """
        Returns the number of tokens in a given input string based on the model's encoding.

        Args:
            input_string (str): The string whose tokens are to be counted.
            model_name (str): The model name to determine the appropriate encoding.

        Returns:
            int: The number of tokens in the string.
        """
        encoding = tiktoken.encoding_for_model(model_name)
        num_tokens = len(encoding.encode(input_string))
        return num_tokens
    
    def write_file(self, file_path:  str, data: str) -> None:
        """
        Writes data to a specified file.

        Args:
            file_path (str): The path to the file where data should be written.
            data (str): The data to write to the file.
        """        
        with open(file_path, "w") as file:
            file.write(data)