from fastapi import FastAPI
from app.error_handlers import register_error_handlers
from app.api import router as api_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Register error handlers
register_error_handlers(app)

# Include API routes
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# structure ref - https://blog.stackademic.com/using-fastapi-with-sqlalchemy-5cd370473fe5
#  file upload - https://stackoverflow.com/questions/65342833/fastapi-uploadfile-is-slow-compared-to-flask/70667530#70667530
# https://stackoverflow.com/questions/63048825/how-to-upload-file-using-fastapi
# https://fastapi.tiangolo.com/tutorial/request-files/
# file download
# https://fastapi.tiangolo.com/advanced/custom-response/?h=fileresponse#fileresponse
# test
# https://testdriven.io/tips/b1b6489d-6538-4734-b148-6c03f8100096/
# exceptions
# https://fastapi.tiangolo.com/tutorial/handling-errors/#install-custom-exception-handlers




