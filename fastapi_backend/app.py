from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import core.configure  # noqa: F401
import utils.log_util  # noqa: F401
from api.v1.api import handle_router
from core.middleware import handle_middleware
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from core.configure import conf
import uvicorn
from loguru import logger


app = FastAPI()

# 挂一个文件服务
app.mount(path=conf.upload_url_prefix, app=StaticFiles(directory=conf.upload_dirpath), name='profile')


# 中间件
handle_middleware(app)
handle_router(app)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    logger.error(exc.errors())  # 👈 哪个参数错，一清二楚
    logger.error(exc.body)  # 👈 实际收到的请求体

    return JSONResponse(
        status_code=422,
        content={
            'detail': exc.errors(),
        },
    )


if __name__ == '__main__':
    uvicorn.run(
        'app:app',
        host=conf.backend_bind_host,
        port=conf.backend_port,
        reload=False,
    )
