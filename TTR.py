import json
import re
from collections import Counter
from statistics import mean


def calculate_ttr(text):
    """
    计算英文文本的TTR（Type-Token Ratio）

    参数:
    text (str): 要分析的英文文本

    返回:
    float: TTR值
    int: 不同单词数量（types）
    int: 总单词数量（tokens）
    """
    words = re.findall(r'\b[a-zA-Z]+\b', text.lower())

    if not words:
        return 0.0, 0, 0

    token_count = len(words)
    type_count = len(Counter(words))
    ttr = type_count / token_count

    return ttr, type_count, token_count


def process_json_ttr(json_file_path):
    """
    读取JSON文件，计算每个条目中description及五种画面属性的TTR，并返回平均值

    参数:
    json_file_path (str): JSON文件路径

    返回:
    dict: 包含description及五种画面属性的平均TTR
    """
    ttr_data = {
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
                ttr_desc, _, _ = calculate_ttr(desc_text)
                ttr_data['description'].append(ttr_desc)

                visual_attrs = entry['description']['second_section']['visual_attributes']
                for attr in ['brushstroke', 'color', 'composition', 'light_and_shadow', 'line_quality']:
                    attr_text = visual_attrs.get(attr, '')
                    ttr_attr, _, _ = calculate_ttr(attr_text)
                    ttr_data[attr].append(ttr_attr)

            except KeyError as e:
                print(f"警告: 条目缺少字段 {e}，跳过该条目")
                continue

        avg_ttr = {}
        for field, ttr_list in ttr_data.items():
            if ttr_list:
                avg_ttr[field] = mean(ttr_list)
            else:
                avg_ttr[field] = 0.0
                print(f"警告: 字段 {field} 没有有效数据，平均TTR设为0.0")

        return avg_ttr

    except FileNotFoundError:
        print(f"错误: 文件 {json_file_path} 未找到")
        return {}
    except json.JSONDecodeError:
        print(f"错误: 文件 {json_file_path} 不是有效的JSON格式")
        return {}


if __name__ == "__main__":
    json_file_path = "E:\Annotation\Abstract Art.json" # Update to your actual JSON file path
    avg_ttr_results = process_json_ttr(json_file_path)
    print(f"avg_ttr_results type: {type(avg_ttr_results)}, value: {avg_ttr_results}")
    if isinstance(avg_ttr_results, dict) and avg_ttr_results:
        print("各字段的平均TTR值:")
        for field, ttr in avg_ttr_results.items():
            print(f"{field}: {ttr:.4f}")
    else:
        print("错误: 无法计算TTR，检查JSON文件或路径")