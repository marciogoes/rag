@echo off
echo ============================================================
echo TESTE RAPIDO - SISTEMA DE PROJETOS
echo Desenvolvido por: Marcio Goes do Nascimento
echo ============================================================
echo.

echo [1/2] Testando gerenciador de projetos...
echo.
python projetos.py
echo.

if %errorlevel% equ 0 (
    echo ✅ Gerenciador OK!
) else (
    echo ❌ Erro no gerenciador
    echo.
    echo DICA: Se o projeto ja existe, e normal!
    echo Execute: python limpar_testes.py para limpar
    pause
    exit /b 1
)

echo.
echo ============================================================
echo.
echo [2/2] Iniciando servidor de teste...
echo.
echo 📡 Servidor em: http://localhost:8000
echo 📖 Documentação: http://localhost:8000/docs
echo.
echo 🔐 Credenciais:
echo    Admin: admin / Admin@RAG2024!Secure
echo    User:  marcio / Marcio@2024!Dev
echo.
echo Para testar, abra outro terminal e execute:
echo    python teste_sistema.py
echo.
echo Ou abra no navegador:
echo    http://localhost:8000/docs
echo.
echo Pressione Ctrl+C para parar o servidor
echo ============================================================
echo.

python servidor_teste.py

pause
