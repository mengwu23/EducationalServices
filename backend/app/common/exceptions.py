"""
业务异常定义模块（仅请假审批模块所需）
========================================

异常层级结构：
    AppException（基类，所有业务异常的父类）
    ├── NotFoundException          # 资源不存在（404）
    ├── PermissionDeniedException  # 权限不足（403）
    ├── StateConflictException     # 状态冲突（409），如已审批的请假不能取消
    └── ValidationErrorException   # 参数校验失败（422）
"""


class AppException(Exception):
    """业务异常基类

    所有自定义业务异常的父类，统一携带 code、message、status_code 三个属性。
    Controller 层通过全局异常处理器捕获后，按统一响应格式返回给客户端。

    Attributes:
        code: 业务错误码（如 40401、40301），前端可通过 code 做国际化
        message: 人类可读的错误描述
        status_code: HTTP 状态码
    """

    def __init__(self, code: int, message: str, status_code: int = 400):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"


class NotFoundException(AppException):
    """资源未找到异常

    当请求的业务数据不存在时抛出，对应 HTTP 404。

    使用示例：
        raise NotFoundException("请假申请不存在")
        raise NotFoundException("学生不存在", code=40402)
    """

    def __init__(self, message: str = "请求的资源不存在", code: int = 40400):
        super().__init__(code=code, message=message, status_code=404)


class PermissionDeniedException(AppException):
    """权限不足异常

    当用户尝试执行其角色不允许的操作时抛出，对应 HTTP 403。

    使用示例：
        raise PermissionDeniedException("只有学生才能提交请假")
        raise PermissionDeniedException("只有员工才能审批请假")
    """

    def __init__(self, message: str = "权限不足", code: int = 40300):
        super().__init__(code=code, message=message, status_code=403)


class StateConflictException(AppException):
    """状态冲突异常

    当业务状态不满足操作前提时抛出，对应 HTTP 409。
    例如：试图取消一个已经审批通过的请假。

    使用示例：
        raise StateConflictException("当前状态不允许取消，仅待审批的请假可以取消")
        raise StateConflictException("该请假已被审批，无法修改")
    """

    def __init__(self, message: str = "当前状态不允许此操作", code: int = 40900):
        super().__init__(code=code, message=message, status_code=409)


class ValidationErrorException(AppException):
    """参数校验失败异常

    当请求参数不符合业务规则时抛出，对应 HTTP 422。
    与 Pydantic 的内置校验不同，这类异常用于业务层面的参数校验失败。

    使用示例：
        raise ValidationErrorException("结束时间不能早于开始时间")
        raise ValidationErrorException("请假原因不能为空")
    """

    def __init__(self, message: str = "参数校验失败", code: int = 42200):
        super().__init__(code=code, message=message, status_code=422)
