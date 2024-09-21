import requests
import logging
import numpy as np

import os
import json
import time

import nls


def saveResponse(path, response):
    # 以二进制写入模式打开文件
    with open(path, 'wb') as file:
        # 将响应的二进制内容写入文件
        file.write(response.content)

def read_response_to_numpy(response):
    # 将二进制内容转换为numpy数组
    return np.frombuffer(response.content, np.float32)

def cosyvoice(api: str, mode: str, prompt_text:str, prompt_wav:str, tts_text:str="你好，我是cosyvoice", tts_wav:str="output.wav", spk_id:str="中文女", instruct_text:str=""):
    if mode == 'sft':
        url = api + "/api/inference/sft"
        payload={
            'tts': tts_text,
            'role': spk_id
        }
        response = requests.request("POST", url, data=payload)
        return read_response_to_numpy(response)
    elif mode == 'zero_shot':
        url = api + "/api/inference/zero-shot"
        payload={
            'tts': tts_text,
            'prompt': prompt_text
        }
        files=[('audio', ('prompt_audio.wav', open(prompt_wav,'rb'), 'application/octet-stream'))]
        response = requests.request("POST", url, data=payload, files=files)
        return read_response_to_numpy(response)

    elif mode == 'cross_lingual':
        url = api + "/api/inference/cross-lingual"
        payload={
            'tts': tts_text,
        }
        files=[('audio', ('prompt_audio.wav', open(prompt_wav,'rb'), 'application/octet-stream'))]
        response = requests.request("POST", url, data=payload, files=files)
        return read_response_to_numpy(response)

    else:
        url = api + "/api/inference/instruct"
        payload = {
            'tts': tts_text,
            'role': spk_id,
            'instruct': instruct_text
        }
        response = requests.request("POST", url, data=payload)
        return read_response_to_numpy(response)

    logging.info("Response save to {}", tts_wav)
