from pathlib import Path

import yaml
from pydantic import BaseSettings, BaseModel


class Url(BaseModel):
    home: str = 'https://irs.zuvio.com.tw'
    target: str = 'https://irs.zuvio.com.tw/student5/irs/rollcall/123456'


class User(BaseModel):
    account: str = '123456789@school.edu.tw'
    password: str = 'enter_your_password'


class Location(BaseModel):
    latitude: float = 22.649803
    longitude: float = 120.328455


class Settings(BaseSettings):
    url: Url = Url()
    user: User = User()
    location: Location = Location()
    app_file: str = 'app.ui'
    env_file: str = 'default.yaml'
    headless: bool = False
    refresh_min: int = 4
    refresh_max: int = 8


class StatusCode(BaseModel):
    running = '執行中'
    stop = '停止中'


class ZuvioCode(BaseModel):
    finish = '已簽到完成'
    waiting = '尚未開始簽到'
    starting = '開始簽到'
    login_failed = '帳號或密碼錯誤'


def save_args(args, output_path=None):
    assert output_path is not None
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(Path(output_path), 'w', encoding='utf-8') as f:
        yaml.dump(args, f, Dumper=yaml.CDumper, indent=4, allow_unicode=True)
    return output_path


def read_args(file_path=None):
    assert file_path is not None
    if Path(file_path).exists() is False:
        return dict()
    with open(Path(file_path), 'r', encoding='utf-8') as f:
        args = yaml.load(f.read(), Loader=yaml.FullLoader)
    return args


if __name__ == '__main__':
    settings = Settings()
    print(settings.dict())
