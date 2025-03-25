class StringBuilder:
    """
    A utility class to efficiently build and manipulate strings by accumulating
    individual string parts in a container. It supports adding strings, clearing 
    the container, popping strings, and retrieving the final concatenated result 
    with a specified delimiter.
    """
    
    def __init__(self, delimiter: str = ""):
        """
        Initializes the StringBuilder instance.

        Args:
            delimiter (str): The delimiter to be used between added strings when 
                              retrieving the final concatenated result. Defaults to an empty string.
        """
        self.container = []  # Initialize an empty list to store strings
        self.delimeter = delimiter  # Set the delimiter for string concatenation

    def add(self, s: str) -> None:
        """
        Adds a new string to the container.

        Args:
            s (str): The string to be added to the container.
        """
        self.container.append(s)  # Append the string to the container

    def clear(self) -> None:
        """
        Clears all the strings from the container, effectively resetting the builder.
        """
        self.container.clear()  # Remove all strings from the container

    def pop(self) -> str:
        """
        Removes and returns the last added string from the container.

        Returns:
            str: The last string added to the container.
        """
        return self.container.pop()  # Pop and return the last string from the container

    def get(self) -> str:
        """
        Retrieves the final concatenated string, with all strings in the container 
        joined by the specified delimiter.

        Returns:
            str: The concatenated string with the delimiter in between parts.
        """
        return self.delimeter.join(self.container)  # Join the strings using the delimiter and return the result