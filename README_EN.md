# LiveAssistPro

[中文](README_CN.md) | English

LiveAssistPro is an AI-driven live streaming assistant that automates tasks and creates interactive experiences by monitoring screen content and engaging in real-time conversations. It leverages the Zhipu AI vision model to analyze the screen and detect user speech to facilitate interaction with a role-playing AI assistant.

## Features

- **Vision Analysis**: LiveAssistPro analyzes the screen content every few seconds using the Zhipu AI vision model and provides structured JSON descriptions.
- **Speech Detection**: Voice Activity Detection (VAD) detects when the user speaks, and Automatic Speech Recognition (ASR) converts the speech into text.
- **AI Interaction**: The AI assistant interacts based on both the screen content and user speech, enabling dynamic, context-aware dialogue.
- **Real-Time Updates**: AI dialogues are continuously updated based on the screen’s visual content and user inputs for highly adaptive interactions.

## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/yourusername/LiveAssistPro.git
   cd LiveAssistPro
   ```

2. **Install Dependencies:**

   Ensure you have Python installed (version 3.8 or higher), then install the necessary packages:
   Install pytorch first:

    ```bash
    pip install torch==2.0.1 torchvision==0.15.2 torchaudio==2.0.2 --index-url https://download.pytorch.org/whl/cu118
    ```
    Then install the rest of the dependencies:

    ```bash
    pip install -r requirements.txt
    ```
    ```bash
    cd alibabacloud-nls-python-sdk-dev
    python -m pip install -r requirements.txt
    python -m pip install .
    ```

3. **Set up API Keys:**

   You will need an API key from [Zhipu AI](https://maas.aminer.cn/) for the vision model. Add your key to the `.env` file or configure it in your environment:

   ```bash
   ZHIPU_KEY=your_zhipu_api_key
   ```

   For the streaming cosyvoice feature, use the Alibaba Cloud Intelligent Speech Interaction Platform. API access can be found in the [reference documentation](https://help.aliyun.com/zh/isi/developer-reference/speech-synthesis/?spm=a2c4g.11186623.0.0.58387a17R9nwAd).

   Configure Alibaba Cloud Console's AK_ID, AK_SECRET, and the APP_ID for the speech platform in your environment:

   ```bash
    ALIYUN_AK_ID=your_aliyun_ak_id
    ALIYUN_AK_SECRET=your_aliyun_ak_secret
    NLS_APP_ID=your_app_id
   ```

   Run the following to generate a token:

   ```python
   python cosyvoice_stream/get_token.py
   ```

   Copy the generated token and set it in your environment:

   ```bash
    NLS_TOKEN=your_nls_token
   ```

4. **Run the Assistant:**

   After setup, run the assistant:

   ```bash
   python main.py
   ```

   Note: On the first run, the sensevoice_small model weights will be automatically downloaded.

## Usage

1. **Screen Analysis**: The assistant periodically captures and analyzes the live stream’s screen content using the Zhipu AI vision model. The results are returned as JSON and inform AI interactions.

2. **Speech Detection and Processing**: The VAD system listens for user speech. When detected, ASR transcribes it to text, which is then sent to the AI assistant for interaction.

3. **AI Role-Playing Interaction**: Based on both the screen analysis and user speech, the role-playing AI assistant responds, enabling interactive, context-sensitive dialogues that enhance the live stream experience.

## Configuration

You can modify the screen analysis frequency and other settings in the `config.py` file.

```python
# Example Config Settings
SCREEN_READ_FREQ = 60  # Interval in seconds for screen analysis
GLM_MODEL = "glm-4-0520"  # Default Zhipu AI model
```

## Todo

- [ ] Customizable and more complex prompt styles
- [ ] Add history memory functionality
- [ ] Configure support for Dify\
...

## Contributing

Contributions are welcome! If you have suggestions or improvements, feel free to open an issue or submit a pull request.

## License

LiveAssistPro is licensed under the Apache License. See the [LICENSE](LICENSE) file for more details.
