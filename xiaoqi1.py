from common import get_llm_response
import streamlit as st
#运行：streamlit run ...

from openai import OpenAI

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
            'deepseek-chat',
            'deepseek-reasoner'
        ]
    model_name = st.selectbox(label ="请选择模型",options = model_options)
    if model_name in {            "gpt-3.5-turbo",
            "gpt-3.5-turbo-0301",
            "gpt-3.5-turbo-0613",
            "gpt-3.5-turbo-16k",
            "gpt-3.5-turbo-16k-0613",
            "gpt-4",
            "gpt-4-0314",
            "gpt-4-0613",
            "gpt-4-32k",}:
        api_key = st.secrets['API_KEY1']
    else:
        api_key = st.secrets['API_KEY2']
# 新增上传文件功能
uploaded_file = st.file_uploader("上传文本文件", type=["txt"])
uploaded_content = ""
if uploaded_file is not None:
    # 读取上传文件内容
    uploaded_content = uploaded_file.read().decode("utf-8")
    st.sidebar.markdown("### 上传文件内容预览")
    st.sidebar.text_area("", uploaded_content, height=200)

if 'messages' not in st.session_state:
    st.session_state['messages'] = [('ai','你好，我是你的聊天机器人，有什么事情都可以与我分享哦，我叫小七😀')]

st.write("### 聊天机器人小七")

if not api_key:
    st.error("请输入API Key")
    st.stop ()

for role, content in st.session_state['messages']:
    st.chat_message(role).write(content)

user_input = st.chat_input(placeholder ="请输入")
if user_input:
    _, history = st.session_state['messages'][-1]
    st.session_state['messages'].append(('human',user_input))
    st.chat_message("human").write(user_input)
    with st.spinner("小七正在思考中哦~，请耐心等待..."):
        # 如果上传了文件，可以将文件内容附加到问题后面
        prompt = f'{history}, {user_input}'
        if uploaded_content:
            prompt += f"\n\n附加文件内容：\n{uploaded_content}"
        answer = get_answer(prompt)
        result = st.chat_message("ai").write_stream(answer)
        st.session_state['messages'].append(('ai',result))
