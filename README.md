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

## 质谱清言Schema
```s
{
  "openapi": "3.0.0",
  "info": {
    "title": "Coze Chat API",
    "version": "1.0.0",
    "description": "用于与 Coze 智能体进行对话的接口，支持上下文管理和流式响应"
  },
  "servers": [
    {
      "url": "https://api.coze.cn",
      "description": "Coze 生产环境"
    }
  ],
  "paths": {
    "/v3/chat": {
      "post": {
        "tags": ["Chat"],
        "summary": "发起对话",
        "description": "与指定智能体进行交互，支持流式响应和上下文管理",
        "operationId": "createChat",
        "security": [{"ApiKeyAuth": []}],
        "parameters": [
          {
            "name": "conversation_id",
            "in": "query",
            "description": "会话 ID（同一会话中的对话共享上下文）",
            "required": false,
            "schema": {
              "type": "string",
              "example": "conv_123456"
            }
          }
        ],
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "type": "object",
                "required": ["bot_id", "user_id"],
                "properties": {
                  "bot_id": {
                    "type": "string",
                    "description": "智能体 ID（从开发页面 URL 获取）",
                    "example": "7497970613215658020"
                  },
                  "user_id": {
                    "type": "string",
                    "description": "用户标识（需保证唯一性以实现数据隔离）",
                    "example": "user_001"
                  },
                  "additional_messages": {
                    "type": "array",
                    "description": "附加消息（最后一条需为用户消息）",
                    "items": {"$ref": "#/components/schemas/EnterMessage"},
                    "maxItems": 100
                  },
                  "stream": {
                    "type": "boolean",
                    "description": "是否启用流式响应",
                    "default": false
                  },
                  "custom_variables": {
                    "type": "object",
                    "description": "提示词变量（支持 Jinja2 语法）",
                    "additionalProperties": {"type": "string"},
                    "example": {
                      "location": "北京",
                      "temperature": "25℃"
                    }
                  },
                  "auto_save_history": {
                    "type": "boolean",
                    "description": "是否保存对话记录",
                    "default": true
                  },
                  "meta_data": {
                    "type": "object",
                    "description": "业务元数据（最多 16 个键值对）",
                    "additionalProperties": {
                      "type": "string",
                      "maxLength": 512
                    },
                    "maxProperties": 16
                  },
                  "extra_params": {
                    "type": "object",
                    "description": "附加参数（仅支持经纬度）",
                    "properties": {
                      "latitude": {
                        "type": "number",
                        "format": "float",
                        "example": 39.9800718
                      },
                      "longitude": {
                        "type": "number",
                        "format": "float",
                        "example": 116.309314
                      }
                    }
                  },
                  "shortcut_command": {"$ref": "#/components/schemas/ShortcutCommand"},
                  "parameters": {
                    "type": "object",
                    "description": "对话流自定义参数",
                    "additionalProperties": true
                  }
                }
              }
            }
          }
        },
        "responses": {
          "200": {
            "description": "成功响应",
            "content": {
              "application/json": {
                "schema": {
                  "type": "object",
                  "properties": {
                    "code": {
                      "type": "integer",
                      "description": "状态码（0=成功）",
                      "example": 0
                    },
                    "msg": {
                      "type": "string",
                      "description": "状态信息",
                      "example": "success"
                    },
                    "data": {"$ref": "#/components/schemas/ChatData"}
                  }
                }
              }
            }
          }
        }
      }
    },
    "/v3/chat/retrieve": {
      "get": {
        "tags": ["Chat"],
        "summary": "查看对话详情",
        "description": "查看对话的详细信息。在非流式会话场景中，调用发起对话接口后，可以先轮询此 API 确认本轮对话已结束（status=completed），再调用接口查看本轮对话的模型回复。仅在对话开启了保存历史记录（auto_save_history=true）后，可通过此接口查看对话的详细信息。建议每秒最多调用 1 次此接口，否则可能触发接口限流。",
        "operationId": "getChat",
        "security": [{"ApiKeyAuth": []}],
        "parameters": [
          {
            "name": "Authorization",
            "in": "header",
            "description": "用于验证客户端身份的访问令牌。你可以在扣子平台中生成访问令牌，详细信息，参考准备工作",
            "required": true,
            "schema": {
              "type": "string",
              "example": "Bearer $Access_Token"
            }
          },
          {
            "name": "Content-Type",
            "in": "header",
            "description": "解释请求正文的方式",
            "required": true,
            "schema": {
              "type": "string",
              "example": "application/json"
            }
          },
          {
            "name": "conversation_id",
            "in": "query",
            "description": "Conversation ID，即会话的唯一标识",
            "required": true,
            "schema": {
              "type": "string"
            }
          },
          {
            "name": "chat_id",
            "in": "query",
            "description": "Chat ID，即对话的唯一标识",
            "required": true,
            "schema": {
              "type": "string"
            }
          }
        ],
        "responses": {
          "200": {
            "description": "成功响应",
            "content": {
              "application/json": {
                "schema": {
                  "type": "object",
                  "properties": {
                    "data": {
                      "type": "object",
                      "properties": {
                        "id": {
                          "type": "string",
                          "description": "对话 ID，即对话的唯一标识",
                          "example": "737662389258662****"
                        },
                        "conversation_id": {
                          "type": "string",
                          "description": "会话 ID，即会话的唯一标识",
                          "example": "737554565555041****"
                        },
                        "bot_id": {
                          "type": "string",
                          "description": "要进行会话聊天的智能体 ID",
                          "example": "736661612448078****"
                        },
                        "created_at": {
                          "type": "integer",
                          "description": "对话创建的时间。格式为 10 位的 Unixtime 时间戳，单位为秒",
                          "example": 1717508113
                        },
                        "completed_at": {
                          "type": "integer",
                          "description": "对话结束的时间。格式为 10 位的 Unixtime 时间戳，单位为秒",
                          "example": 1717508113
                        },
                        "failed_at": {
                          "type": "integer",
                          "description": "对话失败的时间。格式为 10 位的 Unixtime 时间戳，单位为秒",
                          "example": 1717508113
                        },
                        "meta_data": {
                          "type": "object",
                          "description": "创建消息时的附加消息，用于传入使用方的自定义数据，获取消息时也会返回此附加消息。自定义键值对，应指定为 Map 对象格式。长度为 16 对键值对，其中键（key）的长度范围为 1～64 个字符，值（value）的长度范围为 1～512 个字符",
                          "example": {}
                        },
                        "last_error": {
                          "type": "object",
                          "description": "对话运行异常时，此字段中返回详细的错误信息，包括：Code：错误码。Integer 类型。0 表示成功，其他值表示失败。Msg：错误信息。String 类型。对话正常运行时，此字段返回 null。",
                          "properties": {
                            "code": {
                              "type": "integer",
                              "description": "错误码。0 表示成功，其他值表示失败",
                              "example": 0
                            },
                            "msg": {
                              "type": "string",
                              "description": "错误信息",
                              "example": ""
                            }
                          }
                        },
                        "status": {
                          "type": "string",
                          "description": "对话的运行状态。取值为：created：对话已创建；in_progress：智能体正在处理中；completed：智能体已完成处理，本次对话结束；failed：对话失败；requires_action：对话中断，需要进一步处理；canceled：对话已取消。",
                          "example": "completed"
                        },
                        "required_action": {
                          "type": "object",
                          "description": "需要运行的信息详情",
                          "properties": {
                            "type": {
                              "type": "string",
                              "description": "额外操作的类型，枚举值为 submit_tool_outputs",
                              "example": "submit_tool_outputs"
                            },
                            "submit_tool_outputs": {
                              "type": "object",
                              "description": "需要提交的结果详情，通过提交接口上传，并可以继续聊天",
                              "properties": {
                                "tool_calls": {
                                  "type": "array",
                                  "description": "具体上报信息详情",
                                  "items": {
                                    "type": "object",
                                    "properties": {
                                      "id": {
                                        "type": "string",
                                        "description": "上报运行结果的 ID",
                                        "example": ""
                                      },
                                      "type": {
                                        "type": "string",
                                        "description": "工具类型，枚举值为 function",
                                        "example": "function"
                                      },
                                      "function": {
                                        "type": "object",
                                        "description": "执行方法 function 的定义",
                                        "properties": {
                                          "name": {
                                            "type": "string",
                                            "description": "方法名",
                                            "example": ""
                                          },
                                          "arguments": {
                                            "type": "string",
                                            "description": "方法参数",
                                            "example": ""
                                          }
                                        }
                                      }
                                    }
                                  }
                                }
                              }
                            }
                          }
                        },
                        "usage": {
                          "type": "object",
                          "description": "Token 消耗的详细信息。实际的 Token 消耗以对话结束后返回的值为准",
                          "properties": {
                            "token_count": {
                              "type": "integer",
                              "description": "本次对话消耗的 Token 总数，包括 input 和 output 部分的消耗",
                              "example": 6644
                            },
                            "output_count": {
                              "type": "integer",
                              "description": "output 部分消耗的 Token 总数",
                              "example": 766
                            },
                            "input_count": {
                              "type": "integer",
                              "description": "input 部分消耗的 Token 总数",
                              "example": 5878
                            }
                          }
                        }
                      }
                    },
                    "code": {
                      "type": "integer",
                      "description": "状态码。0 代表调用成功",
                      "example": 0
                    },
                    "msg": {
                      "type": "string",
                      "description": "状态信息。API 调用失败时可通过此字段查看详细错误信息",
                      "example": ""
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  },
  "components": {
    "schemas": {
      "EnterMessage": {
        "type": "object",
        "properties": {
          "role": {
            "type": "string",
            "enum": ["user", "assistant"],
            "description": "消息角色"
          },
          "content": {
            "type": "string",
            "description": "消息内容"
          }
        }
      },
      "ShortcutCommand": {
        "type": "object",
        "properties": {
          "command_id": {
            "type": "string",
            "description": "快捷指令 ID"
          },
          "params": {
            "type": "object",
            "description": "指令参数",
            "additionalProperties": true
          }
        }
      },
      "ChatData": {
        "type": "object",
        "properties": {
          "conversation_id": {
            "type": "string",
            "example": "conv_123456"
          },
          "messages": {
            "type": "array",
            "items": {"$ref": "#/components/schemas/EnterMessage"}
          }
        }
      }
    },
    "securitySchemes": {
      "ApiKeyAuth": {
        "type": "apiKey",
        "in": "header",
        "name": "Authorization",
        "description": "Bearer Token（需包含 chat 权限）"
      }
    }
  }
}
```
