from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import os
import tempfile
import traceback

# ------------------------------
# Initialize Flask App
# ------------------------------
app = Flask(__name__)
CORS(app)

# ------------------------------
# Helper Function: Run Commands Safely
# ------------------------------
def run_command(command, input_text=None):
    """Execute a system command with optional input and timeout."""
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
# Health Check Route
# ------------------------------
@app.route('/')
def home():
    """Check backend health and Java availability."""
    java_path = subprocess.getoutput("which java")
    javac_path = subprocess.getoutput("which javac")
    return jsonify({
        "status": "✅ Backend Running Successfully",
        "java": java_path or "Not found",
        "javac": javac_path or "Not found"
    })


# ------------------------------
# Main Analyzer Route
# ------------------------------
@app.route('/analyze', methods=['POST'])
def analyze_code():
    """Analyze or execute submitted code based on language."""
    try:
        data = request.get_json()
        language = data.get("language", "").lower()
        code = data.get("code", "").strip()

        if not code or not language:
            return jsonify({"error": "⚠ Missing code or language."}), 400

        # Skip execution for frontend languages
        if language in ["html", "js", "javascript"]:
            return jsonify({
                "language": language,
                "output": "✅ HTML/JS code received successfully (frontend handles rendering).",
                "error": "",
                "status": "success"
            })

        # Use a safe temporary directory for compilation & execution
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

            # ---- Java ----
            elif language == "java":
                with open("Main.java", "w") as f:
                    f.write(code)
                _, compile_err, compile_status = run_command(["javac", "Main.java"])
                if compile_status != 0:
                    return jsonify({"error": compile_err}), 400
                stdout, stderr, code_status = run_command(["java", "-cp", ".", "Main"])

            else:
                return jsonify({"error": f"❌ Unsupported language: {language}"}), 400

        # ---- Prepare Final Response ----
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
# Main Entry
# ------------------------------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Starting Flask backend on port {port} ...")
    app.run(host='0.0.0.0', port=port, debug=True)
