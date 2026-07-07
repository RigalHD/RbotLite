# RbotLite (A Discord bot)
Create an `.env` file following the instructions bellow 
(see an example here: `.config/.env.example`)
- `.config/dev/.env.dev` for development
- `.config/prod/.env.prod` for production

## Installing dependencies
```cmd
pip install uv
uv pip install -e .
```
### Optional dependencies
```cmd
uv pip install -e ".[lint]"
```

## Launching the bot

### Development
```cmd
just dev
```

### Production
```cmd
just prod
```
