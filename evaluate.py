import json
import warnings
from sklearn.metrics import precision_score, recall_score, f1_score
from sklearn.preprocessing import MultiLabelBinarizer

warnings.filterwarnings("ignore")

def extract_entities(entities):
    return set([entity.lower() for entity in entities])

def calculate_entity_metrics(true_data, pred_data):
    true_entities = []
    pred_entities = []

    common_sentences = set(true_data.keys()).intersection(set(pred_data.keys()))
    
    for sentence in common_sentences:
        true_entities.append(extract_entities(true_data[sentence]['entity']))
        pred_entities.append(extract_entities(pred_data[sentence]['entity']))

    mlb = MultiLabelBinarizer()
    y_true = mlb.fit_transform(true_entities)
    y_pred = mlb.transform(pred_entities)

    precision_entity = precision_score(y_true, y_pred, average='micro')
    recall_entity = recall_score(y_true, y_pred, average='micro')
    f1_entity = f1_score(y_true, y_pred, average='micro')
    
    return precision_entity, recall_entity, f1_entity

def calculate_metrics(true_data, pred_data):
    true_entities_with_categories = []
    pred_entities_with_categories = []
    
    common_sentences = set(true_data.keys()).intersection(set(pred_data.keys()))
    
    for sentence in common_sentences:
        true_entities_with_categories.append(
            set((entity.lower(), category.lower()) for entity, category in zip(true_data[sentence]['entity'], true_data[sentence]['category']))
        )
        pred_entities_with_categories.append(
            set((entity.lower(), category.lower()) for entity, category in zip(pred_data[sentence]['entity'], pred_data[sentence]['category']))
        )

    mlb = MultiLabelBinarizer()
    y_true = mlb.fit_transform(true_entities_with_categories)
    y_pred = mlb.transform(pred_entities_with_categories)

    precision = precision_score(y_true, y_pred, average='micro')
    recall = recall_score(y_true, y_pred, average='micro')
    f1 = f1_score(y_true, y_pred, average='micro')
    
    return precision, recall, f1

def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def main(ground_truth_path, predict_path):
    ground_truth = load_json(ground_truth_path)
    predict = load_json(predict_path)

    precision, recall, f1 = calculate_metrics(ground_truth, predict)
    precision_entity, recall_entity, f1_entity = calculate_entity_metrics(ground_truth, predict)

    print(f"Overall Precision (Entity + Category): {precision:.4f}")
    print(f"Overall Recall (Entity + Category): {recall:.4f}")
    print(f"Overall F1 Score (Entity + Category): {f1:.4f}")
    print(f"Entity-level Precision: {precision_entity:.4f}")
    print(f"Entity-level Recall: {recall_entity:.4f}")
    print(f"Entity-level F1 Score: {f1_entity:.4f}")

if __name__ == "__main__":
    ground_truth_path = 'path/to/ground_truth.json'
    predict_path = 'path/to/predictions.json'
    main(ground_truth_path, predict_path)

