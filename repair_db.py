import sqlite3
import os

print("🔧 Reparando base de datos - Preferencias de usuario...")

conn = sqlite3.connect('db.sqlite3')
c = conn.cursor()

# Verificar UserNotificationPreference
print("📋 Verificando tabla notifications_usernotificationpreference...")
c.execute('PRAGMA table_info(notifications_usernotificationpreference);')
columns = c.fetchall()

existing_columns = [col[1] for col in columns]
print(f"Columnas existentes: {existing_columns}")

required_columns = [
    'order_notifications',
    'shipping_notifications', 
    'promotional_notifications',
    'support_notifications',
    'email_enabled',
    'sms_enabled',
    'whatsapp_enabled',
    'push_enabled',
    'phone_number',
    'whatsapp_number'
]

for col_name in required_columns:
    if col_name not in existing_columns:
        try:
            if col_name.endswith('_notifications') or col_name.endswith('_enabled'):
                c.execute(f'ALTER TABLE notifications_usernotificationpreference ADD COLUMN {col_name} BOOLEAN DEFAULT 1;')
            elif col_name in ['phone_number', 'whatsapp_number']:
                c.execute(f'ALTER TABLE notifications_usernotificationpreference ADD COLUMN {col_name} VARCHAR(20) DEFAULT "";')
            
            print(f'✅ Agregada columna: {col_name}')
        except sqlite3.OperationalError as e:
            print(f'⚠️  Error con {col_name}: {e}')

conn.commit()
conn.close()
print("🎉 Base de datos reparada!")
