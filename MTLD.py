import json
import re
from typing import List, Tuple
from statistics import mean


def calculate_mtld(text: str, threshold: float = 0.72) -> Tuple[float, float, float]:
    """
    计算英文文本的 MTLD（Measure of Textual Lexical Diversity），
    并返回正向、反向及平均 MTLD 值。

    参数:
        text (str): 输入的英文文本
        threshold (float): TTR 阈值（默认 0.72）

    返回:
        Tuple[float, float, float]: (正向 MTLD, 反向 MTLD, 平均 MTLD)
        如果文本为空，返回 (0.0, 0.0, 0.0)
    """
    words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
    if not words:
        return 0.0, 0.0, 0.0

    def compute_factors(word_list: List[str]) -> float:
        factors = 0.0
        start_idx = 0
        unique_words = set()

        for i in range(len(word_list)):
            unique_words.add(word_list[i])
            current_ttr = len(unique_words) / (i - start_idx + 1)

            if current_ttr < threshold:
                factors += 1
                start_idx = i + 1
                unique_words = set()

        remaining_length = len(word_list) - start_idx
        if remaining_length > 0:
            remaining_ttr = len(unique_words) / remaining_length
            factors += (1 - remaining_ttr) / (1 - threshold)

        return factors

    forward_factors = compute_factors(words)
    reverse_factors = compute_factors(words[::-1])

    mtld_forward = len(words) / forward_factors if forward_factors > 0 else 0.0
    mtld_reverse = len(words) / reverse_factors if reverse_factors > 0 else 0.0

    if mtld_forward == 0.0 or mtld_reverse == 0.0:
        mtld_avg = max(mtld_forward, mtld_reverse)
    else:
        mtld_avg = (mtld_forward + mtld_reverse) / 2

    return mtld_forward, mtld_reverse, mtld_avg


def process_json_mtld(json_file_path: str) -> dict:
    """
    读取JSON文件，计算每个条目中description及五种画面属性的MTLD，并返回平均值

    参数:
        json_file_path (str): JSON文件路径

    返回:
        dict: 包含description及五种画面属性的平均MTLD（正向、反向、平均）
    """
    # 存储每个字段的MTLD值（forward, reverse, avg）
    mtld_data = {
        'description': {'forward': [], 'reverse': [], 'avg': []},
        'brushstroke': {'forward': [], 'reverse': [], 'avg': []},
        'color': {'forward': [], 'reverse': [], 'avg': []},
        'composition': {'forward': [], 'reverse': [], 'avg': []},
        'light_and_shadow': {'forward': [], 'reverse': [], 'avg': []},
        'line_quality': {'forward': [], 'reverse': [], 'avg': []}
    }

    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        for entry in data:
            try:
                desc_text = entry['description']['first_section']['description']
                forward, reverse, avg = calculate_mtld(desc_text)
                mtld_data['description']['forward'].append(forward)
                mtld_data['description']['reverse'].append(reverse)
                mtld_data['description']['avg'].append(avg)

                visual_attrs = entry['description']['second_section']['visual_attributes']
                for attr in ['brushstroke', 'color', 'composition', 'light_and_shadow', 'line_quality']:
                    attr_text = visual_attrs.get(attr, '')
                    forward, reverse, avg = calculate_mtld(attr_text)
                    mtld_data[attr]['forward'].append(forward)
                    mtld_data[attr]['reverse'].append(reverse)
                    mtld_data[attr]['avg'].append(avg)

            except KeyError as e:
                print(f"警告: 条目缺少字段 {e}，跳过该条目")
                continue

        # 计算每个字段的平均MTLD
        avg_mtld = {}
        for field in mtld_data:
            avg_mtld[field] = {
                'forward': mean(mtld_data[field]['forward']) if mtld_data[field]['forward'] else 0.0,
                'reverse': mean(mtld_data[field]['reverse']) if mtld_data[field]['reverse'] else 0.0,
                'avg': mean(mtld_data[field]['avg']) if mtld_data[field]['avg'] else 0.0
            }
            if not mtld_data[field]['forward']:
                print(f"警告: 字段 {field} 没有有效数据，平均MTLD设为0.0")

        return avg_mtld

    except FileNotFoundError:
        print(f"错误: 文件 {json_file_path} 未找到")
        return {}
    except json.JSONDecodeError:
        print(f"错误: 文件 {json_file_path} 不是有效的JSON格式")
        return {}


if __name__ == "__main__":
    json_file_path = r'D:\Openai_api\data.json'  # Update to your actual JSON file path
    avg_mtld_results = process_json_mtld(json_file_path)
    print(f"avg_mtld_results type: {type(avg_mtld_results)}, value: {avg_mtld_results}")
    if isinstance(avg_mtld_results, dict) and avg_mtld_results:
        print("各字段的平均MTLD值:")
        for field, mtld in avg_mtld_results.items():
            print(f"{field}:")
            print(f"  正向 MTLD: {mtld['forward']:.2f}")
            print(f"  反向 MTLD: {mtld['reverse']:.2f}")
            print(f"  平均 MTLD: {mtld['avg']:.2f}")
    else:
        print("错误: 无法计算MTLD，检查JSON文件或路径")