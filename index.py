from app import app
from utils.db import db


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
