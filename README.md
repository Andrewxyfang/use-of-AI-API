# use-of-AI-API
# agent API的使用
## 网页前端布局代码
```javascript
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chat with Agent</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.7.2/css/all.min.css" rel="stylesheet">
</head>

<body class="bg-gray-100 p-8">
    <div class="max-w-md mx-auto bg-white p-6 rounded shadow-md">
        <h1 class="text-2xl font-bold mb-4">与 Agent 聊天</h1>
        <input type="text" id="user-input" class="border border-gray-300 p-2 w-full mb-4" placeholder="输入你的消息">
        <button id="send-button" class="bg-blue-500 text-white p-2 rounded hover:bg-blue-600">发送</button>
        <div id="chat-responses" class="mt-4">
            <!-- 聊天回复将显示在这里 -->
        </div>
    </div>

    <script>
        const sendButton = document.getElementById('send-button');
        const userInput = document.getElementById('user-input');
        const chatResponses = document.getElementById('chat-responses');

        sendButton.addEventListener('click', async () => {
            const message = userInput.value;
            if (message) {
                const data = {
                    "bot_id": "7494103024999219218",
                    "user_id": "123123123",
                    "stream": false,
                    "auto_save_history": true,
                    "additional_messages": [
                        {
                            "role": "user",
                            "content": message,
                            "content_type": "text"
                        }
                    ]
                };//data的格式是API自己规定好的，需要查看他的API文档

                try {
                    const response = await fetch('/chat', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(data)
                    });

                    const result = await response.json();
                    if (result.replies) {
                        result.replies.forEach(reply => {
                            const p = document.createElement('p');
                            p.textContent = reply;
                            chatResponses.appendChild(p);
                        });
                    } else {
                        const p = document.createElement('p');
                        p.textContent = `错误: ${result.error}`;
                        chatResponses.appendChild(p);
                    }
                } catch (error) {
                    const p = document.createElement('p');
                    p.textContent = `网络错误: ${error.message}`;
                    chatResponses.appendChild(p);
                }
            }
        });
    </script>
</body>

pat_C9Px9VT3D74I4jLqWvAfPmy9J0Url09LslYHn3HvGXIMBazuG1kQS1y0JCVFPYVL
</html>
```
## 后端代码（内部接收前端请求，并向API发送请求）
```python
from flask import Flask, request, jsonify, send_file
import requests
import time

app = Flask(__name__)

@app.route('/', methods=['GET'])
def serve_index():
    return send_file('temple/index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()#前端发送过来的数据
    # 初始请求URL
    url = 'https://api.coze.com/v3/chat'# 这个是请求的端口号
    headers = {
        'Authorization': 'Bearer pat_Nf9BeYxzFeABSyfMwFy3uijRGsW3oVto091PcDW9P29ppnw2JnkU81P9lIGmiYcI',# 这个是通讯令牌，有些API不需要
        'Content-Type': 'application/json' # 规定发送回来的信息格式为json格式
    }
    try:
        # 发送初始请求
        response = requests.post(url, headers=headers, json=data)# 这里发送请求，将收到的结果赋值给response
        response.raise_for_status()# 检查返回的状态码
        result = response.json()# 形成json格式，储存在result中
        print("初始请求响应结果:")
        for key, value in result.items():
            print(f"{key}: {value}")

        # 从初始响应中获取 conversation_id 和 chat_id，数据要如何解析需要查看API文档，了解他的数据组成结构
        conversation_id = result['data']['conversation_id']
        chat_id = result['data']['id']

        # 超时设置
        start_time = time.time()
        timeout = 600  # 超时时间，单位为秒
        # 确保信息已经处理成功
        while result['data']['status'] != 'completed':
            if time.time() - start_time > timeout:
                print("请求超时，未获取到结果。")
                return jsonify({"error": "请求超时，未获取到结果。"}), 500
            
            result_url = f'https://api.coze.com/v3/chat/retrieve?conversation_id={conversation_id}&chat_id={chat_id}'
            newresponse = requests.post(result_url, headers=headers)
            newresponse.raise_for_status()
            result = newresponse.json()
            print("再次请求响应结果:")
            for key, value in result.items():
                print(f"{key}: {value}")
        # 获得最终的回复
        end_url=f'https://api.coze.com/v3/chat/message/list?conversation_id={conversation_id}&chat_id={chat_id}'
        endresponse = requests.post(end_url, headers=headers)
        result = endresponse.json()
        print("最后的响应结果:")
        for key, value in result.items():
             print(f"{key}: {value}")
        replies = [result['data'][0]['content']]
        return jsonify({"replies": replies})
        # 错误处理
    except requests.exceptions.HTTPError as http_err:
        return jsonify({"error": f'HTTP error occurred: {http_err}'}), 500
    except requests.exceptions.RequestException as req_err:
        return jsonify({"error": f'Request error occurred: {req_err}'}), 500
    except ValueError as json_err:
        return jsonify({"error": f'JSON decoding error occurred: {json_err}'}), 500

           
if __name__ == '__main__':
    app.run(debug=True，port=5000)
```
