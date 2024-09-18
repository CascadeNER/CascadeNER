import json
import random
from collections import defaultdict

def count_assistant_values(data):
    value_counts = defaultdict(int)
    for i in range(1, len(data), 2):
        assistant_value = data[i]["conversations"][1]["value"]
        value_counts[assistant_value] += 1
    return value_counts

def uniform_sample_conversations(data, sample_size):
    value_counts = count_assistant_values(data)
    value_index = defaultdict(list)
    for i in range(1, len(data), 2):
        assistant_value = data[i]["conversations"][1]["value"]
        value_index[assistant_value].append(i)

    sampled_data = []
    unique_values = len(value_index)
    target_count = min(sample_size // unique_values, min(len(indices) for indices in value_index.values()))

    for value, indices in value_index.items():
        random.shuffle(indices)
        num_samples = min(target_count, len(indices))
        for idx in indices[:num_samples]:
            sampled_data.append(data[idx - 1])
            sampled_data.append(data[idx])

    return sampled_data

def read_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def write_json_file(data, output_path):
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def main(input_file, output_file, sample_size):
    data = read_json_file(input_file)
    sampled_data = uniform_sample_conversations(data, sample_size)
    write_json_file(sampled_data, output_file)
    print(f"Uniform sampling completed and saved to {output_file}, sample size: {sample_size}")

if __name__ == "__main__":
    input_file = "input_path/test3.json"
    output_file = "output_path/test_sampled.json"
    sample_size = 3000
    main(input_file, output_file, sample_size)
