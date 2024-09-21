# coding=utf-8
#
# Installation instructions for pyaudio:
# APPLE Mac OS X
#   brew install portaudio
#   pip install pyaudio
# Debian/Ubuntu
#   sudo apt-get install python-pyaudio python3-pyaudio
#   or
#   pip install pyaudio
# CentOS
#   sudo yum install -y portaudio portaudio-devel && pip install pyaudio
# Microsoft Windows
#   python -m pip install pyaudio

import nls
import time
import os

# 设置打开日志输出
nls.enableTrace(False)

# 将音频保存进文件
SAVE_TO_FILE = True
# 将音频通过播放器实时播放，需要具有声卡。在服务器上运行请将此开关关闭
PLAY_REALTIME_RESULT = True
if PLAY_REALTIME_RESULT:
    import pyaudio

test_text = [
    "流式文本语音合成SDK，",
    "可以将输入的文本",
    "合成为语音二进制数据，",
    "相比于非流式语音合成，",
    "流式合成的优势在于实时性",
    "更强。用户在输入文本的同时",
    "可以听到接近同步的语音输出，",
    "极大地提升了交互体验，",
    "减少了用户等待时间。",
    "适用于调用大规模",
    "语言模型（LLM），以",
    "流式输入文本的方式",
    "进行语音合成的场景。",
]

if __name__ == "__main__":
    if SAVE_TO_FILE:
        file = open("output.wav", "wb")
    if PLAY_REALTIME_RESULT:
        player = pyaudio.PyAudio()
        stream = player.open(
            format=pyaudio.paInt16, channels=1, rate=24000, output=True
        )

    # 创建SDK实例
    # 配置回调函数
    def test_on_data(data, *args):
        if SAVE_TO_FILE:
            file.write(data)
        if PLAY_REALTIME_RESULT:
            stream.write(data)

    def test_on_message(message, *args):
        print("on message=>{}".format(message))

    def test_on_close(*args):
        print("on_close: args=>{}".format(args))

    def test_on_error(message, *args):
        print("on_error message=>{} args=>{}".format(message, args))

    sdk = nls.NlsStreamInputTtsSynthesizer(
        # 由于目前阶段大模型音色只在北京地区服务可用，因此需要调整url到北京
        url="wss://nls-gateway-cn-beijing.aliyuncs.com/ws/v1",
        token=os.getenv("NLS_TOKEN"),
        appkey=os.getenv("NLS_APP_ID"),
        on_data=test_on_data,
        on_sentence_begin=test_on_message,
        on_sentence_synthesis=test_on_message,
        on_sentence_end=test_on_message,
        on_completed=test_on_message,
        on_error=test_on_error,
        on_close=test_on_close,
        callback_args=[],
    )

    # 发送文本消息
    sdk.startStreamInputTts(
        voice="longxiaochun",       # 语音合成说话人
        aformat="wav",              # 合成音频格式
        sample_rate=24000,          # 合成音频采样率
        volume=50,                  # 合成音频的音量
        speech_rate=0,              # 合成音频语速
        pitch_rate=0,               # 合成音频的音调
    )
    for text in test_text:
        sdk.sendStreamInputTts(text)
        time.sleep(0.05)
    sdk.stopStreamInputTts()
    if SAVE_TO_FILE:
        file.close()
    if PLAY_REALTIME_RESULT:
        stream.stop_stream()
        stream.close()
        player.terminate()