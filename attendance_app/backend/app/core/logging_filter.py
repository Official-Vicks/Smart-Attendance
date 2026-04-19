import logging
from app.core.request_context import user_id_ctx, school_id_ctx, role_ctx

class ContextFilter(logging.Filter):
    def filter(self, record):
        from app.core.request_context import user_id_ctx, school_id_ctx, role_ctx

        record.user_id = user_id_ctx.get()
        record.school_id = school_id_ctx.get()
        record.role = role_ctx.get()
        return True