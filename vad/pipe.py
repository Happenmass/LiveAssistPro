import pyaudio
import wave
import webrtcvad
import collections
import time
import io
import struct
from vad.model import SenseVoiceSmall
import torchaudio
import re
import os

regex = r"<\|.*\|>"

# 配置参数
RATE = 16000  # 采样率
CHUNK_DURATION_MS = 30    # 每个chunk的时长，10ms, 20ms或30ms
CHUNK = int(RATE * CHUNK_DURATION_MS / 1000)  # 每个chunk的帧数
FORMAT = pyaudio.paInt16
CHANNELS = 1


def create_model():
    model_dir = "iic/SenseVoiceSmall"
    m, kwargs = SenseVoiceSmall.from_pretrained(model=model_dir, device="cuda:"+str(os.getenv("VAD_DEVICE", 0)))
    m.eval()
    return m, kwargs

def save_wav(file_name, audio_data):
    with wave.open(file_name, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(2)
        wf.setframerate(RATE)
        wf.writeframes(b''.join(audio_data))

def transcribe_audio(audio_streams,m,**kwargs):
    try:
        sample_rate=16000
        num_channels=1
        bits_per_sample=16
        # Concatenate the raw audio streams into a single byte sequence
        audio_data = b''.join(audio_streams)

        # Create a WAV header for the raw PCM data
        byte_rate = sample_rate * num_channels * bits_per_sample // 8
        block_align = num_channels * bits_per_sample // 8
        wav_header = struct.pack('<4sI4s4sIHHIIHH4sI',
                                b'RIFF', 36 + len(audio_data), b'WAVE', b'fmt ', 16, 1, num_channels,
                                sample_rate, byte_rate, block_align, bits_per_sample, b'data', len(audio_data))

        # Combine the WAV header with the raw PCM data
        wav_data = wav_header + audio_data

        # Create a BytesIO object containing the full WAV file
        audio_buffer = io.BytesIO(wav_data)

        # Load the audio using torchaudio
        waveform, sr = torchaudio.load(audio_buffer, format='wav', channels_first=True)

        # Perform inference using the provided model `m`
        res = m.inference(
            data_in=waveform,
            language="zh",  # "zh", "en", "yue", "ja", "ko", "nospeech"
            use_itn=False,
            ban_emo_unk=False,
            fs=sr,
            **kwargs,
        )

        for it in res[0]:
            it["clean_text"] = re.sub(regex, "", it["text"], 0, re.MULTILINE)

        return res[0]
    except Exception as e:
        print(e)
        return None

def start_listen(asr_queue):
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
                            if len(res[0]['clean_text'])>5:
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

if __name__ == "__main__":
    from multiprocessing import Queue
    asr_queue = Queue()

    start_listen(asr_queue)
