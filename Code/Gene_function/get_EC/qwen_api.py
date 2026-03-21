from openai import OpenAI
import time
import sentencepiece

def countTokens(prompt):
    sp = sentencepiece.SentencePieceProcessor(model_file='/home/zhetao/.cache/modelscope/hub/AI-ModelScope/Mixtral-8x7B-Instruct-v0.1/tokenizer.model')
    prompt_tokens = sp.encode_as_ids(prompt)
    return len(prompt_tokens)

def qwen_api(user_message, port=8000, top_p=0.9, temperature=0.5, system_message='', max_tokens=4096):
    # OpenAI
    client = OpenAI(
        base_url=f"http://localhost:{port}/v1",  # API URL
        api_key="none"  # API key
    )

    history = []
    if system_message:
        history.append({'role': 'system', 'content': system_message})
    history.append({"role": "user", "content": user_message})

    try:
        # Ask
        start_time = time.time()
        response = client.chat.completions.create(
            # model="gpt-oss-120b",  # model path
            # model="Llama3.1_8B_NER",
            model="Llama-3.3-70B-Instruct",
            messages=history,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            frequency_penalty=0.0,
            presence_penalty=1.0,
            stop=[],
            stream=False
        )
        use_time = time.time() - start_time
        response_content = response.choices[0].message.content
        print(response_content)
        token_length = countTokens(response_content)
        print('time cost:', round(use_time, 2), 'Second\nSpeed:', round(token_length/use_time, 2), 'token/s')

    except KeyError as e:
        print(f"KeyError: {e} - The response structure does not match expectations")
        print(f"Full responce: {response if 'response' in locals() else 'No responds'}")
    except Exception as ex:
        print(f"Other errors: {ex}")

    return response_content if 'response_content' in locals() else None


if __name__ == '__main__':
    system_prompt = "You are a helpful assistant."
    text = '''The high affinity glyoxylate reductase gene GLYR1 was expressed in K. lactis strain containing malate synthase and isocitrate dehydrogenase deletions. ... (truncated for brevity)'''
    prompt = """Give me a concise question to which the answer is “{}”. Answer as a question, one sentence, short.""".format(text)
    result = qwen_api(prompt, port=8000, top_p=0.7, temperature=0.7, system_message=system_prompt)
