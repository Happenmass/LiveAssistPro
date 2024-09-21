import dotenv
dotenv.load_dotenv()
import multiprocessing as mp
import time
import numpy as np
import sounddevice as sd
from collections import deque
import keyboard
from PIL import ImageGrab  # 用于截屏
import os
from cosyvoice_utils import cosyvoice
from dify_utils import extractor_images_content, play_huxianfeng_role, play_huxianfeng_role_novision
from threading import Thread
from cosyvoice_stream.tools import create_sdk, create_stream_generate
import pyaudio
import sys

dot_list= ["？", "！", "，", "。"]

def custom_excepthook(exctype, value, tb):
    print(f"Unhandled exception: {value}")

sys.excepthook = custom_excepthook

def play_text(text_queue):
    player = pyaudio.PyAudio()
    stream = player.open(
        format=pyaudio.paInt16, channels=1, rate=22050, output=True
    )

    time.sleep(0.01)
    while True:
        try:
            if not text_queue.empty():
                create_stream_generate(text_queue, stream)
            time.sleep(0.01)
        except KeyboardInterrupt:
            print("Stopping...")
            break
    
    stream.stop_stream()
    stream.close()
    player.terminate()

def glm_response(asr_queue, text_queue, shared_string):
    while True:
        try:
            if not asr_queue.empty():
                ars_text = asr_queue.get()
                text_buffer = deque(maxlen=200)  # 创建一个有限大小的缓冲区

                # text = extractor_images_content(ars_text)
                # print(text)
                text_iter = play_huxianfeng_role(ars_text, shared_string.value)
                
                for chunk in text_iter:
                    content = chunk.choices[0].delta.content
                    text_buffer.append(content)
                    if content in dot_list:

                        text_string = ""
                        if len(text_buffer) > 10:
                            while len(text_buffer) > 0:
                                text_string += text_buffer.popleft()
                        if text_string != "":
                            text_queue.put(text_string)
                time.sleep(1.0)  # 防止多次触发
            time.sleep(0.01)
        except Exception as e:
            print(e)

def start_listen(asr_queue):
    from vad.pipe import webrtcvad, transcribe_audio, create_model, CHUNK_DURATION_MS, FORMAT, CHANNELS, RATE, CHUNK, collections
    # VAD参数
    VAD_MODE = 3  # 0-3, 0最为敏感
    vad = webrtcvad.Vad(VAD_MODE)

    # 音频缓冲区配置
    num_padding_chunks = int(300 / CHUNK_DURATION_MS)  # 用户停止说话后保留的音频段数，300ms的语音段
    buffer_max_len = 10 * num_padding_chunks  # 最大缓冲区大小

    audio = pyaudio.PyAudio()

    stream = audio.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)

    buffer = collections.deque(maxlen=buffer_max_len)
    triggered = False
    voiced_frames = []

    m, kwargs = create_model()

    print("Listening... Press Ctrl+C to stop.")

    try:
        while True:
            chunk = stream.read(CHUNK)
            is_speech = vad.is_speech(chunk, RATE)
            if not triggered:
                buffer.append(chunk)
                if is_speech:
                    triggered = True
                    voiced_frames.extend(buffer)
                    buffer.clear()
            else:
                voiced_frames.append(chunk)
                if not is_speech:
                    if num_padding_chunks > 0:
                        num_padding_chunks -= 1
                    else:
                        triggered = False
                        num_padding_chunks = int(300 / CHUNK_DURATION_MS)

                        print("Processing...")
                        # 将检测到的语音段保存或发送到ASR
                        # save_wav("detected_speech.wav", voiced_frames)
                        res = transcribe_audio(voiced_frames, m, **kwargs)
                        print(res)
                        try:
                            if len(res[0]['clean_text']) >= 5:
                                asr_queue.put(res[0]['clean_text'])
                        except:
                            pass
                        # 清除缓存
                        voiced_frames = []

            time.sleep(0.01)

    except KeyboardInterrupt:
        print("Stopping...")
    
    finally:
        stream.stop_stream()
        stream.close()
        audio.terminate()

def update_shared_string(shared_string):
    while True:
        screenshot = ImageGrab.grab()
        screenshot = screenshot.resize((1280, 720))
        text = extractor_images_content(screenshot)
        new_value = text
        shared_string.value = new_value
        print(f"Shared String updated to: {shared_string.value}")
        time.sleep(int(os.getenv("SCREEN_READ_FREQ")))  # 每隔1分钟更新一次

def main():
    # 创建队列和进程
    manager = mp.Manager()
    shared_string = manager.Value('c', 'Initial Value')
    
    asr_queue = mp.Queue()
    text_queue = mp.Queue()

    asr_process = mp.Process(target=start_listen, args=(asr_queue,))
    tts_process = mp.Process(target=play_text, args=(text_queue,))
    glm_process = mp.Process(target=glm_response, args=(asr_queue,text_queue,shared_string, ))
    screenshot_process = mp.Process(target=update_shared_string, args=(shared_string,))

    asr_process.start()
    tts_process.start()
    glm_process.start()
    screenshot_process.start()

    asr_process.join()
    tts_process.join()
    glm_process.join()
    screenshot_process.join()

if __name__ == "__main__":
    main()
