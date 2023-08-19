import base64
import streamlit as st
import pandas as pd
import requests
import time
import io
from requests.exceptions import ReadTimeout, ConnectionError
html_code = """
<!DOCTYPE html>
<html>
<head>
    <title>Таблица описаний кодов ошибок</title>
</head>
<body>
    <h3>Таблица описаний кодов ошибок</h3>
    <table border="1">
        <tr>
            <th>Код ошибки</th>
            <th>Описание</th>
        </tr>
        <tr>
            <td>404</td>
            <td>Ошибка 404: Страница не найдена</td>
        </tr>
        <tr>
            <td>200</td>
            <td>Код 200: Успешный запрос</td>
        </tr>
        <tr>
            <td>301</td>
            <td>Ошибка 301: Перемещено навсегда</td>
        </tr>
        <tr>
            <td>302</td>
            <td>Ошибка 302: временное перенаправление</td>
        </tr>
        <tr>
            <td>307</td>
            <td>Ошибка 307: Временное перенаправление</td>
        </tr>
        <tr>
            <td>308</td>
            <td>Ошибка 308: Постоянное перенаправление</td>
        </tr>
        <tr>
            <td>429</td>
            <td>Ошибка 429: Слишком много запросов</td>
        </tr>
        <tr>
            <td>401</td>
            <td>Ошибка 401: Не авторизован</td>
        </tr>
        <tr>
            <td>503</td>
            <td>Ошибка 503: Сервис недоступен</td>
        </tr>
        <tr>
            <td>500</td>
            <td>Ошибка 500: Внутренняя ошибка сервера</td>
        </tr>
    </table>
</body>
</html>
"""
def callback(button):
    st.session_state.clicked[button] = True



def comboxchange():
    st.session_state.clicked[1] = True
    st.session_state.clicked[2] = True
    st.session_state.on_change = True

@st.cache
def convert_df(df):
    return df.to_csv().encode('utf-8')

def check_url(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
        }
        response = requests.head(url, headers=headers, timeout=10)
        status_code = response.status_code
        if status_code == 200:
            result = "200"
        elif status_code == 404:
            result = "404"
        else:
            result = f"{status_code}"
    except ReadTimeout as e:
        result = f"-1"
    except ConnectionError as e:
        result = f"-1"

    return url, result

def get_table_download_link_csv(df):
    csv = df.to_csv(index=False).encode()
    b64 = base64.b64encode(csv).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="data.csv" target="_blank">Скачать csv файл (вся таблица)</a>'
    return href




if 'results' not in st.session_state:
    st.session_state.results = []
results = st.session_state.results
results_df = pd.DataFrame(results, columns=["URL", "Ответ"])
st.title("URL Checker ( массовая проверка ответа сервера)")
html_footer= """<p>Проверка кода ответа сервера по списку url.
    Онлайн-сервис проверяет кода ответа HTTP страницы, который отдает сервер взамен на запрос. Можно массово проверить ссылки и узнать статус каждой.
    </p>
    """
st.markdown(html_footer, unsafe_allow_html=True)
st.write(html_code, unsafe_allow_html=True)
memo_text = st.text_area("Вставьте url (1 строка= 1 url)")

delay = st.number_input("Задержка в секундах", value=0, min_value=0)


if 'clicked' not in st.session_state:
    st.session_state.clicked = {1:False,2:False}
st.session_state.on_change=False


st.button("Запустить парсинг", on_click=callback,args=[1])
if st.session_state.clicked[1]:

    if st.session_state.on_change==False and  st.session_state.clicked[2]==False:
        urls = memo_text.split("\n")
        urls = [url.strip() for url in urls if url.strip()]

        progress_bar = st.progress(0, )
        for i, url in enumerate(urls):
            time.sleep(delay)
            fff="Подождите, идет проверка..., еще осталось "+str(len(urls)-i-1)+" url"
            progress_bar.progress((i + 1) / len(urls),text=fff)
            results.append(check_url(url))

    results_df = pd.DataFrame(results, columns=["URL", "Ответ"])
    st.dataframe(results_df)
    st.markdown(get_table_download_link_csv(results_df), unsafe_allow_html=True)






    export_options = st.selectbox("Выберите ошибки для экспорта:", ["Все", "404", "200", "301", "302", "307","308", "429","401","503","500"], on_change=comboxchange)

    st.button("Экспортировать в  CSV", on_click=callback,args=[2])
    if st.session_state.clicked[2]:
        export_df = pd.DataFrame()
        export_df = results_df

        if export_options == "Все":
            filtered_df = export_df
        else:
            response_code = int(export_options)
            filtered_df = export_df[export_df["Ответ"] == str(response_code)]

        st.markdown(get_table_download_link_csv(filtered_df), unsafe_allow_html=True)
        st.stop()

        st.session_state.clicked[1] = False
        st.session_state.clicked[2] = False
        st.session_state.on_change = False


