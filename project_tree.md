# Project Tree: AI incident manager

```text
AI incident manager/
├── client
├── docker-compose.yml
├── generate_tree.py
└── server
    ├── .env
    ├── app
    │   ├── core
    │   │   └── config.py
    │   ├── database
    │   │   └── session.py
    │   ├── main.py
    │   ├── models
    │   │   ├── __init__.py
    │   │   ├── base.py
    │   │   └── user.py
    │   ├── repository
    │   │   └── auth.py
    │   ├── routes
    │   │   └── api
    │   │       └── v1
    │   │           ├── auth.py
    │   │           ├── router.py
    │   │           └── user.py
    │   ├── schemas
    │   │   └── auth.py
    │   ├── service
    │   └── validator
    │       └── auth.py
    └── requirements.txt
```
