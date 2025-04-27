# -*- coding: utf-8 -*-
"""
Author: jian wei
Create Time: 2025/4/25 10:41
File Name:speech_recognition.py
"""
# speech_recognition.py
# 语音识别模块，用于将用户语音转换为文本

import os
import tempfile
import uuid
from funasr import AutoModel
from funasr.utils.postprocess_utils import rich_transcription_postprocess


class SpeechRecognizer:
    def __init__(self, model_dir="iic/SenseVoiceSmall", device="cuda:0"):
        """初始化语音识别模型

        Args:
            model_dir: 模型目录
            device: 设备类型，如'cuda:0'或'cpu'
        """
        self.model_dir = model_dir
        self.device = device
        self.model = None

        # 延迟加载模型
        self._load_model()

    def _load_model(self):
        """加载语音识别模型"""
        try:
            self.model = AutoModel(
                model=self.model_dir,
                vad_model="fsmn-vad",
                vad_kwargs={"max_single_segment_time": 30000},
                device=self.device,
            )
            print(f"语音识别模型已加载，使用设备：{self.device}")
        except Exception as e:
            print(f"加载语音识别模型失败: {e}")
            # 如果CUDA不可用，尝试使用CPU
            if self.device.startswith("cuda"):
                print("尝试使用CPU加载模型...")
                self.device = "cpu"
                try:
                    self.model = AutoModel(
                        model=self.model_dir,
                        vad_model="fsmn-vad",
                        vad_kwargs={"max_single_segment_time": 30000},
                        device=self.device,
                    )
                    print("已使用CPU成功加载模型")
                except Exception as e2:
                    print(f"使用CPU加载模型也失败: {e2}")

    def recognize(self, audio_data, format="wav", sample_rate=16000):
        """将音频数据转换为文本

        Args:
            audio_data: 音频数据字节
            format: 音频格式
            sample_rate: 采样率

        Returns:
            str: 识别的文本
        """
        if self.model is None:
            print("语音识别模型未成功加载")
            return "语音识别模型未加载，请检查配置"

        try:
            # 保存音频数据到临时文件
            temp_dir = tempfile.gettempdir()
            temp_file = os.path.join(temp_dir, f"speech_{uuid.uuid4()}.{format}")

            with open(temp_file, "wb") as f:
                f.write(audio_data)

            # 识别音频
            res = self.model.generate(
                input=temp_file,
                cache={},
                language="auto",  # "zn", "en", "yue", "ja", "ko", "nospeech"
                use_itn=True,
                batch_size_s=60,
                merge_vad=True,
                merge_length_s=15,
            )

            # 处理结果
            if res and len(res) > 0:
                text = rich_transcription_postprocess(res[0]["text"])
                return text
            else:
                return "未能识别语音内容"

        except Exception as e:
            print(f"语音识别出错: {e}")
            return f"语音识别出错: {str(e)}"
        finally:
            # 删除临时文件
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass
