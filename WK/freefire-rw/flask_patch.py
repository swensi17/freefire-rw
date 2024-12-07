import sys
import os

def patch_flask():
    # Find Flask installation directory
    flask_dir = None
    for path in sys.path:
        helpers_path = os.path.join(path, 'flask', 'helpers.py')
        if os.path.exists(helpers_path):
            flask_dir = os.path.dirname(helpers_path)
            break
    
    if not flask_dir:
        print("Could not find Flask installation")
        return False

    # Patch helpers.py
    helpers_path = os.path.join(flask_dir, 'helpers.py')
    with open(helpers_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace url_quote with quote
    content = content.replace('from werkzeug.urls import url_quote', 'from werkzeug.urls import quote as url_quote')
    
    with open(helpers_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Successfully patched Flask")
    return True

if __name__ == '__main__':
    patch_flask()
