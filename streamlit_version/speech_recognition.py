# -*- coding: utf-8 -*-
"""
Author: jian wei
Create Time: 2025/4/27 16:30
File Name: speech_recognition.py
"""
import os
from datetime import datetime
import streamlit as st
from audio_recorder_streamlit import audio_recorder
from funasr import AutoModel
from funasr.utils.postprocess_utils import rich_transcription_postprocess


def init_speech_model():
    """
    初始化语音识别模型
    """
    if "speech_model" not in st.session_state:
        try:
            with st.spinner("正在加载语音识别模型，请稍候..."):
                model_dir = "iic/SenseVoiceSmall"
                model = AutoModel(
                    model=model_dir,
                    trust_remote_code=True,
                    remote_code="./model.py",
                    vad_model="fsmn-vad",
                    vad_kwargs={"max_single_segment_time": 30000},
                    device="cuda",
                )
                st.session_state.speech_model = model
                return model
        except Exception as e:
            st.error(f"语音识别模型加载失败: {str(e)}")
            return None
    return st.session_state.speech_model


def record_audio():
    """
    录制音频并返回音频路径
    点击一次开始录音，再次点击停止录音
    """
    # 确保录音状态初始化
    if "recording_status" not in st.session_state:
        st.session_state.recording_status = "ready"

    # 根据录音状态显示不同的按钮文本
    button_text = "点击开始录音" if st.session_state.recording_status == "ready" else "点击停止录音"
    audio_bytes = audio_recorder(
        text=button_text,
        recording_color="#e87070",
        neutral_color="#6aa36f",
        icon_name="microphone",
        icon_size="2x"
    )

    if audio_bytes:
        # 创建audio目录(如果不存在)
        os.makedirs("audio", exist_ok=True)

        # 保存录音文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        audio_path = f"audio/audio_{timestamp}.wav"
        with open(audio_path, "wb") as f:
            f.write(audio_bytes)

        # 更新录音状态
        st.session_state.recording_status = "ready"

        return audio_path, audio_bytes

    return None, None


def transcribe_audio(audio_path):
    """
    将音频转换为文本，转换完成后删除音频文件
    """
    model = init_speech_model()
    if not model:
        return None

    try:
        with st.spinner("语音识别中..."):
            res = model.generate(
                input=audio_path,
                cache={},
                language="auto",  # "zn", "en", "yue", "ja", "ko", "nospeech"
                use_itn=True,
                batch_size_s=60,
                merge_vad=True,
                merge_length_s=15,
            )
            text = rich_transcription_postprocess(res[0]["text"])
            try:
                os.remove(audio_path)
            except Exception as e:
                pass

            return text
    except Exception as e:
        st.error(f"语音识别失败: {str(e)}")
        try:
            os.remove(audio_path)
        except:
            pass
        return None


def speech_to_text_widget():
    """
    语音转文本小部件
    """
    col1, col2 = st.columns([1, 3])

    with col1:
        st.write("语音输入:")
        audio_path, audio_bytes = record_audio()

    with col2:
        if audio_path:
            st.audio(audio_bytes, format="audio/wav")

            text = transcribe_audio(audio_path)

            if text:
                st.session_state.speech_text = text
                st.success("语音识别成功!")
                return text

    return None
