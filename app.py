from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import os
import tempfile
import traceback
import re

app = Flask(__name__)
CORS(app)

# ------------------------------
# Helper Function: Run Commands Safely
# ------------------------------
def run_command(command, input_text=None):
    try:
        result = subprocess.run(
            command,
            input=input_text.encode() if input_text else None,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10
        )
        return result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        return "", "⏱ Execution timed out.", 124
    except Exception as e:
        return "", f"⚠ Error: {str(e)}", 1


# ------------------------------
# Root Route
# ------------------------------
@app.route('/')
def home():
    java_path = subprocess.getoutput("which java")
    javac_path = subprocess.getoutput("which javac")
    return jsonify({
        "status": "✅ Backend Running Successfully",
        "java": java_path or "Not found",
        "javac": javac_path or "Not found"
    })


# ------------------------------
# Analyzer Route
# ------------------------------
@app.route('/analyze', methods=['POST'])
def analyze_code():
    try:
        data = request.get_json()
        language = data.get("language", "").lower()
        code = data.get("code", "").strip()

        if not code or not language:
            return jsonify({"error": "⚠ Missing code or language."}), 400

        # ===============================
        # FRONTEND LANGUAGES
        # ===============================

        # ---------- HTML ----------
        if language == "html":
            from bs4 import Beautiful
            try:
        # Parse the HTML to check for syntax issues
            soup = BeautifulSoup(code, "html.parser")
        # If BeautifulSoup parses without exception, consider it valid
            return jsonify({
            "language": "html",
            "output": code,
            "error": "",
            "status": "success"
            })
        except Exception as e:
            return jsonify({
                "language": "html",
                "output": "",
                "error": f"❌ HTML parsing error:\n{str(e)}",
                "status": "error"
            })
        # ---------- JAVASCRIPT ----------
        if language in ["js", "javascript"]:
            with tempfile.TemporaryDirectory() as temp_dir:
                js_path = os.path.join(temp_dir, "main.js")
                with open(js_path, "w") as f:
                    f.write(code)

                # Syntax check
                _, stderr, status = run_command(["node", "--check", js_path])
                if status != 0:
                    return jsonify({
                        "language": "javascript",
                        "output": "",
                        "error": f"❌ JS syntax error:\n{stderr}",
                        "status": "error"
                    })

                # Execute valid JS
                stdout, stderr, exec_status = run_command(["node", js_path])
                return jsonify({
                    "language": "javascript",
                    "output": stdout.strip(),
                    "error": stderr.strip(),
                    "status": "success" if exec_status == 0 else "error"
                })

        # ---------- HTML + JS ----------
        if "<script>" in code and "</script>" in code:
            return jsonify({
                "language": "html+js",
                "output": code,
                "error": "",
                "status": "success"
            })

        # ===============================
        # BACKEND LANGUAGES
        # ===============================
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            stdout = stderr = ""
            code_status = 0

            # ---- Python ----
            if language == "python":
                with open("main.py", "w") as f:
                    f.write(code)
                stdout, stderr, code_status = run_command(["python3", "main.py"])

            # ---- C ----
            elif language == "c":
                with open("main.c", "w") as f:
                    f.write(code)
                _, compile_err, compile_status = run_command(["gcc", "main.c", "-o", "main"])
                if compile_status != 0:
                    return jsonify({"error": compile_err}), 400
                stdout, stderr, code_status = run_command(["./main"])

            # ---- C++ ----
            elif language == "cpp":
                with open("main.cpp", "w") as f:
                    f.write(code)
                _, compile_err, compile_status = run_command(["g++", "main.cpp", "-o", "main"])
                if compile_status != 0:
                    return jsonify({"error": compile_err}), 400
                stdout, stderr, code_status = run_command(["./main"])

            # ---- Java (Dynamic Class + Syntax Check) ----
            elif language == "java":
                match = re.search(r'public\s+class\s+(\w+)', code)
                class_name = match.group(1) if match else "Main"
                file_name = f"{class_name}.java"

                with open(file_name, "w") as f:
                    f.write(code)

                # Compile for syntax check
                _, compile_err, compile_status = run_command(["javac", file_name])
                if compile_status != 0:
                    return jsonify({
                        "language": "java",
                        "output": "",
                        "error": f"❌ Java syntax error:\n{compile_err}",
                        "status": "error"
                    })

                # Execute if syntax OK
                stdout, stderr, code_status = run_command(["java", "-cp", ".", class_name])

            else:
                return jsonify({"error": f"❌ Unsupported language: {language}"}), 400

        # ===============================
        # Final Response
        # ===============================
        return jsonify({
            "language": language,
            "output": stdout.strip(),
            "error": stderr.strip(),
            "status": "success" if code_status == 0 else "error"
        })

    except Exception as e:
        print("❌ Exception:", traceback.format_exc())
        return jsonify({"error": str(e)}), 500


# ------------------------------
# Start Flask Server
# ------------------------------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Starting Flask backend on port {port} ...")
    app.run(host='0.0.0.0', port=port, debug=True)
