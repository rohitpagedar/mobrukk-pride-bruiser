# mobrukk-pride-bruiser

`mobrukk-pride-bruiser` is a small Python helper package for working with PostgreSQL-backed user and image metadata tables.

It was built as a lightweight database helper for experiments around WhatsApp chatbots and playful image-generation workflows. The package is intentionally simple: it gives a chatbot or background worker a place to track users, uploaded/generated images, metadata, and whether an image has been processed.

The default schema includes:

- `users`
- `images`

It wraps basic create, read, update, delete, and listing operations for these records.

## Use Case

This package can be useful when prototyping a chat-based image app where:

- users interact with a bot through WhatsApp or another messaging surface,
- image uploads or generated results need to be tracked,
- background jobs need to mark images as processed,
- small amounts of user/image metadata need to live in PostgreSQL.

It is not a full chatbot framework or image-generation system by itself. It is just the database helper layer that can sit underneath those workflows.

## Installation

Install the package locally from the repository:

```bash
pip install .
```

For development, install it in editable mode:

```bash
pip install -e .
```

## Requirements

- Python 3.8+
- PostgreSQL
- `psycopg2`

## Usage

```python
from mobrukk_pride_bruiser import Gandalf

db = Gandalf(
    host="localhost",
    port=5432,
    user="postgres",
    password="your-password",
    database="your-database",
)

db.connect()
db.add_user(
    userid="user-1",
    name="Ada Lovelace",
    email="ada@example.com",
    photos=0,
    metadata="{}",
)
db.add_image(
    imageid="image-1",
    userid="user-1",
    metadata="{}",
    processed=False,
)

user = db.get_user_details("user-1")
image = db.get_image_details("image-1")

db.close()
```

## Database Tables

The package can create the following tables when needed.

### `users`

| Column | Type |
| --- | --- |
| `userid` | `VARCHAR(255) PRIMARY KEY` |
| `name` | `VARCHAR(255)` |
| `email` | `VARCHAR(255)` |
| `photos` | `INT` |
| `metadata` | `VARCHAR(255)` |

### `images`

| Column | Type |
| --- | --- |
| `imageid` | `VARCHAR(255) PRIMARY KEY` |
| `userid` | `VARCHAR(255)` |
| `metadata` | `VARCHAR(255)` |
| `processed` | `BOOLEAN DEFAULT FALSE` |

## Publishing

Build a source distribution with:

```bash
python setup.py sdist
```

Upload with Twine after configuring your PyPI credentials:

```bash
python -m twine upload dist/*
```

## License

MIT License. See [LICENSE](LICENSE).
