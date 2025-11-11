from config.settings import settings

print("\n" + "="*60)
print("CONFIGURATION TEST")
print("="*60)
print(f"App Name: {settings.APP_NAME}")
print(f"Database Host: {settings.DB_HOST}")
print(f"Database Name: {settings.DB_NAME}")
print(f"Database User: {settings.DB_USER}")
print(f"Database Port: {settings.DB_PORT}")
print(f"Log Level: {settings.LOG_LEVEL}")
print("="*60)
print("✓ Configuration loaded successfully!")
print("="*60 + "\n")
