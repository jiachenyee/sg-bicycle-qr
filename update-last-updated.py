import datetime

last_updated = datetime.datetime.now().isoformat()
    
with open('data/last_updated.txt', 'w') as file:
    file.write(last_updated)
    
print(f"Last updated date written: {last_updated}")