# GKerLove-agent

果壳之恋代理人项目

## 运行

安装依赖：

```shell
pip install -r requirements.txt
```

启动：

```shell
python index.py
```

## 环境变量

需要提供代理人的密码的环境变量，如*PASSWORD_ATHENA*。

需要提供*OPENAI_API_KEY*环境变量，配置*OPENAI_API_KEY*。项目中使用的是计算云的服务。如果使用*OpenAI*服务，需要在*config.py*中修改openai_base_url。

如果使用天气工具，需要提供*GAODE_API_KEY*环境变量。

如果使用必应搜索工具，需要提供*BING_SUBSCRIPTION_KEY*和*BING_SEARCH_URL*环境变量。

如果使用LangSmith追踪Agent，需要提供*LANGCHAIN_API_KEY*并设置*LANGCHAIN_TRACING_V2*值为true。

## 配置

在*config.py*中需要配置后端服务器地址和聊天服务器地址。

## 添加新的代理人

可以修改*user.py*，添加一个新的类即可。配置用户的用户名、密码（用户需要提前注册），编写用户的prompt。