from contextvars import ContextVar

user_id_ctx = ContextVar("user_id", default=None)
school_id_ctx = ContextVar("school_id", default=None)
role_ctx = ContextVar("role", default=None)