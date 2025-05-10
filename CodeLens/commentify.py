# this code is used to comment a file in a repo
import os
import sys
from typing import List
import google.generativeai as genai
import time

GEMINI_API_KEY = "AIzaSyCBYIosCIl1nizUdA4M1qjqueTh2e-36s4"
genai.configure(api_key=GEMINI_API_KEY)

def chunk_code(lines, max_chars=20000): # we are considering the default max_chars to be 10000
    # this function chunk_code make the codeinto chuncks and then return that to the commentify to facilitate the limited prompt size of the llm used
    chunks, current_chunk=[],[]
    current_length =0

    for line in lines:
        if current_length+len(line)>max_chars:
            chunks.append("".join(current_chunk))
            current_chunk,current_length=[line],len(line)
        else:
            current_chunk.append(line)
            current_length+=len(line)
    if current_chunk:
        chunks.append("".join(current_chunk))
    return chunks

def generate_comments(code_chunk):
    prompt = (
        "Please add concise, helpful comments to the following code. "
        "Place the comments above each relevant line, and do not rewrite the code structure:\n\n"
        "Don't write too many comments just add the comments to which it is important."
        "Just add comments to the code , don't generate any extra test just add comments."
        "Don't even add ```cpp ``` block just treat the code as text add comments in between that's it."
        f"{code_chunk}"
    )
    model = genai.GenerativeModel("models/gemini-1.5-pro-002")
    response=model.generate_content(prompt)
    return response.text

def commentify_file(file_path: str):
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found")
        sys.exit(1)
    
    with open(file_path, "r", encoding="utf-8") as f:
        code_lines=f.readlines()

    chunks=chunk_code(code_lines)
    final_code=[]

    for i, chunk in enumerate(chunks):
        commented=generate_comments(chunk)
        final_code.append(commented.strip())

    with open(file_path,"w",encoding="utf-8") as f:
        f.write("\n\n".join(final_code))

    print(f"✅ Comments added to {file_path}")

    

if __name__=="__main__":
    if len(sys.argv) !=2:
        print("Usage: python commentify.py <file_path>")
        sys.exit(1)
    
    file_path=sys.argv[1]
    start_time = time.time()
    commentify_file(file_path)
    end_time = time.time()
    print(f"⏱️ Time taken: {end_time - start_time:.2f} seconds")