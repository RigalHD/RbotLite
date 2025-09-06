# RbotLite (Очень маленький discord бот)
Перед запуском нужно создать файл аналогичный с `.config/.env.example`
- `.config/dev/.env.dev` для разработки
- `.config/prod/.env.prod` для продакшна

## Установка проекта

```cmd
pip install uv
uv pip install -e .
```

## Запуск проекта

### Разработка
```cmd
just dev
```

### Продакшн
```cmd
just prod
```
