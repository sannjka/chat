from fastapi import Request
from fastapi.exceptions import RequestValidationError

from .users import templates


async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ):
    form_data = await request.form()
    context = {
        'request': request,
        'msg': 'Validation error',
        'username': form_data.get('username'),
    }
    return templates.TemplateResponse('register.html', context)

def include_app(app):
    app.add_exception_handler(RequestValidationError,
                              validation_exception_handler)
