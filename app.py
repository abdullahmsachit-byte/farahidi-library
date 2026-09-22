import os, json, shutil, secrets
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory, session

ROOT=Path(__file__).resolve().parent
DATA=ROOT/"books.json"
UP=ROOT/"static"/"uploads"; UP.mkdir(parents=True,exist_ok=True)
app=Flask(__name__,static_folder="static")
app.secret_key=os.environ.get("SECRET_KEY", secrets.token_hex(32))
ADMIN_PASSWORD=os.environ.get("ADMIN_PASSWORD","farahidi2026")

def load():
    try:return json.loads(DATA.read_text(encoding="utf-8"))
    except:return []
def save(x): DATA.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding="utf-8")
def admin(): return bool(session.get("admin"))

@app.get("/")
def index(): return send_from_directory(ROOT,"index.html")
@app.get("/api/books")
def books(): return jsonify(load())
@app.get("/api/admin")
def status(): return jsonify({"admin":admin()})
@app.post("/api/login")
def login():
    if request.form.get("password","")==ADMIN_PASSWORD:
        session["admin"]=True; return jsonify({"ok":True})
    return jsonify({"ok":False,"error":"كلمة السر غير صحيحة"}),403
@app.post("/api/logout")
def logout(): session.clear(); return jsonify({"ok":True})

@app.post("/api/save")
def api_save():
    if not admin(): return jsonify({"ok":False,"error":"غير مخول"}),403
    books=load(); bid=request.form.get("id","")
    old=next((b for b in books if str(b.get("id"))==bid),None)
    image=old.get("image","") if old else ""
    fi=request.files.get("image")
    if fi and fi.filename:
        ext=Path(fi.filename).suffix.lower() or ".jpg"
        name=f"{secrets.token_hex(10)}{ext}"; fi.save(UP/name); image="static/uploads/"+name
    if old: b=old
    else:
        nid=max([int(x.get("id",0)) for x in books]+[0])+1
        b={"id":nid}; books.append(b)
    try: stage=int(request.form.get("stage","1"))
    except: stage=1
    b.update({"dept":request.form.get("dept",""),"stage":stage,"subject":request.form.get("subject",""),
              "teacher":request.form.get("teacher",""),"price":request.form.get("price",""),
              "code":request.form.get("code",""),"image":image})
    save(books); return jsonify({"ok":True})

@app.post("/api/delete")
def api_delete():
    if not admin(): return jsonify({"ok":False,"error":"غير مخول"}),403
    bid=request.form.get("id",""); books=[b for b in load() if str(b.get("id"))!=bid]
    save(books); return jsonify({"ok":True})

if __name__=="__main__":
    app.run(host="0.0.0.0",port=int(os.environ.get("PORT","8000")))
