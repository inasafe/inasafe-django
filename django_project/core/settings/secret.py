# coding=utf-8
import os

# This is django secret

if 'SECRET_KEY' in os.environ:
    SECRET_KEY = os.environ.get('SECRET_KEY')
else:
    # Use default secret key for development use
    # Generate new one and don't share it for production
    SECRET_KEY = "&+&ly2fd$$tj&9)polyg!qol@@=f!jr@k3-pb)5q8vqj)9=2l#"


# This secret is used by mapquest

MAPQUEST_MAP_KEY = os.environ.get('MAPQUEST_MAP_KEY')
