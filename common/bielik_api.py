import requests
import json


def call_model_non_stream(system_prompt, user_prompt):
    url = "http://localhost:11434/api/generate"
    
    data = {
        "model": "Bielik-11B-v2_6-Instruct_Q4_K_M",
        "system": system_prompt,
        "prompt": user_prompt,
        "stream": False
    }
    
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        
        json_response = response.json()
        return json_response.get('response', '')
        
    except requests.exceptions.RequestException as e:
        return f"Error connecting to Ollama API: {e}"
    except Exception as e:
        return f"Unexpected error: {e}"


def call_model_stream(system_prompt, user_prompt):
    url = "http://localhost:11434/api/generate"
    
    data = {
        "model": "Bielik-11B-v2_6-Instruct_Q4_K_M",
        "system": system_prompt,
        "prompt": user_prompt,
        "stream": True
    }
    
    try:
        response = requests.post(url, json=data, stream=True)
        response.raise_for_status()
        
        for line in response.iter_lines():
            if line:
                try:
                    json_response = json.loads(line.decode('utf-8'))
                    if 'response' in json_response:
                        yield json_response['response']
                    
                    # Check if the response is done
                    if json_response.get('done', False):
                        break
                        
                except json.JSONDecodeError:
                    continue
                    
    except requests.exceptions.RequestException as e:
        yield f"Error connecting to Ollama API: {e}"
    except Exception as e:
        yield f"Unexpected error: {e}"