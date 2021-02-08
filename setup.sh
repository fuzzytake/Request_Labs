pip3 install flask_sqlalchemy
pip3 install flask_cors
pip3 install flask --upgrade
pip3 uninstall flask-socketio -y
brew services restart postgresql
sudo su postgres bash -c "psql < /home/workspace/backend/setup.sql"
sudo su postgres bash -c "psql bookshelf < /home/workspace/backend/books.psql"