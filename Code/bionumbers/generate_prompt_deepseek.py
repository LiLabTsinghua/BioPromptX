from qwen_api import qwen_api
import random
import numpy as np
import spacy  # For embedding-based state representation
import torch
from collections import deque
import os
from openai import OpenAI
import re
import time  # For retry mechanism
import requests

# Load spaCy's pre-trained model
nlp = spacy.load('en_core_web_md')  # Medium-sized model with word vectors

# Constants
NUM_EPISODES = 5  # Number of episodes for RL training
MAX_STEPS_PER_EPISODE = 10  # Maximum steps per episode
LEARNING_RATE = 0.001  # Learning rate for DQN
DISCOUNT_FACTOR = 0.9  # Discount factor for future rewards
EPSILON_START = 1.0  # Initial exploration rateEPISODES
EPSILON_END = 0.01  # Minimum exploration rate
EPSILON_DECAY = 0.995  # Decay rate for exploration
BATCH_SIZE = 32  # Batch size for DQN training
MEMORY_SIZE = 1000  # Size of the replay memory

# Placeholder for Replay Memory
replay_memory = deque(maxlen=MEMORY_SIZE)

# List to store all full-score prompts
full_score_prompts = []


# DQN Model with 1D CNN
class DQN(torch.nn.Module):
    def __init__(self, input_dim, output_dim):
        super(DQN, self).__init__()
        self.conv1 = torch.nn.Conv1d(in_channels=1, out_channels=32, kernel_size=3, stride=1, padding=1)
        self.conv2 = torch.nn.Conv1d(in_channels=32, out_channels=64, kernel_size=3, stride=1, padding=1)
        self.fc1 = torch.nn.Linear(64 * input_dim, 128)
        self.fc2 = torch.nn.Linear(128, output_dim)

    def forward(self, x):
        x = x.unsqueeze(1)  # Add a channel dimension for Conv1d
        x = torch.relu(self.conv1(x))
        x = torch.relu(self.conv2(x))
        x = x.view(x.size(0), -1)  # Flatten the tensor
        x = torch.relu(self.fc1(x))
        return self.fc2(x)


# Initialize DQN
input_dim = 300  # Dimension of spaCy's word vectors
output_dim = 5  # Number of actions
dqn = DQN(input_dim, output_dim)
optimizer = torch.optim.Adam(dqn.parameters(), lr=LEARNING_RATE)
loss_fn = torch.nn.MSELoss()

# Initialize the DeepSeek client
client = OpenAI(api_key="sk-3630bcbc16fe459ab1f3cc72b8e5a24f", base_url="https://api.deepseek.com")


def load_prompt_from_file(file_path):
    """Read prompts from a text file."""
    with open(file_path, 'r') as file:
        return file.read()


def generate_initial_prompt(content_to_extract):
    """Generate an initial prompt using qwen_api with dynamic content to extract."""
    system_prompt = 'You are a knowledgeable assistant in molecular biology.'
    prompt = f"""
    Generate a prompt to extract "{content_to_extract}" values with units and annotation from the article.

    Only generate a prompt.
    Output format:
    "{content_to_extract}" prompt: "generated prompt"
    """
    result = qwen_api(user_message=prompt, top_p=0.6, system_message=system_prompt)
    return result


def modify_prompt(prompt, action, base_prompts, content_to_extract, suggestions=None):
    """Modify the prompt using qwen_api based on the action, base prompts, and suggestions."""
    system_prompt = 'You are a knowledgeable assistant in molecular biology.'
    action_descriptions = [
        "Add more details to the prompt, especially focusing on numerical values and tables.",
        "Focus on key points in the prompt, ensuring clarity and specificity for numerical data.",
        "Make the prompt more concise while ensuring no numerical values are omitted.",
        "Add specific examples to the prompt, particularly from tables and numerical data.",
        "Rephrase the prompt for clarity, emphasizing the importance of numerical values."
    ]
    modification_instruction = action_descriptions[action]

    # Include suggestions if provided
    if suggestions:
        modification_instruction += f"\nAdditional suggestions: {', '.join(suggestions)}"

    prompt = f"""
    Based on the following prompts, modify the given prompt to extract "{content_to_extract}" information.
    Prompts: {base_prompts}

    Modification Instruction: {modification_instruction}
    Current Prompt: {prompt}

    Only generate the modified prompt.
    Output format:
    "{content_to_extract}" prompt: "modified prompt"
    """
    result = qwen_api(user_message=prompt, top_p=0.6, system_message=system_prompt)
    return result


def parse_score_from_response(response):
    """Use regular expression to extract score from response"""
    # Match integers or floating point numbers (including decimal values)
    score_match = re.search(r'\b\d+(?:\.\d+)?\b', response)
    if not score_match:
        raise ValueError("No valid number found in the response")

    score_str = score_match.group()
    score = float(score_str)

    if 0 <= score < 10:
        return score
    else:
        raise ValueError(f"Score {score} is out of range 0-9")


def deepseek_api(user_message, system_message="You are a helpful assistant", top_p=0.6, model="deepseek-chat",
                 stream=False):
    """
    Call DeepSeek API to generate a response based on user and system messages.
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message},
            ],
            top_p=top_p,
            stream=stream
        )

        if not stream:
            if hasattr(response, 'choices') and len(response.choices) > 0:
                return response.choices[0].message.content
            else:
                raise ValueError("Invalid API response")
        else:
            full_response = ""
            for chunk in response:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
            return full_response
    except Exception as e:
        print(f"API call failed: {e}")
        raise


def deepseek_api_with_retry(user_message, system_message="You are a helpful assistant", max_retries=5,
                            backoff_factor=1):
    """Exponential backoff retry mechanism"""
    for attempt in range(max_retries):
        try:
            response = deepseek_api(user_message=user_message, system_message=system_message)
            return response
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            sleep_time = backoff_factor * (2 ** attempt)
            print(f"Request failed: {str(e)}. Retrying in {sleep_time} seconds...")
            time.sleep(sleep_time)
    raise Exception("Exceeded maximum retries")


def evaluate_prompt(prompt):
    """Evaluate prompt quality (0-9 scale) and get modification suggestions."""
    system_prompt = 'You are an expert in molecular biology evaluation'
    evaluation_prompt = f"""
    Please score the following prompt strictly based on the following criteria:
    1. Clarity (0-3 points)
    2. Specificity (0-3 points)
    3. Effectiveness (0-3 points)
    The total score is 9 points. Provide the final score and a brief suggestion for improvement.

    **Output format** 
    Total score: <score>
    Suggestion: <suggestion>

    Prompt to evaluate: {prompt}
    """

    try:
        response = deepseek_api_with_retry(
            user_message=evaluation_prompt,
            system_message=system_prompt,
            max_retries=5
        )
        # Extract score and suggestion from the response
        score = parse_score_from_response(response)
        suggestion = response.split("Suggestion:")[-1].strip() if "Suggestion:" in response else ""
        return score, suggestion
    except Exception as e:
        print(f"Critical error: Evaluation process failed - {str(e)}")
        raise


def get_three_valid_scores(prompt):
    """Get three valid scores and corresponding suggestions."""
    scores = []
    suggestions = []
    while len(scores) < 3:
        try:
            score, suggestion = evaluate_prompt(prompt)
            scores.append(score)
            suggestions.append(suggestion)
            print(f"Successfully received score: {score} ({len(scores)}/3)")
        except Exception as e:
            print(f"Score failed, retrying... Reason: {str(e)}")

    print(f"Final valid scores: {scores}")
    print(f"Corresponding suggestions: {suggestions}")
    return scores, suggestions


def get_state(prompt):
    """Convert the prompt into a state representation using spaCy."""
    doc = nlp(prompt)
    return doc.vector  # Use spaCy's document vector as state representation


def choose_action(state, epsilon):
    """Choose an action based on the current state and exploration rate."""
    if random.uniform(0, 1) < epsilon:
        return random.randint(0, 4)  # Random action (exploration)
    else:
        state_tensor = torch.FloatTensor(state).unsqueeze(0)
        q_values = dqn(state_tensor)
        return torch.argmax(q_values).item()  # Best action (exploitation)


def update_dqn():
    """Update the DQN using a batch of experiences from replay memory."""
    if len(replay_memory) < BATCH_SIZE:
        return

    batch = random.sample(replay_memory, BATCH_SIZE)
    states, actions, rewards, next_states = zip(*batch)

    states = torch.FloatTensor(np.array(states))
    actions = torch.LongTensor(actions)
    rewards = torch.FloatTensor(rewards)
    next_states = torch.FloatTensor(np.array(next_states))

    current_q_values = dqn(states).gather(1, actions.unsqueeze(1))
    next_q_values = dqn(next_states).max(1)[0].detach()
    target_q_values = rewards + DISCOUNT_FACTOR * next_q_values

    loss = loss_fn(current_q_values.squeeze(), target_q_values)
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()


def vote_for_best_prompt(prompts):
    """
    Perform a single voting round to select the best prompt.
    Returns the prompt with the highest score.
    """
    if not prompts:
        raise ValueError("No prompts provided for voting.")

    # 确保提示是独立的
    unique_prompts = list(set(prompts))  # 去重
    print("Unique prompts for voting:", unique_prompts)

    # 初始化投票计数
    vote_counts = {prompt: 0 for prompt in unique_prompts}
    print("Initial vote counts:", vote_counts)

    # 执行投票
    try:
        # 将所有提示组合成一个消息
        combined_prompts = "\n".join([f"Prompt {i + 1}: {prompt}" for i, prompt in enumerate(unique_prompts)])
        user_message = f"""
        Please evaluate the following prompts and select the best one based on clarity, specificity, and effectiveness.
        Return only the number of the best prompt (e.g., '1', '2', etc.).

        Prompts:
        {combined_prompts}
        """

        # 调用 API 获取最佳提示
        response = deepseek_api(
            user_message=user_message,
            system_message="You are an expert in prompt evaluation."
        )

        # 提取选择的提示编号
        selected_prompt_number = int(re.search(r'\d+', response).group())
        selected_prompt = unique_prompts[selected_prompt_number - 1]  # 转换为 0-based 索引

        print(f"Selected best prompt: {selected_prompt}")
        return selected_prompt

    except Exception as e:
        print(f"Error during voting: {e}")
        # 如果投票失败，返回第一个提示作为备选
        print("Falling back to the first prompt.")
        return unique_prompts[0]


def rl_prompt_optimization(content_to_extract):
    """Reinforcement learning loop to optimize the prompt for a given content."""
    epsilon = EPSILON_START
    best_prompt = generate_initial_prompt(content_to_extract)
    best_score = np.mean(get_three_valid_scores(best_prompt)[0])  # Get only scores
    best_prompts = []  # List to store all prompts with the best score
    best_extracted_prompts = []  # List to store all extracted prompts with the best score

    for episode in range(NUM_EPISODES):
        current_prompt = generate_initial_prompt(content_to_extract)
        state = get_state(current_prompt)

        for step in range(MAX_STEPS_PER_EPISODE):
            # Choose action
            action = choose_action(state, epsilon)

            # Get scores and suggestions
            scores, suggestions = get_three_valid_scores(current_prompt)
            reward = np.mean(scores)

            # Modify prompt using action and suggestions
            new_prompt = modify_prompt(current_prompt, action, content_to_extract, suggestions)
            next_state = get_state(new_prompt)

            # Store experience in replay memory
            replay_memory.append((state, action, reward, next_state))

            # Update DQN
            update_dqn()

            if reward > best_score:
                best_score = reward
                best_prompt = new_prompt
                best_prompts = [new_prompt]  # 重置为新的最佳提示
                best_extracted_prompts = [new_prompt]  # 重置为新的最佳提取提示
            elif reward == best_score:
                if new_prompt not in best_prompts:  # 避免重复添加
                    best_prompts.append(new_prompt)  # 添加到最佳提示列表
                    best_extracted_prompts.append(new_prompt)  # 添加到最佳提取提示列表

            # Move to next state
            current_prompt = new_prompt
            state = next_state

            # Decay epsilon
            epsilon = max(EPSILON_END, epsilon * EPSILON_DECAY)

            print(f"Episode {episode + 1}, Step {step + 1}: Score = {reward}, Best Score = {best_score}")

    return best_prompt, best_score, best_extracted_prompts  # 返回提取的 prompt


if __name__ == '__main__':
    # Define the content to extract (can be customized for different tasks)
    content_to_extract = "Cell total volume"

    # Run RL-based prompt optimization
    best_prompt, best_score, best_extracted_prompts = rl_prompt_optimization(content_to_extract)
    print(f"Optimized Prompt: {best_prompt}")
    print(f"Best Score: {best_score}")

    # Vote for the best prompt among all best prompts (including non-perfect scores)
    if best_extracted_prompts:
        print("Best extracted prompts before voting:", best_extracted_prompts)
        final_best_prompt = vote_for_best_prompt(best_extracted_prompts)
        print(f"The best prompt selected by voting is: {final_best_prompt}")
    else:
        print("No best prompts were recorded during RL optimization.")
        print("The best prompt selected by voting is: \n", best_prompt)