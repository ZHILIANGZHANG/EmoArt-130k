import json
import re
import math
from collections import Counter
from statistics import mean


def calculate_shannon_entropy(text):
    """
    计算英文文本的Shannon熵

    参数:
    text (str): 要分析的英文文本

    返回:
    float: Shannon熵值（以bits为单位）
    int: 不同单词数量
    int: 总单词数量
    """
    words = re.findall(r'\b[a-zA-Z]+\b', text.lower())

    if not words:
        return 0.0, 0, 0

    total_words = len(words)
    word_counts = Counter(words)

    entropy = 0.0
    for count in word_counts.values():
        probability = count / total_words
        entropy -= probability * math.log2(probability)

    return entropy, len(word_counts), total_words


def process_json_entropy(json_file_path: str) -> dict:
    """
    读取JSON文件，计算每个条目中description及五种画面属性的Shannon熵，并返回平均值

    参数:
        json_file_path (str): JSON文件路径

    返回:
        dict: 包含description及五种画面属性的平均熵值
    """
    entropy_data = {
        'description': [],
        'brushstroke': [],
        'color': [],
        'composition': [],
        'light_and_shadow': [],
        'line_quality': []
    }

    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        for entry in data:
            try:
                desc_text = entry['description']['first_section']['description']
                entropy, _, _ = calculate_shannon_entropy(desc_text)
                entropy_data['description'].append(entropy)

                visual_attrs = entry['description']['second_section']['visual_attributes']
                for attr in ['brushstroke', 'color', 'composition', 'light_and_shadow', 'line_quality']:
                    attr_text = visual_attrs.get(attr, '')
                    entropy, _, _ = calculate_shannon_entropy(attr_text)
                    entropy_data[attr].append(entropy)

            except KeyError as e:
                print(f"警告: 条目缺少字段 {e}，跳过该条目")
                continue

        avg_entropy = {}
        for field, entropy_list in entropy_data.items():
            if entropy_list:
                avg_entropy[field] = mean(entropy_list)
            else:
                avg_entropy[field] = 0.0
                print(f"警告: 字段 {field} 没有有效数据，平均熵设为0.0")

        return avg_entropy

    except FileNotFoundError:
        print(f"错误: 文件 {json_file_path} 未找到")
        return {}
    except json.JSONDecodeError:
        print(f"错误: 文件 {json_file_path} 不是有效的JSON格式")
        return {}


if __name__ == "__main__":
    json_file_path = r'D:\Openai_api\data.json'  # Update to your actual JSON file path
    avg_entropy_results = process_json_entropy(json_file_path)
    print(f"avg_entropy_results type: {type(avg_entropy_results)}, value: {avg_entropy_results}")
    if isinstance(avg_entropy_results, dict) and avg_entropy_results:
        print("各字段的平均Shannon熵值:")
        for field, entropy in avg_entropy_results.items():
            print(f"{field}: {entropy:.4f} bits")
    else:
        print("错误: 无法计算Shannon熵，检查JSON文件或路径")