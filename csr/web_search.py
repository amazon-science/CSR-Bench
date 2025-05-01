import json
import requests


def perplexity_search(question):
    API_KEY = "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"
    MODEL = "llama-3-sonar-large-32k-online"
    url = "https://api.perplexity.ai/chat/completions"

    payload = {
        "model": MODEL,
        "messages": [
            # {"role": "system", "content": "Be precise and concise."},
            {"role": "system", "content": "RETURN THE MOST RELEVANT AND PRECISE SOLUTION CONCISELY."},
            {"role": "user", "content": question}
        ],
        "search_quality": 10,
        "search_quality_reflection": True,
    }
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "accept": "application/json",
        "content-type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)
    try:
        result = json.loads(response.text)
        # Navigate through the nested dictionary safely
        content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
        return content if content else "No content available"
    except json.JSONDecodeError:
        # Handle cases where the response is not a valid JSON
        return "Invalid JSON response"
    except Exception as e:
        # Handle other unforeseen errors
        return f"An error occurred: {str(e)}"

if __name__ == "__main__":
    # Example usage
    question = "Can you search the internet to answer this question: Are the following two records the same business? Record 1: GUARDIAN AND IDA PHARMACY, 3352 KEELE ST TORONTO M3J1L5 ON Record 2: WELLCARE PHARMACY, 3352 KEELE ST TORONTO M3J1L5 ON] Do you have internet access to search for more accurate answers?"
    question = "How to install PyTorch on Windows?"
    result_text = perplexity_search(question)
    print(result_text)
