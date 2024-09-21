import requests
import PIL
import json
import io
import base64
from zhipuai import ZhipuAI
import os

client = ZhipuAI(api_key=os.getenv("ZHIPU_KEY")) # 请填写您自己的APIKey


# uoload Image with multipart/form-data
def convert_to_base64(image: PIL.Image.Image):
    # 创建一个字节流来保存图像
    img_byte_arr = io.BytesIO()
    # 保存图像到字节流（PNG格式）
    image.save(img_byte_arr, format='PNG')
    # 获取字节流的字节数据
    img_byte_arr = img_byte_arr.getvalue()
    # 对字节数据进行 base64 编码
    base64_encoded = base64.b64encode(img_byte_arr)
    # 将编码结果转换为字符串
    return "data:image/png;base64,"+ base64_encoded.decode('utf-8')

def extractor_images_content(image: PIL.Image.Image):
    image.save("test.png", format='PNG')
    response = client.chat.completions.create(
        model="glm-4v",  # 填写需要调用的模型名称
        messages=[
            {"role": "user",
            "content": [
            {
                "type": "text",
                "text": os.getenv("SCREEN_ANALYSIS_TEMP")
            },
            {
                "type": "image_url",
                "image_url": {
                    "url" : convert_to_base64(image)
                }
            }
            ]
            },
        ],
        stream=False,
    )

    return response.choices[0].message.content


def play_huxianfeng_role(player_text:str, env_description:str, danmu: str = "无"):
    
    response = client.chat.completions.create(
        model=os.getenv("GLM_MODEL"),  # 填写需要调用的模型编码
        messages=[
                {"role": "system", "content": os.getenv("ROLE_PLAY_TEMP")},
                {"role": "user", "content": f"主播说：{player_text}\n场景描述：{env_description}\n观众弹幕：{danmu}"},
            ],
            stream=True,
    )

    return response

def play_huxianfeng_role_novision(player_text:str, env_description:str, danmu: str = "无"):
    response = client.chat.completions.create(
        model=os.getenv("GLM_MODEL"),  # 填写需要调用的模型编码
        messages=[
                {"role": "system", "content": os.getenv("ROLE_PLAY_TEMP_NO_VISION")},
                {"role": "user", "content": f"主播说：{player_text}\n 观众弹幕：{danmu}"},
            ],
            stream=True,
    )

    return response
