# Overview

Errorfinder is a web-based multi-language code error detection and analysis tool that supports multiple programming languages (Python, C, C++, JavaScript, HTML, with Java support available when javac is installed). The application uses a Flask backend with gunicorn WSGI server for production deployment and an HTML/CSS frontend with JavaScript for dynamic API communication. The tool provides real-time syntax error detection and intelligent suggestions for code improvement.

## Current Status

The application is fully functional and deployed on Replit with the following components:
- **Backend**: Flask API with multi-language code analysis using system compilers
- **Frontend**: Single-page HTML application with responsive design and real-time analysis
- **Server**: Gunicorn WSGI server for production-grade deployment
- **Toolchain Detection**: Automatic detection of available programming language tools with graceful fallbacks

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
- **Technology**: HTML/CSS hosted on GitHub Pages
- **Design**: Single-page application with responsive layout using flexbox
- **UI Components**: Code editor interface, file upload functionality, and results display
- **Styling**: Custom CSS with gradient backgrounds and modern UI elements

## Backend Architecture
- **Framework**: Flask (Python) hosted on Replit
- **Security**: CORS restricted to same origin, 1MB payload limit
- **Code Analysis Engine**: `CodeAnalyzer` class that handles multiple programming languages
- **Language Support**: Configurable language processors with specific compilers/interpreters
- **Error Processing**: Pattern-based error extraction from compiler/interpreter output

## Code Analysis Pipeline
1. **Language Detection**: Automatic detection based on file extension or code patterns
2. **Compilation/Analysis**: Uses respective compilers (gcc, g++, javac) or interpreters (python3)
3. **Error Extraction**: Regex-based pattern matching to identify error types
4. **ML Classification**: Machine Learning model classifies errors and suggests fixes
5. **Result Formatting**: Structured output with error type, line number, and suggested solutions

## File Processing
- **Temporary Files**: Uses Python's `tempfile` module for secure file handling
- **Language Configurations**: Dictionary-based configuration for each supported language
- **Compiler Integration**: Direct subprocess calls to system compilers and interpreters

# External Dependencies

## System Dependencies
- **GCC/G++**: C and C++ compilation
- **Java Compiler (javac)**: Java code analysis
- **Python 3**: Python code execution and py_compile module

## Python Libraries
- **Flask**: Web framework for API endpoints
- **Flask-CORS**: Cross-origin resource sharing management
- **subprocess**: System command execution
- **tempfile**: Secure temporary file handling
- **shutil**: File operations

## Hosting Services
- **Replit**: Backend Flask application hosting
- **GitHub Pages**: Frontend static site hosting

## Machine Learning Component
- **Custom ML Model**: Trained on error logs for error classification and fix recommendations
- **Error Pattern Recognition**: Regex-based error type identification system