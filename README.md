# LiveAssistPro

中文|[English](README_EN.md)

LiveAssistPro 是一个 AI 驱动的直播助手，通过监控屏幕内容和实时对话来帮助自动化任务并创建互动体验。它利用智谱 AI 的视觉模型分析屏幕，并检测用户语音以促进与角色扮演 AI 助手的交互。

## 功能特点

- **视觉分析**：LiveAssistPro 每隔几秒分析一次屏幕内容，使用智谱 AI 的视觉模型并提供结构化的 JSON 描述。
- **语音检测**：语音活动检测（VAD）用于检测用户讲话，自动语音识别（ASR）将讲话转化为文本。
- **AI 交互**：基于屏幕内容和用户语音与角色扮演 AI 助手进行交互，支持动态、上下文相关的对话。
- **实时更新**：根据屏幕的视觉内容和用户输入持续调整 AI 对话，确保高度自适应的互动。

## 安装

1. **克隆仓库：**

   ```bash
   git clone https://github.com/yourusername/LiveAssistPro.git
   cd LiveAssistPro
   ```

2. **安装依赖：**

   确保你已经安装了 Python（版本 3.8 或更高），然后安装所需的依赖包：
   pytorch first
    ```bash
    pip install torch==2.0.1 torchvision==0.15.2 torchaudio==2.0.2 --index-url https://download.pytorch.org/whl/cu118
    ```
    ```bash
    pip install -r requirements.txt
    ```
    ```bash
    cd alibabacloud-nls-python-sdk-dev
    python -m pip install -r requirements.txt
    python -m pip install .
    ```

3. **设置 API 密钥：**

   你需要[智谱 AI](https://maas.aminer.cn/)（用于视觉模型）的 API 密钥。将密钥添加到 `.env` 文件或直接在环境中配置。

   ```bash
   ZHIPU_KEY=your_zhipu_api_key
   ```

   此外，流式的cosyvoice功能需要使用阿里云智能语音交互平台，api获取[参考文档](https://help.aliyun.com/zh/isi/developer-reference/speech-synthesis/?spm=a2c4g.11186623.0.0.58387a17R9nwAd)

   同样在环境变量中配置阿里云控制台AK_ID, AK_SECRET，以及智能语音交互平台的 APP_ID
   ```bash
    ALIYUN_AK_ID= your_aliyun_ak_id
    ALIYUN_AK_SECRET= your_aliyun_ak_scret
    NLS_APP_ID=your_app_id
   ```
   然后运行
   ```python
   python cosyvoice_stream\get_token.py
   ```
   复制生成的token并填入
   ```bash
    NLS_TOKEN=your_nls_token
   ```

4. **运行助手：**

   设置完成后，运行助手：

   ```bash
   python main.py
   ```
    注：首次运行会自动下载sensevoice_small 权重
## 使用说明

1. **屏幕分析**：助手会定期捕捉并分析直播中的屏幕内容，使用智谱 AI 视觉模型。分析结果会以 JSON 格式返回，并用于指导 AI 交互。

2. **语音检测和处理**：VAD 系统监听用户语音，当检测到用户讲话时，ASR 将其转换为文本并传递给 AI 助手以便交互。

3. **AI 角色扮演交互**：基于屏幕分析和用户语音，角色扮演的 AI 助手会做出回应，创建互动性强、上下文相关的对话，提升直播体验。

## 配置

你可以在 `config.py` 文件中修改屏幕分析的时间间隔和其他设置。

```python
# 配置示例
SCREEN_READ_FREQ = 60  # 屏幕分析的时间间隔，单位：秒
GLM_MODEL = glm-4-0520 # 默认使用的智谱模型
```

## Todo

- [ ] 更复杂的提示词样式自定义
- [ ] 增加历史记忆功能
- [ ] 配置对 Dify 的支持\
...

## 贡献

欢迎贡献！如果你有建议或改进，请提交 issue 或 pull request。

## 许可证

LiveAssistPro 根据 Apache 许可证授权。更多细节请参阅 [LICENSE](LICENSE) 文件。
