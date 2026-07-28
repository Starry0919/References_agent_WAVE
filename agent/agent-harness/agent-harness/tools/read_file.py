# =============================================================================
# 示例用户工具:read_file —— 读取 workspace/ 沙箱里的文本文件
# =============================================================================
#
# 这个例子演示两件事:
#   1. 工具的基本写法(见 tools/http_get.py 顶部更完整的教程注释);
#   2. 如何给工具做「安全边界」:凡是涉及文件系统的工具,都应该把可访问
#      范围限制在一个沙箱目录里,防止模型(或被诱导的模型)读到项目之外
#      的任意文件,比如 .env 里的密钥。
#
# 约定:本项目的文件沙箱是项目根目录下的 workspace/ 文件夹。
# 想让 Agent 能读某个文件,就把它放进 workspace/ 里。
#
# 错误处理小技巧:与其抛异常,不如返回一个以 "ERROR:" 开头的字符串——
# 两种方式模型都能看到,但自己拼的错误信息可以写得更友好、更可读。
# =============================================================================

from pathlib import Path

# 所有用户工具都用这一行导入装饰器:
from harness.tools import tool

# 计算沙箱目录:本文件位于 <项目根>/tools/read_file.py,
# 所以 parent.parent 就是项目根目录,再拼上 "workspace"。
WORKSPACE = Path(__file__).resolve().parent.parent / "workspace"


@tool
def read_file(path: str) -> str:
    """读取 workspace/ 目录下的一个文本文件并返回其内容。

    Args:
        path: 相对于 workspace/ 的文件路径,例如 "notes.txt" 或 "data/a.csv"。
    """
    # 第一步:把用户给的相对路径拼到沙箱目录下,并 resolve() 成绝对路径。
    # resolve() 会展开所有的 ".."、符号链接等,得到真实的最终位置。
    target = (WORKSPACE / path).resolve()

    # 第二步:安全检查——最终位置必须仍然在沙箱目录之内。
    # 如果有人传入 "../../.env" 这类路径,resolve 之后就会跑出沙箱,
    # relative_to() 会抛 ValueError,我们据此拒绝并返回错误字符串(不抛异常)。
    try:
        target.relative_to(WORKSPACE.resolve())
    except ValueError:
        return f"ERROR: path escapes the workspace/ sandbox: {path}"

    # 第三步:读文件。文件不存在、是目录、编码不对等情况都转成
    # 可读的 ERROR 字符串返回,让模型知道发生了什么并自行调整。
    if not target.is_file():
        return f"ERROR: file not found in workspace/: {path}"
    try:
        return target.read_text(encoding="utf-8")
    except Exception as exc:  # e.g. UnicodeDecodeError, PermissionError
        return f"ERROR: {type(exc).__name__}: {exc}"
