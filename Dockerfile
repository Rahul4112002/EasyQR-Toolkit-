# Use the official Python 3.10 image
FROM python:3.10

# Install system dependencies including zbar shared library
RUN apt-get update && apt-get install -y \
    zbar-tools \
    libzbar0 \
    && apt-get clean


# Set the working directory inside the container
WORKDIR /core

# Copy the project files into the container
COPY . .

# Install dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

RUN python manage.py collectstatic --noinput

# Expose the port the app runs on
EXPOSE 8000

# Start the Django application using Gunicorn
CMD ["gunicorn", "djangoqr.wsgi:application", "--bind", "0.0.0.0:8000"]
