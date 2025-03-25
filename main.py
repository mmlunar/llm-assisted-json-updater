import sys
import os
import argparse
import json
import asyncio
from pathlib import Path
import os
from llm_operations import LlmOperations



async def modify_json(input_data, instructions):
    llm_op = LlmOperations(input_data, instructions)
    responses = await llm_op.get_updated_data()
    return responses


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", required=True, help="JSON input file")
    parser.add_argument("--instruction", required=True, help="Instruction file")
    args = parser.parse_args()

    # Remove any 'inputs/' prefix if it exists
    input_json_path = args.json
    instruction_path = args.instruction

    # Now add the inputs/ prefix just once for input files
    input_json_path = os.path.join("inputs", input_json_path)
    instruction_path = os.path.join("inputs", instruction_path)

    # Load the input JSON
    with open(input_json_path, "r") as f:
        input_data = json.load(f)

    # Load the instruction JSON
    with open(instruction_path, "r") as f:
        instructions = json.load(f)

    # Create output path using test_num and test_case
    output_path = os.path.join("outputs", args.json)

    # Here you would implement your logic to modify input_data based on instructions.
    modified_json = await modify_json(input_data, json.dumps(instructions))

    # Write the modified JSON to the output
    with open(output_path, "w") as f:
        print("Outputting to", output_path)
        json.dump(modified_json, f, indent=2)

    print(f"Modified JSON written to {output_path}")


if __name__ == "__main__":
    asyncio.run(main())
