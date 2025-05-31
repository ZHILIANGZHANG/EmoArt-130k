import torch
from PIL import Image
from transformers import AutoModel, AutoTokenizer
from peft import PeftModel
import json
import os
from tqdm import tqdm

# 严格使用您提供的原始问题
QUESTIONS = [
    "Describe the brushstroke of this painting.",
    "Describe the color characteristics of this painting.",
    "Describe the composition of this painting.",
    "Describe the use of light and shadow in this painting.",
    "Describe the line quality of this painting."
]

def load_model():
    model = AutoModel.from_pretrained(
        "/root/autodl-tmp/models/modelscope/models/OpenBMB/MiniCPM-V-2_6",
        trust_remote_code=True,
        torch_dtype=torch.bfloat16
    ).eval().cuda()
    
    model = PeftModel.from_pretrained(
        model,
        "/root/autodl-tmp/LLaMA-Factory/saves/MiniCPM-V-2_6/lora/Attributes/checkpoint-900"
    )
    tokenizer = AutoTokenizer.from_pretrained(
        "/root/autodl-tmp/models/modelscope/models/OpenBMB/MiniCPM-V-2_6",
        trust_remote_code=True
    )
    return model, tokenizer

def analyze_single_image(model, tokenizer, img_path):
    """完全独立的五轮提问，无任何上下文干扰"""
    img_name = os.path.splitext(os.path.basename(img_path))[0]
    results = {}
    
    try:
        # 第一问：笔触
        img = Image.open(img_path).convert("RGB")
        msgs = [{"role": "user", "content": [img, QUESTIONS[0]]}]
        results["brushstroke"] = model.chat(image=None, msgs=msgs, tokenizer=tokenizer).strip()
        
        # 第二问：色彩（全新会话）
        img = Image.open(img_path).convert("RGB")
        msgs = [{"role": "user", "content": [img, QUESTIONS[1]]}]
        results["color"] = model.chat(image=None, msgs=msgs, tokenizer=tokenizer).strip()
        
        # 第三问：构图（全新会话）
        img = Image.open(img_path).convert("RGB")
        msgs = [{"role": "user", "content": [img, QUESTIONS[2]]}]
        results["composition"] = model.chat(image=None, msgs=msgs, tokenizer=tokenizer).strip()
        
        # 第四问：光影（全新会话）
        img = Image.open(img_path).convert("RGB")
        msgs = [{"role": "user", "content": [img, QUESTIONS[3]]}]
        results["light_and_shadow"] = model.chat(image=None, msgs=msgs, tokenizer=tokenizer).strip()
        
        # 第五问：线条（全新会话）
        img = Image.open(img_path).convert("RGB")
        msgs = [{"role": "user", "content": [img, QUESTIONS[4]]}]
        results["line_quality"] = model.chat(image=None, msgs=msgs, tokenizer=tokenizer).strip()
        
    except Exception as e:
        print(f"Error processing {img_name}: {str(e)}")
        return None
    
    return {img_name: results}

def process_all_images(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    model, tokenizer = load_model()
    
    for folder in os.listdir(input_dir):
        folder_path = os.path.join(input_dir, folder)
        if not os.path.isdir(folder_path):
            continue
            
        all_results = {}
        png_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.png')]
        
        for img_file in tqdm(png_files, desc=f"Processing {folder}"):
            img_path = os.path.join(folder_path, img_file)
            result = analyze_single_image(model, tokenizer, img_path)
            if result:
                all_results.update(result)
        
        output_path = os.path.join(output_dir, f"{folder}.json")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False)
        
        print(f"Saved {len(all_results)} results to {output_path}")

if __name__ == "__main__":
    process_all_images(
        input_dir="flux-dev",
        output_dir="flux-dev-attributes"
    )
