"""Main FastAPI app module."""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from auth.routes import auth_router
from user.routes import user_router
from group.routes import group_router
from item.routes import item_router
from db import create_db_and_tables, drop_tables
from utils.utils import create_groups, create_items, create_users

# CORS setup
origins: list[str] = [
    'https://jdiaz.akamaized.net',
    'https://jdiaz.akamaized.edgesuite.net',
    'https://69.164.193.198',
    'https://127.0.0.1:80',
    'https://127.0.0.1:8000',
    'http://jdiaz.akamaized.net',
    'http://jdiaz.akamaized.edgesuite.net',
    'http://69.164.193.198',
    'http://127.0.0.1:80',
    'http://127.0.0.1:8000',
]

# Main app
app = FastAPI(title='Test API with FastAPI', version='1.0.0')

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(router=auth_router)
app.include_router(router=user_router)
app.include_router(router=group_router)
app.include_router(router=item_router)

app.mount(
    '/assets',
    StaticFiles(directory='../dist/assets'),
    name='assets',
)


@app.on_event('startup')
def on_startup():
    pass
    # drop_tables()
    # create_db_and_tables()
    # create_groups()
    # create_users()
    # create_items()


@app.get('/')
def get_main_page():
    """Get main page."""
    return FileResponse('../dist/index.html')


@app.get('/login/')
def get_login_page():
    """Get login page."""
    return FileResponse('../dist/login.html')


# Linode Akamaized certificate validation file

# @app.get('/.well-known/pki-validation/7AE15A7223EE5C942C79E9196DC6E51A.txt')
# def certificate_verification():
#     return FileResponse('../cert/7AE15A7223EE5C942C79E9196DC6E51A.txt')


@app.get('/{full_path:path}')
def last_resort(
    request: Request,
    full_path: str,
) -> dict:
    """Catches all undefined paths."""
    print(f'Got path: {full_path}')
    return {'detail': f'Not Found. Try {request.base_url}docs'}
