# 多路径推理与一致性投票

![项目封面](cover.svg)

对多个推理候选进行数值归一化、投票和拒答判断，并观察一致性与正确性的差异。

## 实现

- 使用分数精确表示统一小数、整数和分数答案。
- 无效格式仍进入投票分母。
- 至少三条候选、无并列且支持率达到 60% 才接受。
- 云端模式实际发起五次候选请求，显示每次的输出与总 API 调用情况。

## 在 PyCharm 运行

使用 Python 3.12，打开本文件所在目录，安装 requirements.txt 中依赖，运行 app.py。浏览器打开运行窗口给出的地址。默认端口为 5050，其他项目已运行时先停止或设置 PORT。

本地演示使用明示的固定合成题目与五条候选，其中含一条错误解答。它们不是云端模型的真实输出。输入新题目需要选择云端模式。

云端配置见 .env.example。将其复制为 .env 并在本机填入现有 API 参数，然后重新运行。使用 DeepSeek 时地址为 https://api.deepseek.com，使用 OpenRouter 时为 https://openrouter.ai/api/v1，模型名以服务商控制台为准。

## 可核验的评估

先运行 tests 中的单元测试。扩展实验时应另建带参考答案的题库，比较单次回答与多数投票的准确率、拒答率、调用次数和延迟，保留原始输出。投票支持率不代表答案正确率。候选之间可能相关。

## 参考

- [Self-Consistency Improves Chain of Thought Reasoning in Language Models](https://arxiv.org/abs/2203.11171)
- [DeepSeek API](https://api-docs.deepseek.com/api/create-chat-completion/)
