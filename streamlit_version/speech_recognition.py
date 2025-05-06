"""
Author: jian wei
Create Time: 2025/5/6
File Name: speech_recognition.py
"""
import os
from datetime import datetime
import streamlit as st
from st_audiorec import st_audiorec
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
                    vad_model="fsmn-vad",
                    vad_kwargs={"max_single_segment_time": 30000},
                    device="cuda",
                    disable_update=True
                )
                st.session_state.speech_model = model
                return model
        except Exception as e:
            st.error(f"语音识别模型加载失败: {str(e)}")
            return None
    return st.session_state.speech_model


def save_audio_file(audio_bytes):
    """
    保存音频文件并返回文件路径
    """
    if not audio_bytes:
        return None

    # 创建audio目录(如果不存在)
    os.makedirs("audio", exist_ok=True)

    # 保存录音文件
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    audio_path = f"audio/audio_{timestamp}.wav"
    with open(audio_path, "wb") as f:
        f.write(audio_bytes)

    return audio_path


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
    语音转文本小部件，使用st_audiorec组件
    """
    # 设置一些自定义CSS样式，让音频记录器更美观
    st.markdown('''
    <style>
        /* 自定义音频记录器样式 */
        .stAudio {height: 45px;}
        .css-1pxazr7 {padding-top: 0rem !important;}
        /* 移除重复的音频播放器，只保留st_audiorec内置的播放器 */
        div[data-testid="stAudio"] + div[data-testid="stAudio"] {display: none;}
    </style>
    ''', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 3])

    with col1:
        st.write("语音输入:")

    with col2:
        # 使用st_audiorec组件，它内置了波形可视化
        audio_bytes = st_audiorec()

        if audio_bytes:
            # 判断是否是新录音
            if "last_audio_bytes" not in st.session_state or st.session_state.last_audio_bytes != audio_bytes:
                st.session_state.last_audio_bytes = audio_bytes
                # 保存并处理音频
                audio_path = save_audio_file(audio_bytes)
                if audio_path:
                    text = transcribe_audio(audio_path)
                    # 清空audio目录下的文件
                    for file in os.listdir("audio"):
                        file_path = os.path.join("audio", file)
                        if os.path.isfile(file_path):
                            os.remove(file_path)
                    if text:
                        st.session_state.speech_text = text
                        st.success("语音识别成功!")
                        return text

    # 总是显示文本区域，即使没有语音识别结果
    if "speech_text" not in st.session_state:
        st.session_state.speech_text = ""

    return None