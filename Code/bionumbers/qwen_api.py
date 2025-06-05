from openai import OpenAI
import time
import sentencepiece

def countTokens(prompt):
    sp = sentencepiece.SentencePieceProcessor(model_file='/home/xiongwen/llama2-model/llama2-13b-chat/tokenizer.model')
    prompt_tokens = sp.encode_as_ids(prompt)
    return len(prompt_tokens)

def qwen_api(user_message, port=8000, top_p=0.9, temperature=0.5, system_message='', max_tokens=4096):
    # 初始化 OpenAI 客户端
    client = OpenAI(
        base_url=f"http://localhost:{port}/v1",  # 设置 API 的基础 URL
        api_key="none"  # 设置 API 密钥
    )

    history = []
    if system_message:
        history.append({'role': 'system', 'content': system_message})
    history.append({"role": "user", "content": user_message})

    try:
        # 创建请求
        start_time = time.time()
        response = client.chat.completions.create(
            model="/home/xiongwen/Llama-3.1-70B",  # 模型路径
            messages=history,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            frequency_penalty=0.0,
            presence_penalty=1.0,
            stop=[],  # 可以添加自定义的停止词
            stream=False
        )
        use_time = time.time() - start_time
        response_content = response.choices[0].message.content
        print(response_content)
        token_length = countTokens(response_content)
        print('花费时间:', round(use_time, 2), '秒\n速率:', round(token_length/use_time, 2), 'token/s')

    except KeyError as e:
        print(f"KeyError: {e} - 可能是因为响应结构不符合预期。")
        print(f"完整响应内容: {response if 'response' in locals() else '没有收到有效响应'}")
    except Exception as ex:
        print(f"其他错误: {ex}")

    return response_content if 'response_content' in locals() else None


if __name__ == '__main__':
    system_prompt = "You are a helpful assistant."
    text = '''The high affinity glyoxylate reductase gene GLYR1 was expressed in K. lactis strain containing malate synthase and isocitrate dehydrogenase deletions. ... (truncated for brevity)'''
    prompt = """Give me a concise question to which the answer is “{}”. Answer as a question, one sentence, short.""".format(text)
    result = qwen_api(prompt, port=8000, top_p=0.7, temperature=0.7, system_message=system_prompt)