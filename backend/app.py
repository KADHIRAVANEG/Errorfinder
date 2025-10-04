# --------------------------- Imports ---------------------------
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import subprocess, tempfile, os, re, shutil, logging
from bs4 import BeautifulSoup

# --------------------------- App Setup ---------------------------
app = Flask(__name__)
CORS(app, origins=["*"], supports_credentials=False)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB limit

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s [%(levelname)s] %(message)s')

# --------------------------- Code Analyzer ---------------------------
class CodeAnalyzer:
    """Analyze code for syntax errors and provide suggestions."""

    def __init__(self):
        self.language_configs = {
            'python': {
                'extension': '.py',
                'command': ['python3', '-m', 'py_compile'],
                'error_patterns': [
                    (r'SyntaxError:', 'Syntax Error'),
                    (r'IndentationError:', 'Indentation Error'),
                    (r'NameError:', 'Name Error'),
                    (r'TypeError:', 'Type Error'),
                    (r'ValueError:', 'Value Error'),
                    (r'RuntimeError:', 'Runtime Error')
                ],
                'suggestions': [
                    '💡 Use f-strings for formatting strings',
                    '💡 Follow PEP8 style guide',
                    '💡 Add type hints for readability',
                    '💡 Avoid global variables when possible',
                    '💡 Catch exceptions with try-except',
                    '💡 Modularize code into functions/classes'
                ]
            },
            'c': {
                'extension': '.c',
                'command': ['gcc', '-fsyntax-only'],
                'error_patterns': [(r'error:', 'Compilation Error'), (r'warning:', 'Warning')],
                'suggestions': [
                    '💡 Free dynamically allocated memory',
                    '💡 Check return values of functions',
                    '💡 Use meaningful variable names',
                    '💡 Split code into header and source files'
                ]
            },
            'cpp': {
                'extension': '.cpp',
                'command': ['g++', '-fsyntax-only'],
                'error_patterns': [(r'error:', 'Compilation Error'), (r'warning:', 'Warning')],
                'suggestions': [
                    '💡 Use smart pointers instead of raw pointers',
                    '💡 Apply RAII for resource management',
                    '💡 Apply const correctness',
                    '💡 Handle exceptions properly'
                ]
            },
            'java': {
                'extension': '.java',
                'command': ['javac'],
                'error_patterns': [(r'error:', 'Compilation Error'), (r'warning:', 'Warning')],
                'suggestions': [
                    '💡 Follow Java naming conventions',
                    '💡 Use StringBuilder for concatenation',
                    '💡 Handle exceptions properly',
                    '💡 Keep classes small and focused'
                ]
            },
            'js': {
                'extension': '.js',
                'command': ['node', '--check'],
                'error_patterns': [(r'SyntaxError:', 'Syntax Error'), (r'ReferenceError:', 'Reference Error')],
                'suggestions': [
                    '💡 Use strict mode', '💡 Prefer const/let over var',
                    '💡 Validate inputs before use', '💡 Use try-catch'
                ]
            },
            'bash': {
                'extension': '.sh',
                'command': ['bash', '-n'],
                'error_patterns': [(r'syntax error', 'Syntax Error')],
                'suggestions': [
                    '💡 Start script with #!/bin/bash',
                    '💡 Quote variables properly',
                    '💡 Use set -e to catch errors'
                ]
            },
            'html': {
                'extension': '.html',
                'command': None,
                'error_patterns': [],
                'suggestions': [
                    '💡 Include <!DOCTYPE html> at the top',
                    '💡 Ensure <html>, <head>, and <body> exist',
                    '💡 Close all tags properly'
                ]
            }
        }

        self.available_tools = self._check_available_tools()

    def _check_available_tools(self):
        tools = {}
        for lang, cfg in self.language_configs.items():
            tools[lang] = True if cfg['command'] is None else shutil.which(cfg['command'][0]) is not None
        return tools

    def analyze_code(self, code, language):
        language = language.lower()
        if language not in self.language_configs:
            return {'status': 'error', 'message': f'Language {language} not supported'}

        cfg = self.language_configs[language]

        if not self.available_tools.get(language, False):
            return {'status': 'error', 'message': f'{language.upper()} tool not installed', 'suggestions': cfg['suggestions']}

        if language == 'html':
            return self._analyze_html(code)

        with tempfile.NamedTemporaryFile(mode='w', suffix=cfg['extension'], delete=False) as tmp:
            tmp.write(code)
            tmp_path = tmp.name

        try:
            if language == 'java':
                cls = self._extract_java_class(code)
                if cls:
                    java_file = os.path.join(os.path.dirname(tmp_path), f'{cls}.java')
                    os.rename(tmp_path, java_file)
                    tmp_path = java_file

            cmd = cfg['command'] + [tmp_path] if cfg['command'] else None
            if cmd:
                logging.info(f'Running command: {" ".join(cmd)}')
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
                if result.returncode == 0:
                    return {'status': 'success', 'message': f'✅ No syntax errors in {language.upper()}', 'suggestions': cfg['suggestions']}
                else:
                    errors = self._parse_errors(result.stderr, cfg['error_patterns'])
                    return {'status': 'error', 'message': f'❌ Errors in {language.upper()}', 'errors': errors, 'suggestions': self._get_error_tips(errors, language)}
        except subprocess.TimeoutExpired:
            return {'status': 'error', 'message': 'Code analysis timed out', 'suggestions': cfg['suggestions']}
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def _analyze_html(self, code):
        errors = []
        soup = BeautifulSoup(code, 'html.parser')
        if not soup.find('html'): errors.append('Missing <html> tag')
        if not soup.find('head'): errors.append('Missing <head> tag')
        if not soup.find('body'): errors.append('Missing <body> tag')
        status = 'error' if errors else 'success'
        message = '❌ HTML issues found' if errors else '✅ HTML looks good'
        suggestions = self.language_configs['html']['suggestions'] if errors else ['💡 Add semantic HTML elements', '💡 Add meta tags', '💡 Ensure accessibility']
        return {'status': status, 'message': message, 'errors': errors, 'suggestions': suggestions}

    def _parse_errors(self, stderr, patterns):
        errs = []
        for line in stderr.splitlines():
            for p, t in patterns:
                if re.search(p, line):
                    errs.append({'type': t, 'message': line.strip()})
                    break
            else:
                if ':' in line and ('error' in line.lower() or 'warning' in line.lower()):
                    errs.append({'type': 'General Error', 'message': line.strip()})
        return errs

    def _get_error_tips(self, errors, language):
        tips = []
        for e in errors:
            msg = e['message'].lower()
            if 'syntax' in msg: tips.append('💡 Check brackets, quotes, semicolons')
            elif 'indent' in msg: tips.append('💡 Fix indentation consistently')
            elif 'name' in msg and 'not defined' in msg: tips.append('💡 Check variable names and declarations')
            elif 'type' in msg: tips.append('💡 Check variable types and conversions')
            else: tips.append('💡 Review the error message carefully')
        if len(tips) < 5:
            tips.extend(self.language_configs[language]['suggestions'][:6 - len(tips)])
        return tips

    def _extract_java_class(self, code):
        m = re.search(r'public\s+class\s+(\w+)', code)
        return m.group(1) if m else None


# ------------------- Instantiate Analyzer ---------------------------
analyzer = CodeAnalyzer()

# ------------------- Routes ---------------------------
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json()
        code = data.get('code', '').strip()
        language = data.get('language', '').lower()
        if not code:
            return jsonify({'status': 'error', 'message': '⚠️ Provide code'}), 400
        if not language:
            return jsonify({'status': 'error', 'message': '⚠️ Provide language'}), 400
        return jsonify(analyzer.analyze_code(code, language))
    except Exception as e:
        logging.error(str(e))
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/tools')
def tools():
    return jsonify({'available_tools': analyzer.available_tools, 'languages': list(analyzer.language_configs.keys())})


@app.route('/suggestions/<language>')
def suggestions(language):
    language = language.lower()
    if language not in analyzer.language_configs:
        return jsonify({'status': 'error', 'message': 'Language not supported'}), 400
    return jsonify({'language': language, 'suggestions': analyzer.language_configs[language]['suggestions']})


@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'service': 'Code Error Finder API'})


@app.route('/favicon.ico')
def favicon():
    return '', 204


# ------------------- Run App ---------------------------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
