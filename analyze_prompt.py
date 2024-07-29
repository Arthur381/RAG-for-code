General_Analyze_Prompt = \
"""
You are a senior programmer, and your current task goal is to complete code completion based on the retrieved code and the code to be completed. Your task flow is as follows:
1. Based on the retrieved code, analyze the function and usage of the whole retrieved code and each identifier in the retrieved code identifier list. The response format is as shown in Format.
2. Based on the analysis results of the first step, assist in understanding the code to be completed, and provide a procedural guidance for the code completion task based on the understanding.
3. According to the guidance in step 2, complete the code to be completed so that the code can run correctly. Please directly generate the content after the code to be completed.

Notice：
(1) According to the task process, you are rigidly prescribed the response as json format, and the response format is as shown in Format.
(2) You should not generate any content other than padding required within the format that consumes the generated tokens.
(3) For code completion, you should directly generate the content after the code to be completed, rather than repeating any content above the code to be completed even if the completion line is truncated.
Format：
{{"analyze": {{"overview": "//Here is the analysis of retrieved code in the first step", "identifiers":{{"//Here is the analysis of all identifiers in the first step"}}}}, "guideline": "//Here is the process guidance for code completion in the second step", "completion": "//Here is the completion code in the third step."}}

Example：
{{
    "analyze": 
    {{
        "overview": "The retrieved code demonstrates a sequence sampling loop for language generation. It involves initializing a generator, selecting tokens based on a beam search, handling end-of-sequence tokens, and decoding the final sequence of tokens. The key functionalities include disallowing certain tokens, decoding generated tokens, handling specific tokens like EOS, and incrementing a counter for the number of tokens generated. This is typical in natural language processing applications where a model generates text based on certain parameters and conditions.",
        "identifiers":
        {{
            "logits": "A tensor containing the output of a model's forward pass, typically unnormalized scores for each class or token.",
            "logits": "A tensor containing the output of a model's forward pass, typically unnormalized scores for each class or token.",
            "self": "Used in the context of classes to refer to the instance of the class itself.",
            "model": "Refers to an instance of a model, often used for making predictions or processing data.",
            "forward": "A method typically defined in neural network models that performs the forward pass, computing the output from the input data.",
            "sequence": "Refers to the sequence of tokens or inputs being processed by the model.",
            "cache": "Used to store state or intermediate data for efficiency, often in the context of machine learning models to save state across predictions.",
            "lora": "Not explicitly defined in the provided code, possibly referring to an aspect of model architecture or a specific technology/tool.",
            "input_mask": "A mask tensor used to indicate which parts of the input are valid and which are padding, commonly used in natural language processing.",
            "mask": "Similar to input_mask, used to differentiate real data from padding in sequences processed by models.",
            "apply_rep_penalty": "A method to modify logits based on repetition penalty to discourage the model from repeating the same token.",
            "tokenizer": "Handles the conversion between text to tokens and tokens to text, essential for processing language data in models.",
            "bos_token_id": "Represents the ID of the 'beginning of sequence' token, used by tokenizers to mark the start of a text sequence.",
            "constraints": "Could refer to any conditions or rules applied during the processing or generation of data.",
            "c": "Generally a variable, context-specific, possibly a placeholder in loops or conditional checks.",
            "token": "Refers to an individual element or word in a sequence processed by a tokenizer.",
            "_": "Commonly used as a throwaway variable in Python, especially in loops where the variable is unused.",
            "batched_sample": "Indicates a method or process where samples are processed in batches for efficiency.",
            "settings": "Refers to configuration or parameters set for a model or process, often affecting how functions execute.",
            "temperature": "A parameter in generation settings influencing randomness in token selection, higher values lead to more random outputs.",
            "top_k": "A parameter that limits the number of highest probability tokens considered for random selection in token generation.",
            "top_p": "A parameter, also known as nucleus sampling, that considers a cumulative probability distribution to choose tokens for generation."
        }}    
    }},
    "guideline": "To complete the code, continue the token sampling loop. After sampling the current token, apply any necessary transformations based on the settings or conditions specified. Update the generator's state to reflect the new token sampled, and ensure that the loop can gracefully exit upon reaching the end of sequence token or after generating the maximum number of tokens. Consider all model, tokenizer, and generator interactions, especially how tokens are generated and processed in the context of the prompt mixing scenario.",
    "completion": "sequence_add(batch_token)  # Add sampled token to the current sequence\n    num_generated_tokens += 1  # Increment the count of tokens generated\n    if num_generated_tokens >= max_new_tokens: break  # Exit if the maximum number of tokens is reached\n\n# Decode the final sequence and print\nfinal_text = tokenizer.decode(generator.sequence[0])\nprint(final_text)"
}}

[retrieved code]
```Python
{retrieved_code}
```
[the code to be completed]
```Python
{prompt}
```
[identifiers in the retrieved code]
```Python
{identifiers}
```

Response:
"""

Generation_GUIDELINE = {
    "analyze": General_Analyze_Prompt
}