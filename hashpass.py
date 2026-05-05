print("Script démarré...")

import django
from django.conf import settings

# Configuration complète de Django
if not settings.configured:
    settings.configure(
        SECRET_KEY='temp-secret-key-for-hash-generation',
        INSTALLED_APPS=[
            'django.contrib.contenttypes',
            'django.contrib.auth',
        ],
        DATABASES={},
        PASSWORD_HASHERS=[
            'django.contrib.auth.hashers.PBKDF2PasswordHasher',
        ]
    )
    django.setup()

print("Django configuré avec succès!")

from django.contrib.auth.hashers import make_password

password = 'admin123'
hash_value = make_password(password)

print("\n" + "="*80)
print("AJOUTEZ CECI À VOTRE fypdb.sql :")
print("="*80)
print(f"""
INSERT INTO `app_user` (`user_id`, `name`, `role`, `password_hash`, `is_superuser`, `is_staff`, `is_active`) 
VALUES (
    1,
    'Admin',
    'ADMIN',
    '{hash_value}',
    1,
    1,
    1
);

INSERT INTO `admin_user` (`user_id`) VALUES (1);
""")
print("="*80)
print(f"Mot de passe : {password}")
print("="*80 + "\n")