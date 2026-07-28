## Agent Harness（CMD运行）步骤
### 1.cmd
cd /d "D:\Users\Starry\Desktop\agent\agent\agent-harness\agent-harness"
.venv_win\Scripts\activate.bat
python main.py --reload
cd /d "D:\Users\Starry\Desktop\agent\20260717_JH_agent_structure\agent-harness\agent-harness\frontend"
npm run dev





### 1. 打开 CMD
---
### 2. 进入项目目录
```cmd
cd /d D:\Users\Starry\Desktop\agent\workflow\design\JH\agent-harness-v1\agent-harness-v1
```
---
### 3. 确认目录正确
```cmd
dir
```
应看到：
```text
main.py
requirements.txt
.env
harness
tools
web
```
---
### 4. 安装依赖（首次运行）
```cmd
pip install -r requirements.txt
```
---
### 5. 启动 Agent
```cmd
python main.py
```
---
### 6. 启动成功显示
```text
================================================
Agent Harness 已启动

地址:
http://127.0.0.1:8642

供应商:
deepseek

模型:
xxxx
================================================
```

---

### 7. 浏览器访问

打开：

```text
http://127.0.0.1:8642
```

即可进入 Agent 页面。
