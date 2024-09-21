import nls
import time
import multiprocessing as mp
import pyaudio
import os

def create_sdk(stream):
    # 创建SDK实例
    # 配置回调函数
    def test_on_data(data, *args):
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

    return sdk

def create_stream_generate(text_queue, stream):
    try: 
        sdk = create_sdk(stream)

        # 发送文本消息
        sdk.startStreamInputTts(
            voice="cosyvoice-huxianfeng-c28d85c",       # 语音合成说话人
            aformat="wav",              # 合成音频格式
            sample_rate=22050,          # 合成音频采样率
            volume=80,                  # 合成音频的音量
            speech_rate=0,              # 合成音频语速
            pitch_rate=-100,               # 合成音频的音调
        )
        
        time.sleep(0.01)
        
        while not text_queue.empty():
            text = text_queue.get()
            print("tts: ", text)
            if not text == "":
                sdk.sendStreamInputTts(text)
            time.sleep(0.05)
            
        sdk.stopStreamInputTts()
    except Exception as e:
        print(e)


if __name__ == "__main__":
    text_queue = mp.Queue()
    text_queue.put("你好")

    player = pyaudio.PyAudio()
    stream = player.open(
        format=pyaudio.paInt16, channels=1, rate=22050, output=True
    )

    sdk = create_sdk(stream)

    time.sleep(0.01)
    while True:
        try:
            if not text_queue.empty():
                create_stream_generate(sdk, text_queue)
            time.sleep(0.01)
        except KeyboardInterrupt:
            print("Stopping...")
            break
    
    stream.stop_stream()
    stream.close()
    player.terminate()