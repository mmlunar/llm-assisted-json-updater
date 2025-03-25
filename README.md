# Project Overview

## Introduction

This document provides a brief overview of the solution approach and related details for the json file updater project. It will guide the reader through the code to offer a clearer understanding of how the solution works.

## Solution Approach

This section presents an overview of the solution approach, starting with the problem description, followed by the algorithm and approach used to address the problem.

### Problem

The task at hand is to edit a JSON file based on given instructions. These instructions are presented as plain text, which resembles how we might ask a human to perform a job. However, our goal is to automate the process of converting these instructions into code that modifies the JSON file.

### Solution Overview

The solution leverages OpenAI’s API to process the instructions and generate the required results, which are then saved to the JSON file. While this may sound straightforward, there is a significant challenge posed by the size (token) limitations of the input and output texts that OpenAI’s API can handle. If the text exceeds the API’s token limit, it cannot be processed as a single request. Therefore, the solution must process the task in smaller batches and then combine the results. To address this challenge, the following approach is adopted:

- **Handling Large Lists in JSON:** Many JSON files contain large lists, which often account for the majority of the tokens. When dealing with large JSON files, the lists become the primary focus for batch processing. The strategy is to traverse the JSON object, identify the lists, and if any list exceeds a threshold token count, replace it with a dummy object for the time being. The list can then be processed later in smaller batches. For counting tokens, the `tiktoken` library from OpenAI is used.

- **Batch Processing and Submission:** Once the large lists are split into smaller batches, the next task is to submit them for processing. There are two potential ways to submit batches to OpenAI’s API:
  1. **Batch API:** OpenAI offers a batch API where multiple instructions can be written into a file and uploaded. However, this approach did not work in the given scenario due to the lack of permission for file tasks.
  2. **Sequential Submission:** Therefore, the solution opted for submitting each batch individually. To make this process more efficient, the solution is designed to submit batches asynchronously, allowing the tasks to run in parallel rather than waiting for each one to complete before starting the next.

- **Combining Results:** After receiving the results from the API, we need to combine them. To ensure the results are consistent and accurate, cosine similarity is checked between the input and output texts. In most cases, the modifications are minor, and the input and output texts remain similar. If the AI generates something unexpected, the cosine similarity can help detect anomalies.

- **Updating the JSON:** The results are combined using a key-value paired dictionary that tracks the sequences of updated lists. This ensures that the modified lists are correctly inserted into the new file.

- **Final Formatting and Output:** After combining the results, some text formatting issues (due to the API’s output style) are corrected. The final output is then saved to the JSON file.

## Validation & Testing

The solution has been validated using two tools:

1. **VS Code’s Compare Files Feature:** This tool was used to highlight and verify all changes, ensuring that the changes were legitimate.
2. **Notepad++ String Counter:** This tool was employed to track all expected changes and verify that the corresponding changes were made in the output.


## Challenges

Overall, no significant issues were encountered during the implementation. The primary challenge was occasional timeouts and delays from the API, but the system generally performed as expected.

## Code Overview

In addition to the *main.py*, the solution consists of five Python files and one configuration file: *llm_operations.py*, *utility.py*, *prepare_batch.py*, *json_operations.py*, *string_builder.py*, and *config.json*. Each file contains comments that describe the functionality of the corresponding classes and methods.

At a high level, *llm_operations.py* is the core module requested by *json_editor.py*. This file handles the preparation of batched inputs using *prepare_batch.py* and post-processing tasks using *json_operations.py*. The *string_builder.py* file provides string manipulation support, while *utility.py* offers a range of auxiliary functions to support the solution. Configuration settings are stored in the *config.json* file.

## Acknowledgements

- The JSON data used in this project has been sourced from the following repository: [DummyJSON](https://github.com/Ovi/DummyJSON/).
- The concept for this problem is credited to the company: [Gradial](https://gradial.com).

## License

This project is licensed under the **GNU General Public License v3.0 (GPL-3.0)**.

See the [LICENSE](https://www.gnu.org/licenses/gpl-3.0.en.html) file or visit [gnu.org](https://www.gnu.org/licenses/gpl-3.0.html) for full terms.

This project is for educational and research purposes. Respect the license terms of third-party datasets and models.

