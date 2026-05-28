import sys, json, os, time

DATA_DIR = os.path.expanduser("~/pi-cwd-20260526/notebooklm_data")
DB_FILE = os.path.join(DATA_DIR, "notebooks.json")

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "active_notebook": "default",
        "notebooks": {
            "default": {
                "id": "default",
                "name": "Default Notebook",
                "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "sources": [],
                "chat_history": [],
                "settings": {"context_mode": "auto"}
            }
        }
    }

def save_db(db):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

def create_notebook(name):
    db = load_db()
    nb_id = f"nb_{int(time.time())}"
    db["notebooks"][nb_id] = {
        "id": nb_id,
        "name": name,
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "sources": [],
        "chat_history": [],
        "settings": {"context_mode": "auto"}
    }
    save_db(db)
    return db["notebooks"][nb_id]

def add_source(notebook_id, file_path, title=""):
    db = load_db()
    src_id = f"src_{int(time.time())}"
    filename = os.path.basename(file_path)

    source = {
        "id": src_id,
        "notebook_id": notebook_id,
        "filename": filename,
        "title": title or filename,
        "type": "pdf" if filename.endswith('.pdf') else "txt",
        "added_at": time.strftime("%Y-%m-%dT%H:%M:%SZ")
    }

    db["notebooks"][notebook_id]["sources"].append(source)
    save_db(db)
    return source

def get_active():
    db = load_db()
    return db["notebooks"][db["active_notebook"]]

if __name__ == "__main__":
    action = sys.argv[1]
    if action == "create":
        result = create_notebook(sys.argv[2])
    elif action == "add_source":
        result = add_source(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else "")
    elif action == "get_active":
        result = get_active()
    print(json.dumps(result, ensure_ascii=False))