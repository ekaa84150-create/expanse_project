from database import Base, engine
import models

print("Memuat tabel baru di database...")
Base.metadata.create_all(bind=engine)
print("Tabel 'users' dan 'transactions' berhasil dibuat! ✅")