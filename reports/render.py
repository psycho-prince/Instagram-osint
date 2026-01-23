import json
import os

def save_reports(data, username, json_path=None, md_path=None):
    if json_path:
        with open(json_path, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"[+] JSON report saved to {json_path}")
    
    if md_path:
        with open(md_path, 'w') as f:
            f.write(f"# OSINT Report for {username}\n\n")
            f.write(json.dumps(data, indent=2))
        print(f"[+] Markdown report saved to {md_path}")

