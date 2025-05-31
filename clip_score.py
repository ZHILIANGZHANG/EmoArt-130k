import torch
from PIL import Image
import clip
from torchvision import transforms
import os

def calculate_clip_score(images, texts, model_path="./clip_model"):
    """
    计算图像和文本之间的CLIP Score
    参数:
    images: 图像路径列表或单张图像路径
    texts: 文本描述列表或单个文本
    model_path: 预训练模型保存路径
    """
    # 确保模型路径存在
    if not os.path.exists(model_path):
        os.makedirs(model_path)

    # 加载CLIP模型（指定下载路径）
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, preprocess = clip.load("ViT-B/32", device=device, download_root=model_path)

    # 处理输入格式
    if isinstance(images, str):
        images = [images]
    if isinstance(texts, str):
        texts = [texts]

    # 预处理图像
    image_tensors = []
    for image_path in images:
        image = Image.open(image_path).convert("RGB")
        image_tensor = preprocess(image).unsqueeze(0).to(device)
        image_tensors.append(image_tensor)
    image_tensors = torch.cat(image_tensors)

    # 预处理文本
    text_tokens = clip.tokenize(texts).to(device)

    # 计算特征
    with torch.no_grad():
        image_features = model.encode_image(image_tensors)
        text_features = model.encode_text(text_tokens)

        # 归一化特征
        image_features = image_features / image_features.norm(dim=-1, keepdim=True)
        text_features = text_features / text_features.norm(dim=-1, keepdim=True)

        # 计算余弦相似度
        similarity = (image_features @ text_features.T) * 100  # 乘以100得到百分比形式

    # 返回平均CLIP Score
    clip_scores = similarity.diag().cpu().numpy()
    return clip_scores.mean() if len(clip_scores) > 1 else clip_scores.item()

# 使用示例
if __name__ == "__main__":
    # 指定图像和文本
    image_paths = ["example_image.jpg"]
    text_descriptions = ["A beautiful sunset over the ocean"]

    # 指定模型保存路径
    custom_model_path = "./clip_model"

    # 计算CLIP Score
    score = calculate_clip_score(image_paths, text_descriptions, custom_model_path)
    print(f"CLIP Score: {score:.2f}")