# =============================================================================
# 示例用户工具:http_get —— 抓取一个网页并返回内容
# =============================================================================
#
# 这个文件同时也是一份「如何编写自己的工具」的模板。照着改就能用:
#
#   1. 在项目根目录的 tools/ 文件夹里新建一个 .py 文件(文件名不要以 _ 开头);
#   2. 从 harness.tools 导入 @tool 装饰器;
#   3. 写一个普通的 Python 函数(同步或 async 都可以),加上类型注解和 docstring;
#   4. 给函数戴上 @tool 装饰器;
#   5. 重启服务(或用 `python main.py --reload` 自动热重载)—— 完成!
#      Agent 立刻就能看到并调用你的新工具。
#
# 框架会自动根据函数签名生成给大模型看的 JSON Schema:
#   - 类型注解的映射:str -> string,int -> integer,float -> number,
#     bool -> boolean,list -> array,dict -> object;
#     Optional[X] / X | None 视为 X 且变为可选参数;没写注解则默认当作 string。
#   - 带默认值的参数是「可选」的,没有默认值的参数是「必填」的。
#   - 工具的整体描述取自 docstring 中 "Args:" 之前的文字;
#     每个参数的描述从 Google 风格的 "Args:" 段落里解析(写不写都行,写了更好)。
#
# 关于返回值与异常:
#   - 返回值最好是 str;返回其他类型会被自动 json.dumps 成字符串。
#   - 函数里抛出异常不会搞垮服务:框架会捕获它,并把
#     "ERROR: 异常类型: 消息" 作为工具结果交给模型,让它自行决定下一步。
#   - 超时:默认受配置项 TOOL_TIMEOUT_S(60 秒)限制;也可以针对单个工具
#     指定,例如 @tool(timeout=10)。装饰器还支持自定义名字和描述:
#     @tool(name="my_tool", description="...", timeout=10)。
# =============================================================================

import httpx

# 所有用户工具都用这一行导入装饰器(注意路径是 harness.tools):
from harness.tools import tool


@tool
def http_get(url: str, timeout: float = 20) -> str:
    """发送 HTTP GET 请求并返回响应,用于抓取网页或调用简单的 HTTP 接口。

    Args:
        url: 要请求的完整 URL,例如 "https://example.com"。
        timeout: 请求超时秒数,默认 20 秒。
    """
    # httpx.get 是同步调用;同步函数会被框架放进线程池执行,
    # 不会阻塞服务器,所以放心写同步代码即可。
    # follow_redirects=True:自动跟随 301/302 跳转,抓网页时更省心。
    response = httpx.get(url, timeout=timeout, follow_redirects=True)

    # 网页可能很长,这里只取正文前 5000 个字符,避免撑爆模型的上下文。
    # (框架层面还有 50000 字符的兜底截断,但工具自己控制粒度更好。)
    return f"HTTP {response.status_code}\n{response.text[:5000]}"
