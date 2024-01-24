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

## 配置

需要提供*GKerLove_agent_password*环境变量，配置代理人的密码。

需要提供*OPENAI_API_KEY*环境变量，配置*OPENAI_API_KEY*。项目中使用的是计算云的服务。如果使用*OpenAI*服务，需要在*genertate.py*中修改base_url。

在*config.py*中需要配置后端服务器地址和聊天服务器地址。

## 添加新的代理人

可以修改*user.py*，添加一个新的类即可。配置用户的用户名、密码（用户需要提前注册），编写用户的prompt。

## 项目分支

master分支下，使用的是chat completions API，无状态。

asssistant分支下，使用的asssistant API，有状态，采用事件循环和消息循环实现，目前不太稳定。

目前部署在线上的是master分支。