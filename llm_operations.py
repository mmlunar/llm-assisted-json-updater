import openai
import os
from prepare_batch import PrepareBatch
from utility import Utility
from typing import Union, List, Dict
import asyncio
from json_operations import JsonOperations
from collections import defaultdict
from sklearn.metrics.pairwise import cosine_similarity

class LlmOperations:
    """
    A class that encapsulates operations related to interacting with a language model.
    It handles preparing input data, requesting model responses, and computing similarity
    between generated responses and provided system inputs.
    """
    def __init__(self, data: Union[list, dict], instructions: str):
        """
        Initializes the LlmOperations instance.

        Args:
            data (Union[list, dict]): The input data to be processed.
            instructions (str): The instructions to be given to the model.
        """        
        self.utility = Utility()
        self.model_name = self.utility.get_model_name()
        self.data = data.copy()
        self.instructions = instructions + "\n" + self.utility.get_additional_instructions()
        self.input_list = self.get_input_list(data)
        self.client = openai.AsyncOpenAI(
            base_url="https://api.openai.com/v1",
            api_key=self.utility.get_api_key()
        )
        
    def get_input_list(self, data: Union[list, dict]) -> List:
        """
        Prepares the input data into a list format required by the model.

        Args:
            data (Union[list, dict]): The data to be processed into a list.

        Returns:
            List: The list of inputs prepared from the data.
        """        
        prepare_batch_from_data = PrepareBatch(data)
        return prepare_batch_from_data.create_input_list()
    
    async def get_embedding(self, text, model="text-embedding-ada-002"):
        """
        Asynchronously retrieves the embedding of a given text using the specified model.

        Args:
            text (str): The text for which to retrieve the embedding.
            model (str, optional): The model to use for embedding generation. Defaults to "text-embedding-ada-002".

        Returns:
            List[float]: The embedding vector of the text.
        """        
        text = text.replace("\n", " ")
        embedding_creation = await self.client.embeddings.create(input = [text], model=model)
        return embedding_creation.data[0].embedding
    
    async def compute_similarity(self, text1, text2, model="text-embedding-ada-002"):
        """
        Asynchronously computes the cosine similarity between two pieces of text.

        Args:
            text1 (str): The first text for comparison.
            text2 (str): The second text for comparison.
            model (str, optional): The model to use for generating embeddings. Defaults to "text-embedding-ada-002".

        Returns:
            float: The cosine similarity score between the two texts (range [0, 1]).
        """        
        # Get embeddings for both texts
        embedding1 = await self.get_embedding(text1, model)
        embedding2 = await self.get_embedding(text2, model)
        
        # Compute the cosine similarity
        similarity = cosine_similarity([embedding1], [embedding2])
        
        return similarity[0][0]
        
    async def get_response(self, system_input: str, user_input: str, num_tokens: int = 16384) -> str:
        """
        Asynchronously requests a response from the language model based on system and user input.

        Args:
            system_input (str): The input json data to guide the response.
            user_input (str): The instructions message.
            num_tokens (int, optional): The maximum number of tokens to return in the model's response. Defaults to 16384.

        Returns:
            str: The generated response from the model.
        """        
        completion = await self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_input},
                {"role": "user", "content": user_input}
            ],
            max_tokens= num_tokens
        )
        content = completion.choices[0].message.content
        similarity = await self.compute_similarity(content, system_input)
        output = content if content.find(self.utility.get_check_text()) == -1 and similarity > 0.8 else system_input
        return output
    
    async def run_inputs(self) -> Dict:
        """
        Asynchronously processes all inputs and requests responses from the model.

        Returns:
            Dict: A dictionary containing the processed responses for each input.
        """        
        tasks = {(key_chain, index): self.get_response(system_input, self.instructions, num_tokens) for key_chain, index, system_input, num_tokens in self.input_list}
        awaited_results = await asyncio.gather(*tasks.values())
        final_result = defaultdict(dict)
        for (key_chain, index), result in zip(tasks.keys(), awaited_results):
            final_result[key_chain][index] = result
        return final_result
    
    async def get_updated_data(self) -> Dict:
        """
        Asynchronously fetches the updated data after processing all inputs.

        Returns:
            Dict: The updated data after running through the language model.
        """        
        llm_results = await self.run_inputs()
        return JsonOperations.json_recover(llm_results)
