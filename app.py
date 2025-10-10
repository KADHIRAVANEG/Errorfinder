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
def run_command(command, input_text=None):
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
            timeout=10
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
    """
    Accepts JSON:
    {
        "language": "python" | "c" | "cpp" | "java" | "html" | "js",
        "code": "source code here"
    }
    Returns the program output or any compilation/runtime errors.
    """
    try:
        data = request.get_json()
        language = data.get("language", "").lower()
        code = data.get("code", "")

        if not code or not language:
            return jsonify({"error": "Missing code or language"}), 400

        # ------------------------------
        # Handle HTML and JavaScript directly
        # ------------------------------
        if language in ["html", "js", "javascript"]:
            return jsonify({
                "output": "HTML/JS code received successfully (frontend handles rendering).",
                "language": language
            })

        # ------------------------------
        # Create a temporary working directory
        # ------------------------------
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)

            # ------------------------------
            # Python Execution
            # ------------------------------
            if language == "python":
                with open("program.py", "w") as f:
                    f.write(code)
                stdout, stderr, code_status = run_command(["python3", "program.py"])
            
            # ------------------------------
            # C Execution
            # ------------------------------
            elif language == "c":
                with open("program.c", "w") as f:
                    f.write(code)
                run_command(["gcc", "program.c", "-o", "program"])
                stdout, stderr, code_status = run_command(["./program"])
            
            # ------------------------------
            # C++ Execution
            # ------------------------------
            elif language == "cpp":
                with open("program.cpp", "w") as f:
                    f.write(code)
                run_command(["g++", "program.cpp", "-o", "program"])
                stdout, stderr, code_status = run_command(["./program"])
            
            # ------------------------------
            # Java Execution
            # ------------------------------
            elif language == "java":
                with open("Main.java", "w") as f:
                    f.write(code)
                compile_out, compile_err, compile_status = run_command(["javac", "Main.java"])
                if compile_status != 0:
                    return jsonify({"error": compile_err}), 400
                stdout, stderr, code_status = run_command(["java", "Main"])
            
            else:
                return jsonify({"error": f"Unsupported language: {language}"}), 400

        # ------------------------------
        # Prepare and return final output
        # ------------------------------
        return jsonify({
            "language": language,
            "output": stdout.strip(),
            "error": stderr.strip(),
            "status": "success" if code_status == 0 else "error"
        })

    except Exception as e:
        print("❌ Exception during analyze_code:", traceback.format_exc())
        return jsonify({"error": str(e)}), 500


# ------------------------------
# Main entry point
# ------------------------------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 1000))
    print(f"🚀 Starting Flask app on port {port} ...")
    app.run(host='0.0.0.0', port=port, debug=True)
