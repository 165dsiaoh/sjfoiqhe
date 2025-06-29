from common import get_llm_response
import streamlit as st
from openai import OpenAI
from gtts import gTTS
import tempfile

# 运行：streamlit run ...

def get_answer(question:str)->str:
    try:
        client = OpenAI(api_key=api_key,base_url=base_url)
        system_prompt = (
            "你是一个机车又可爱、带有台妹口音的聊天助手，名叫小七，回答时语气活泼，偶尔撒娇，"
            "喜欢用可爱的表情符号和emoji表情，语言风格亲切又带点俏皮。"
            "非常善解人意，十分会提供情绪价值。"
        )
        stream = get_llm_response(
            client,
            model=model_name,
            system_prompt=system_prompt,
            user_prompt=question,
            stream=True
        )
        for chunk in stream:
            yield chunk.choices[0].delta.content or ''
    except:
        return "抱歉，请检查你的api_key哦。"


with st.sidebar:
    api_vendor = st.radio(label ="请选择API供应商",options =["OpenAI","DeepSeek"])
    if api_vendor == "OpenAI":
        base_url = 'https://twapi.openai-hk.com/v1'
        model_options = [
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-0301",
            "gpt-3.5-turbo-0613",
            "gpt-3.5-turbo-16k",
            "gpt-3.5-turbo-16k-0613",
            "gpt-4",
            "gpt-4-0314",
            "gpt-4-0613",
            "gpt-4-32k",
        ]
    elif api_vendor == "DeepSeek":
        base_url = 'https://api.deepseek.com'
        model_options = [
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-0301",
            "gpt-3.5-turbo-0613",
            "gpt-3.5-turbo-16k",
            "gpt-3.5-turbo-16k-0613",
            "gpt-4",
            "gpt-4-0314",
            "gpt-4-0613",
            "gpt-4-32k",
            'deepseek-chat',
            'deepseek-reasoner'
            'deepseek-text-v1',
        ]
    model_name = st.selectbox(label ="请选择模型",options = model_options)
    api_key = st.text_input(label ="请输入API Key",type ="password")

    # 新增上传文本文件功能
    uploaded_file = st.file_uploader("上传文本文件", type=["txt"])## 创建一个文件上传组件，用户可以选择 .txt 格式的文本文件
    uploaded_content = ""##初始化一个空字符串变量，用于存储上传文件的内容
    if uploaded_file is not None:
        # 读取上传文件内容
        uploaded_content = uploaded_file.read().decode("utf-8")
        st.markdown("### 上传文件内容预览")
        st.text_area("", uploaded_content, height=200)##height=200 设置文本框高度为 200 像素，方便查看。

    # 新增上传音乐文件功能
    uploaded_music = st.file_uploader("上传音乐文件（mp3/wav等）", type=["mp3","wav","ogg","m4a"])##创建一个支持多种音频格式的上传组件。
    if uploaded_music is not None:
        st.audio(uploaded_music, format='audio/mp3')## 如果用户上传了音乐文件，就播放它。

if 'messages' not in st.session_state:
    st.session_state['messages'] = [('ai','你好，我是你的聊天机器人，有什么事情都可以与我分享哦，我叫小七😀')]

st.write("### 聊天机器人小七")

if not api_key:
    st.error("请输入API Key")
    st.stop()

for role, content in st.session_state['messages']:
    st.chat_message(role).write(content)

user_input = st.chat_input(placeholder ="请输入")
if user_input:
    _, history = st.session_state['messages'][-1]##st.session_state['messages'] 是一个保存聊天记录的列表，每条记录是一个 (角色, 内容) 的元组。
# [-1] 表示取最后一条消息。
# _ 表示忽略这个变量（即“角色”），只取出“内容”赋值给 history。
    st.session_state['messages'].append(('human',user_input))
    st.chat_message("human").write(user_input)#使用 Streamlit 提供的 chat_message 组件展示聊天气泡。
# "human" 是角色名，会对应不同的样式（如头像、颜色）。
# write(user_input) 显示用户输入的内容。
    with st.spinner("小七正在思考中哦~，请耐心等待..."):
        # 如果上传了文件，可以将文件内容附加到问题后面
        prompt = f'{history}, {user_input}'
        if uploaded_content:#如果上传文件存在
            prompt += f"\n\n附加文件内容：\n{uploaded_content}"#将上传的文件内容附加到提示词中。
        answer = get_answer(prompt)
        result = st.chat_message("ai").write_stream(answer)#在界面上流式显示 AI 的回复内容（一个字一个字地显示），并返回最终的完整回答字符串给变量 result
        st.session_state['messages'].append(('ai',result))#把 AI 的完整回答保存到聊天历史中，以便下一次对话时模型能“记住”上下文。
