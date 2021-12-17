import time
import requests
from requests import Session
from requests.models import Response

requests.packages.urllib3.disable_warnings()


# 请求
def request(session: Session, url: str, method: str = 'get', headers: dict = None, params: dict = None,
            data: dict = None, json: dict = None, allow_redirects=True, count: int = 3) -> (Response, int):
    req = None
    try:
        if method == 'get':
            req = session.get
        elif method == 'post':
            req = session.post
        response = req(url, headers=headers, params=params, data=data, json=json, timeout=10,
                       allow_redirects=allow_redirects, verify=False)
        if response.status_code == 200:
            return response, response.status_code
        raise ValueError('request:' + str(url) + ' status_code:' + str(response.status_code))
    except Exception as e:
        count -= 1
        if count > 0:
            time.sleep(0.2)
            return request(session, url, method, headers, params, data, json, allow_redirects, count)
        raise ValueError('request: ' + str(e))


# cookies转str
def cookies_to_str(response: Response) -> str:
    cookies_str = '; '.join([k + '=' + v for k, v in response.cookies.items()])  # 字典转成字符串
    return cookies_str
