# Temvelo Project

This document provides instructions for setting up and running the Temvelo Django project.

## Prerequisites

Ensure you have the following installed:
- Python 3.8+
- Pip (Python package manager)
- GDAL (installed globally on your system)

### Installing GDAL Globally

#### On Ubuntu/Debian:
```bash
sudo apt-get install gdal-bin
sudo apt-get install libgdal-dev
```

#### On macOS using Homebrew:
```bash
brew install gdal
```

## Setup Instructions

### Step 1: Install Python

1. Download Python from the official website: [Python Downloads](https://www.python.org/downloads/)
2. Follow the installation instructions for your operating system.

### Step 2: Clone the Repository

```bash
git clone https://your-repo-url.git
cd temvelo
```

### Step 3: Set Up Virtual Environment

1. **Create a virtual environment**:
   ```bash
   python -m venv myvenv
   ```

2. **Activate the virtual environment**:
   - On macOS and Linux:
     ```bash
     source myvenv/bin/activate
     ```
   - On Windows:
     ```bash
     .\myvenv\Scripts\activate
     ```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 5: Set Up Database

> Ensure the database configurations are set in `temvelo/settings.py`.

1. **Apply migrations**:
   ```bash
   python manage.py migrate
   ```

### Step 6: Run the Project

1. **Start the Django development server**:
   ```bash
   python manage.py runserver
   ```

2. Visit `http://127.0.0.1:8000/` in your web browser.

## Additional Information

- **Static Files**: Collect static files using:
  ```bash
  python manage.py collectstatic
  ```
- **Admin Interface**: To access the Django admin interface, create a superuser:
  ```bash
  python manage.py createsuperuser
  ```

Ensure environment variables are correctly configured if using services like OpenAI or Google Cloud.

---

Follow these instructions to set up and run the Temvelo project successfully. For further assistance, please refer to the Django documentation or reach out to the project maintainers.
