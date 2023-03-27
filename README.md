# eLibrary API
- API service for library management. It helps to track a borrowing status of every book, which is registered in the library database.

## Features 
- JWT authentication
- Admin panel at /admin/
- Email authorization
- Documentation located at /api/doc/swagger/
- Creating/updating and deleting books (for admin)
- Detailed book and borrowing info
- Book inventory validation
- Filtering borrowings by book active status(not returned)
- Filtering borrowings by user_id (for admin)
- Telegram notifications when a new borrowing is created
- Telegram daily report of overdue borrowings (Celery & Redis)

## How to run
```
git clone https://github.com/viktory-koroliova/rest_practice.git
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
- Copy .env.sample -> .env and populate  with all required information
- run `docker-compose up --build`
- Use email `admin@admin.com` and password `admin12345` to get admin token on /api/user/token
- Authorize with it on /api/doc/swagger/ OR
- Install ModHeader extension and create Request header with value Bearer <Your access tokekn>
- Run 
```
docker exec -it <container id> bash
celery -A rest_practice worker -l info --pool=solo
celery -A rest_practice beat -l INFO  --scheduler django_celery_beat.schedulers:DatabaseScheduler
```
