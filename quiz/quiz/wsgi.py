"""
WSGI config for quiz project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.1/howto/deployment/wsgi/
"""

import os
# from helloworld.wsgi import HelloWorldApplication
# os.environ["DJANGO_SETTINGS_MODULE"] = "mysite.settings"
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quiz.settings')

application = get_wsgi_application()

application = HelloWorldApplication(application)

