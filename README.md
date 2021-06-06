# Verification call list updater

Чтобы запустить локально, создайте новое виртуальное окружение и установите необходимые пакеты:

```bash
conda create --name calls_upd
conda activate calls_upd
pip install -r requirements.txt
```

Запустите сервер Flask:

```bash
export FLASK_APP=app_flie.py
flask run
```

Сервис будет доступен по адресу `localhost:5000/upload`
