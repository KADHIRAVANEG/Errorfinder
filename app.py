from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import os
import tempfile
import traceback

# ------------------------------
# Initialize Flask app
# ------------------------------
app = Flask(__name__)
CORS(app)  # Enable CORS for all domains

# ------------------------------
# Utility function: Run a system command safely
# ------------------------------
def run_command(command, input_text=None, cwd=None):
    """
    Executes a system command safely and returns stdout, stderr, and exit code.
    """
    try:
        result = subprocess.run(
            command,
            input=input_text.encode() if input_text else None,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10,
            cwd=cwd  # run in the temporary directory
        )
        return result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        return "", "Execution timed out.", 124
    except Exception as e:
        return "", f"Error: {str(e)}", 1

# ------------------------------
# Route: Health Check
# ------------------------------
@app.route('/')
def home():
    """
    Simple route to check if backend and Java are available.
    """
    java_path = subprocess.getoutput("which java")
    javac_path = subprocess.getoutput("which javac")

    return jsonify({
        "status": "JDK Backend Running Successfully",
        "java": java_path if java_path else "Not found",
        "javac": javac_path if javac_path else "Not found"
    })

# ------------------------------
# Route: Analyze and execute code
# ------------------------------
@app.route('/analyze', methods=['POST'])
def analyze_code():
    try:
        data = request.get_json()
        language = data.get("language", "").lower()
        code = data.get("code", "")

        if not code or not language:
            return jsonify({"error": "Missing code or language"}), 400

        # Handle HTML and JavaScript
        if language in ["html", "js", "javascript"]:
            return jsonify({
                "output": "HTML/JS code received successfully (frontend handles rendering).",
                "language": language,
                "error": "",
                "status": "success"
            })

        # Create a temporary working directory for each request
        with tempfile.TemporaryDirectory() as temp_dir:
            # Python
            if language == "python":
                file_path = os.path.join(temp_dir, "program.py")
                with open(file_path, "w") as f:
                    f.write(code)
                stdout, stderr, code_status = run_command(["python3", file_path], cwd=temp_dir)

            # C
            elif language == "c":
                file_path = os.path.join(temp_dir, "program.c")
                exe_path = os.path.join(temp_dir, "program")
                with open(file_path, "w") as f:
                    f.write(code)
                compile_out, compile_err, compile_status = run_command(["gcc", file_path, "-o", exe_path], cwd=temp_dir)
                if compile_status != 0:
                    return jsonify({"output": "", "error": compile_err.strip(), "language": language, "status": "error"}), 400
                stdout, stderr, code_status = run_command([exe_path], cwd=temp_dir)

            # C++
            elif language == "cpp":
                file_path = os.path.join(temp_dir, "program.cpp")
                exe_path = os.path.join(temp_dir, "program")
                with open(file_path, "w") as f:
                    f.write(code)
                compile_out, compile_err, compile_status = run_command(["g++", file_path, "-o", exe_path], cwd=temp_dir)
                if compile_status != 0:
                    return jsonify({"output": "", "error": compile_err.strip(), "language": language, "status": "error"}), 400
                stdout, stderr, code_status = run_command([exe_path], cwd=temp_dir)

            # Java
            elif language == "java":
                file_path = os.path.join(temp_dir, "Main.java")
                with open(file_path, "w") as f:
                    f.write(code)
                compile_out, compile_err, compile_status = run_command(["javac", file_path], cwd=temp_dir)
                if compile_status != 0:
                    return jsonify({"output": "", "error": compile_err.strip(), "language": language, "status": "error"}), 400
                stdout, stderr, code_status = run_command(["java", "-cp", temp_dir, "Main"], cwd=temp_dir)

            else:
                return jsonify({"error": f"Unsupported language: {language}"}), 400

        return jsonify({
            "language": language,
            "output": stdout.strip() if stdout else "",
            "error": stderr.strip() if stderr else "",
            "status": "success" if code_status == 0 else "error"
        })

    except Exception as e:
        print("❌ Exception during analyze_code:", traceback.format_exc())
        return jsonify({
            "error": str(e),
            "output": "",
            "language": "",
            "status": "error"
        }), 500

# ------------------------------
# Main entry point
# ------------------------------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 1000))
    print(f"🚀 Starting Flask app on port {port} ...")
    app.run(host='0.0.0.0', port=port, debug=True)