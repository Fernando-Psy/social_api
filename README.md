# Social API - Backend

REST API for a social network built with Django REST Framework.

## 🚀 Technologies

- Python 3.12
- Django 5.2.8
- Django REST Framework 3.16.1
- PostgreSQL (production) / SQLite (development)
- JWT Authentication
- Heroku (deployment)

## 📋 Prerequisites

- Python 3.12+
- pip
- virtualenv (recommended)
- PostgreSQL (for production)

## 🔧 Installation and Setup

### 1. Clone the repository
```bash
git clone <repository-url>
cd social_api
```

### 2. Create and activate virtual environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=  # Leave empty to use SQLite in development
```

### 5. Run migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create a superuser (optional)
```bash
python manage.py createsuperuser
```

### 7. Start the development server
```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000`

## 📚 Main Endpoints

### Authentication
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - Login
- `GET /api/auth/profile/` - Authenticated user profile
- `PATCH /api/auth/profile/` - Update profile

### Posts
- `GET /api/posts/` - List posts (feed)
- `POST /api/posts/` - Create post
- `GET /api/posts/{id}/` - Post details
- `PUT/PATCH /api/posts/{id}/` - Update post
- `DELETE /api/posts/{id}/` - Delete post
- `POST /api/posts/{id}/like/` - Like post
- `DELETE /api/posts/{id}/unlike/` - Unlike post
- `POST /api/posts/{id}/comment/` - Comment on post
- `GET /api/posts/{id}/comments/` - List comments

### Follows
- `POST /api/follows/users/{id}/follow/` - Follow user
- `DELETE /api/follows/users/{id}/unfollow/` - Unfollow user
- `GET /api/follows/following/` - List who you follow
- `GET /api/follows/followers/` - List your followers

### JWT Token
- `POST /api/token/` - Obtain access token
- `POST /api/token/refresh/` - Refresh token

## 🧪 Run Tests
```bash
python manage.py test
```

## 📦 Deploy to Heroku

### 1. Install Heroku CLI

Download at: https://devcenter.heroku.com/articles/heroku-cli

### 2. Login to Heroku
```bash
heroku login
```

### 3. Create an app on Heroku
```bash
heroku create your-app-name
```

### 4. Configure environment variables on Heroku
```bash
heroku config:set SECRET_KEY=your-secret-key
heroku config:set DEBUG=False
```

### 5. Add PostgreSQL
```bash
heroku addons:create heroku-postgresql:essential-0
```

### 6. Deploy
```bash
git push heroku main
```

### 7. Run migrations on Heroku
```bash
heroku run python manage.py migrate
```

### 8. Create a superuser on Heroku (optional)
```bash
heroku run python manage.py createsuperuser
```

## 🔐 Authentication

The API uses JWT (JSON Web Tokens) for authentication. To access protected endpoints:

1. Login at `/api/auth/login/` or register at `/api/auth/register/`
2. Use the returned `access` token in request headers:
```
   Authorization: Bearer {your-token-here}
```

## 📝 Project Structure
```
social_api/
├── follows/          # Followers app
├── posts/            # Posts, likes and comments app
├── users/            # Users and authentication app
├── social_api/       # Project settings
├── manage.py
├── requirements.txt
├── Procfile          # Heroku configuration
└── runtime.txt       # Python version
```

## 🤝 Contributing

1. Fork the project
2. Create a feature branch (`git checkout -b feature/MyFeature`)
3. Commit your changes (`git commit -m 'Add MyFeature'`)
4. Push to the branch (`git push origin feature/MyFeature`)
5. Open a Pull Request

## 📄 License

This project is under the MIT license.


## Versão em Português

# Social API - Backend

API REST para uma rede social construída com Django REST Framework.

## 🚀 Tecnologias

- Python 3.12
- Django 5.2.8
- Django REST Framework 3.16.1
- PostgreSQL (produção) / SQLite (desenvolvimento)
- JWT Authentication
- Heroku (deploy)

## 📋 Pré-requisitos

- Python 3.12+
- pip
- virtualenv (recomendado)
- PostgreSQL (para produção)

## 🔧 Instalação e Configuração

### 1. Clone o repositório
```bash
git clone <url-do-repositorio>
cd social_api
```

### 2. Crie e ative o ambiente virtual
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto:
```env
SECRET_KEY=sua-chave-secreta-aqui
DEBUG=True
DATABASE_URL=  # Deixe vazio para usar SQLite em desenvolvimento
```

### 5. Execute as migrações
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Crie um superusuário (opcional)
```bash
python manage.py createsuperuser
```

### 7. Inicie o servidor de desenvolvimento
```bash
python manage.py runserver
```

A API estará disponível em `http://localhost:8000`

## 📚 Endpoints Principais

### Autenticação
- `POST /api/auth/register/` - Registro de novo usuário
- `POST /api/auth/login/` - Login
- `GET /api/auth/profile/` - Perfil do usuário autenticado
- `PATCH /api/auth/profile/` - Atualizar perfil

### Posts
- `GET /api/posts/` - Listar posts (feed)
- `POST /api/posts/` - Criar post
- `GET /api/posts/{id}/` - Detalhes do post
- `PUT/PATCH /api/posts/{id}/` - Atualizar post
- `DELETE /api/posts/{id}/` - Deletar post
- `POST /api/posts/{id}/like/` - Curtir post
- `DELETE /api/posts/{id}/unlike/` - Descurtir post
- `POST /api/posts/{id}/comment/` - Comentar em post
- `GET /api/posts/{id}/comments/` - Listar comentários

### Seguidores
- `POST /api/follows/users/{id}/follow/` - Seguir usuário
- `DELETE /api/follows/users/{id}/unfollow/` - Deixar de seguir
- `GET /api/follows/following/` - Lista quem você segue
- `GET /api/follows/followers/` - Lista seus seguidores

### Token JWT
- `POST /api/token/` - Obter token de acesso
- `POST /api/token/refresh/` - Renovar token

## 🧪 Executar Testes
```bash
python manage.py test
```

## 📦 Deploy no Heroku

### 1. Instale o Heroku CLI

Baixe em: https://devcenter.heroku.com/articles/heroku-cli

### 2. Faça login no Heroku
```bash
heroku login
```

### 3. Crie um app no Heroku
```bash
heroku create nome-do-seu-app
```

### 4. Configure as variáveis de ambiente no Heroku
```bash
heroku config:set SECRET_KEY=sua-chave-secreta
heroku config:set DEBUG=False
```

### 5. Adicione o PostgreSQL
```bash
heroku addons:create heroku-postgresql:essential-0
```

### 6. Deploy
```bash
git push heroku main
```

### 7. Execute as migrações no Heroku
```bash
heroku run python manage.py migrate
```

### 8. Crie um superusuário no Heroku (opcional)
```bash
heroku run python manage.py createsuperuser
```

## 🔐 Autenticação

A API usa JWT (JSON Web Tokens) para autenticação. Para acessar endpoints protegidos:

1. Faça login em `/api/auth/login/` ou registre-se em `/api/auth/register/`
2. Use o token `access` retornado no header das requisições:
```
   Authorization: Bearer {seu-token-aqui}
```

## 📝 Estrutura do Projeto
```
social_api/
├── follows/          # App de seguidores
├── posts/            # App de posts, likes e comentários
├── users/            # App de usuários e autenticação
├── social_api/       # Configurações do projeto
├── manage.py
├── requirements.txt
├── Procfile          # Configuração Heroku
└── runtime.txt       # Versão do Python
```

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT.
