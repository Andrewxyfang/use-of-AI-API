from flask import Flask, request, jsonify, send_file
import requests
import time

app = Flask(__name__)

@app.route('/', methods=['GET'])
def serve_index():
    return send_file('temple/index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    # 初始请求URL
    url = 'https://api.coze.cn/v3/chat'
    headers = {
        'Authorization': 'Bearer pat_C9Px9VT3D74I4jLqWvAfPmy9J0Url09LslYHn3HvGXIMBazuG1kQS1y0JCVFPYVL',
        'Content-Type': 'application/json'
    }
    try:
        # 发送初始请求
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        print("初始请求响应结果:")
        for key, value in result.items():
            print(f"{key}: {value}")

        # 从初始响应中获取 conversation_id 和 chat_id
        conversation_id = result['data']['conversation_id']
        chat_id = result['data']['id']

        # 超时设置
        start_time = time.time()
        timeout = 600  # 超时时间，单位为秒

        while result['data']['status'] != 'completed':
             time.sleep(1)
             if time.time() - start_time > timeout:
                 print("请求超时，未获取到结果。")
                 return jsonify({"error": "请求超时，未获取到结果。"}), 500
             result_url = f'https://api.coze.cn/v3/chat/retrieve?conversation_id={conversation_id}&chat_id={chat_id}'
             newresponse = requests.get(result_url, headers=headers)
             newresponse.raise_for_status()
             result = newresponse.json()
             print("再次请求响应结果:")
             for key, value in result.items():
                print(f"{key}: {value}")

        end_url=f'https://api.coze.cn/v3/chat/message/list?conversation_id={conversation_id}&chat_id={chat_id}'
        endresponse = requests.get(end_url, headers=headers)
        result = endresponse.json()
        print("最后的响应结果:")
        for key, value in result.items():
             print(f"{key}: {value}")
        replies = [result['data'][0]['content']]
        return jsonify({"replies": replies})
        
    except requests.exceptions.HTTPError as http_err:
        return jsonify({"error": f'HTTP error occurred: {http_err}'}), 500
    except requests.exceptions.RequestException as req_err:
        return jsonify({"error": f'Request error occurred: {req_err}'}), 500
    except ValueError as json_err:
        return jsonify({"error": f'JSON decoding error occurred: {json_err}'}), 500

           
if __name__ == '__main__':
    app.run(debug=True)
