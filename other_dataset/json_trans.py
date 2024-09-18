import json
from collections import defaultdict

def ground_truth_to_ner_format(ground_truth_file):
    sentences = defaultdict(lambda: {"sentence": "", "entity": [], "category": []})
    current_sentence = []
    current_entity = []
    current_category = None
    sentence_counter = 1

    with open(ground_truth_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip() == "":
                if current_entity:
                    sentences[f"sentence{sentence_counter}"]["entity"].append(" ".join(current_entity))
                    sentences[f"sentence{sentence_counter}"]["category"].append(current_category)
                    current_entity = []
                sentences[f"sentence{sentence_counter}"]["sentence"] = " ".join(current_sentence).strip()
                current_sentence = []
                sentence_counter += 1
            else:
                word, label = line.strip().split()
                current_sentence.append(word)
                if label.startswith("B-"):
                    if current_entity:
                        sentences[f"sentence{sentence_counter}"]["entity"].append(" ".join(current_entity))
                        sentences[f"sentence{sentence_counter}"]["category"].append(current_category)
                        current_entity = []
                    current_entity.append(word)
                    current_category = label[2:]
                elif label.startswith("I-"):
                    current_entity.append(word)
                elif label == "O":
                    if current_entity:
                        sentences[f"sentence{sentence_counter}"]["entity"].append(" ".join(current_entity))
                        sentences[f"sentence{sentence_counter}"]["category"].append(current_category)
                        current_entity = []

    if current_entity:
        sentences[f"sentence{sentence_counter}"]["entity"].append(" ".join(current_entity))
        sentences[f"sentence{sentence_counter}"]["category"].append(current_category)
        sentences[f"sentence{sentence_counter}"]["sentence"] = " ".join(current_sentence).strip()

    return dict(sentences)

def save_as_json(data, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    ground_truth_file = "input_path/ground_truth.txt"
    ner_data = ground_truth_to_ner_format(ground_truth_file)
    output_file = "output_path/ner_output.json"
    save_as_json(ner_data, output_file)
    print("success:", output_file)

