@echo off
:restart
echo Запускаем бот...
python botnew.py
if %ERRORLEVEL% EQU 0 (
    echo Бот завершил работу успешно.
) else (
    echo Бот был заблокирован Cloudflare. Перезапускаем через 60 секунд...
    timeout /t 60 /nobreak
    goto restart
)
