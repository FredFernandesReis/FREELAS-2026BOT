# Freelancer BH Bot

Aplicacao Django com integracao ao Telegram e recebimento de webhooks da Cakto.

## Preparar ambiente local

Requer Python 3.13 ou superior compativel com Django 6.1.

1. Crie e ative um ambiente virtual.
2. Instale as dependencias: `pip install -r requirements.txt`.
3. Copie `.env.example` para `.env` e preencha as credenciais necessarias.
4. Execute `python manage.py migrate`.
5. Inicie o servidor local com `python manage.py runserver`.

O banco SQLite e os arquivos `.env` nao sao enviados ao GitHub. Em uma nova
instalacao, as migracoes criam a estrutura do banco; configure as credenciais
e crie novamente os usuarios administrativos conforme necessario.

## Variaveis para producao

Na VPS, configure as variaveis do `.env.example` no ambiente do servico ou em
um arquivo `.env` mantido fora do Git. Gere uma `DJANGO_SECRET_KEY` exclusiva,
defina `DJANGO_DEBUG=false` e informe o dominio/IP da VPS em
`DJANGO_ALLOWED_HOSTS` (separando varios hosts por virgula). Nunca publique
credenciais reais no repositorio.
