from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import RedirectResponse

from .users import templates


async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ):
    form_data = await request.form()
    username = form_data.get('username')
    if 'login' in str(request.url):
        name = 'login.html'
    elif 'register' in str(request.url):
        name = 'register.html'
    else:
        raise exc
    return templates.TemplateResponse(
        request=request, name=name,
        context={'msg': 'Validation error', 'username': username},
    )

def include_app(app):
    app.add_exception_handler(RequestValidationError,
                              validation_exception_handler)
