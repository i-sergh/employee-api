## git
git clone

# env files


# docker-compose
sudo docker-compose up

## Alembic

sudo docker-compose exec web alembic revision --autogenerate -m "message"

sudo docker-compose exec web alembic upgrade head

sudo docker-compose exec web alembic current


## Pytest

sudo docker-compose exec web pytest -s tests/ --forked