from collections import defaultdict
import os
import json
import openai
from typing import Dict, List

# openai.api_key= os.getenv("OPENAI_API_KEY", "")

EXAMPLE_HATCH_OUTPUT = f"""
Green Drakes (Ephemera guttulata), Green Drake Dry Fly, 10-12, Olive body with gray wings and a touch of brown
Green Drakes (Ephemera guttulata), Green Drake Nymph, 10-12, Olive body with brown and gray accents
Golden Stoneflies, Golden Stonefly Dry, 6-10, Yellow or tan body with dark mottled wings and brown hackle
Golden Stoneflies, Pat's Rubber Legs, 6-10, Dark brown or black body with rubber legs and a touch of orange
Terrestrials, Dave's Hopper, 10-12, Tan or yellow body with a foam wing and rubber legs
Terrestrials, Black Foam Ant, 14-16, Black foam body with a sparse wing and black hackle
"""

EXAMPLE_MATERIALS_OUTPUT = f"""
Elk Hair Caddis, Hook, Size 12-16 dry fly hook
Elk Hair Caddis, Thread, Pink or red 6/0 or 8/0 thread
Elk Hair Caddis, Tail, Medium dun hackle fibers
Elk Hair Caddis, Body, Dubbing in a pinkish-red color
Elk Hair Caddis, Post, White or pink synthetic yarn (for the parachute)
Elk Hair Caddis, Hackle, Brown or grizzly rooster hackle
Elk Hair Caddis, Wing, White or light gray calf body hair
"""


GPT_PRICING = {
    "gpt-3.5-turbo": {
        "completion_tokens": 0.002,
        "prompt_tokens": 0.0015
    }
}

def gpt_call(prompt, model: str = "gpt-3.5-turbo"):
    # Generic wrapper for llm call
    print("Calling Pulze...")
    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    llm_output = response.choices[0].message
    if model in GPT_PRICING:
        prompt_cost = (response['usage']['prompt_tokens'] / 1000 * GPT_PRICING.get(model).get("prompt_tokens"))
        completion_cost = (response['usage']['completion_tokens'] / 1000 * GPT_PRICING.get(model).get("completion_tokens"))
        print(f"Prompt Cost: ${round(prompt_cost + completion_cost, 5)}")

    return llm_output["content"]


def generate_hatch_list(location: str, river: str, target_species: str, season: str) -> Dict[str, Dict]:
    prompt = (
        f"""
        I am planning a fly-fishing trip to {location}, where I will be targeting {target_species} on the {river}. 
        The trip will be in {season}. Predict at least 5 of the insect hatches that will be going on in this area at this point in the season, 
        and suggest at least two patterns for each of the insect species. Include the hook sizes 
        and colors of the recommended fly patterns. Return each fly pattern on a new line in the following format:
        
        Insect Species (optional latin name), Fly Pattern Name, Hook Size, Color Description

        Example Output:
        {EXAMPLE_HATCH_OUTPUT}
        """
    )
    
    content = gpt_call(prompt).split("\n")
    print(content)
    hatches_to_patterns = defaultdict(list)
    for pattern in content:
        # print(f"Retrieved pattern: {pattern}")
        try:
            parsed_pattern = pattern.split(', ')
            hatches_to_patterns[parsed_pattern[0]].append({
                "pattern": parsed_pattern[1],
                "hook_size": parsed_pattern[2],
                "description": parsed_pattern[3],
            })
        except Exception as e:
            print(f"Unable to add pattern due to unexpected format: {repr(e)}")
            print(f"Failing pattern: {pattern}")

    print(hatches_to_patterns)
    return hatches_to_patterns

    
def generate_pattern_materials_list(hatches_to_patterns):
    pattern_list_for_materials = "\n"
    for hatch, patterns in hatches_to_patterns.items():
        for pattern in patterns:
            pattern_list_for_materials += hatch + ", " + pattern["pattern"] + ", Size " + pattern["hook_size"] + ", " + pattern["description"] + "\n"
    

    prompt = f"""
Generate and combine a complete shopping list of materials for a list of fly fishing patterns. Do not include any other headers or information, only the cumulative list of recommended materials.
Format each line of the output in the following format:

Pattern, Component, Description

An example input list and desired output is given below:

Example fly pattern: 
Caddisflies, Elk Hair Caddis, Size 14-18, Light tan or brown body with elk hair wings and a brown hackle

Example output:
{EXAMPLE_MATERIALS_OUTPUT}

Generate the material shopping list for the following list of patterns:
{pattern_list_for_materials}
"""

    print(prompt)

    llm_output = gpt_call(prompt).split("\n")
    pattern_to_materials = defaultdict(list)
    print(llm_output)
    for line in llm_output:
        try:
            parsed_line = line.split(", ")
            pattern_to_materials[parsed_line[0]].append(([parsed_line[1]], parsed_line[2]))
        except Exception as e:
            print(f"Unable to add material due to unexpected format: {repr(e)}")
            print(f"Failing material: {line}")

    return pattern_to_materials
