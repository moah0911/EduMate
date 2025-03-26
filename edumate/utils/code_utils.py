"""Utility functions for code processing and execution."""
import os
import subprocess
import tempfile
import re
import time


def run_code(code, language, timeout=5):
    """Run code in a safe environment and return the result."""
    if not code or not language:
        return {
            'success': False,
            'output': 'No code or language specified',
            'error': 'Invalid input'
        }
    
    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=get_file_extension(language)) as temp:
        temp_filename = temp.name
        try:
            # Write code to the file
            temp.write(code.encode('utf-8'))
            temp.flush()
            
            # Run the code based on the language
            result = execute_code(temp_filename, language, timeout)
            
            return result
        except Exception as e:
            return {
                'success': False,
                'output': '',
                'error': str(e)
            }
        finally:
            # Clean up
            try:
                os.unlink(temp_filename)
            except:
                pass


def get_file_extension(language):
    """Get the file extension for a language."""
    extensions = {
        'python': '.py',
        'java': '.java',
        'cpp': '.cpp',
        'c': '.c',
        'javascript': '.js',
        'html': '.html',
        'css': '.css',
        'php': '.php'
    }
    return extensions.get(language.lower(), '.txt')


def execute_code(filename, language, timeout):
    """Execute code in a specific language."""
    commands = {
        'python': ['python', filename],
        'java': ['java', filename],
        'cpp': ['g++', filename, '-o', filename + '.out', '&&', filename + '.out'],
        'c': ['gcc', filename, '-o', filename + '.out', '&&', filename + '.out'],
        'javascript': ['node', filename],
        'php': ['php', filename]
    }
    
    cmd = commands.get(language.lower())
    if not cmd:
        return {
            'success': False,
            'output': '',
            'error': f'Unsupported language: {language}'
        }
    
    try:
        # Execute the command with a timeout
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        try:
            stdout, stderr = process.communicate(timeout=timeout)
            
            return {
                'success': process.returncode == 0,
                'output': stdout,
                'error': stderr
            }
        except subprocess.TimeoutExpired:
            process.kill()
            return {
                'success': False,
                'output': '',
                'error': f'Execution timed out after {timeout} seconds'
            }
    except Exception as e:
        return {
            'success': False,
            'output': '',
            'error': str(e)
        }


def check_code_style(code, language):
    """Check code style and return issues."""
    if not code or not language:
        return {
            'success': False,
            'issues': ['No code or language specified']
        }
    
    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=get_file_extension(language)) as temp:
        temp_filename = temp.name
        try:
            # Write code to the file
            temp.write(code.encode('utf-8'))
            temp.flush()
            
            # Check style based on language
            if language.lower() == 'python':
                return check_python_style(temp_filename)
            elif language.lower() in ['java', 'cpp', 'c']:
                return check_c_style(temp_filename, language.lower())
            else:
                return {
                    'success': True,
                    'issues': []
                }
        except Exception as e:
            return {
                'success': False,
                'issues': [str(e)]
            }
        finally:
            # Clean up
            try:
                os.unlink(temp_filename)
            except:
                pass


def check_python_style(filename):
    """Check Python code style using flake8."""
    try:
        result = subprocess.run(
            ['flake8', filename],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        issues = []
        if result.stdout:
            # Parse flake8 output
            for line in result.stdout.split('\n'):
                if line.strip():
                    issues.append(line)
        
        return {
            'success': len(issues) == 0,
            'issues': issues
        }
    except Exception as e:
        return {
            'success': False,
            'issues': [str(e)]
        }


def check_c_style(filename, language):
    """Check C/C++/Java code style."""
    # This is a simplified style checker
    issues = []
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            code = f.read()
            
            # Check for consistent indentation
            if not check_indentation(code):
                issues.append("Inconsistent indentation")
            
            # Check for long lines
            if has_long_lines(code):
                issues.append("Lines longer than 100 characters")
            
            # Check for naming conventions
            if not check_naming_conventions(code, language):
                issues.append("Naming conventions not followed")
            
            # Check for commented code
            if has_commented_code(code):
                issues.append("Contains commented out code")
        
        return {
            'success': len(issues) == 0,
            'issues': issues
        }
    except Exception as e:
        return {
            'success': False,
            'issues': [str(e)]
        }


def check_indentation(code):
    """Check if code has consistent indentation."""
    lines = code.split('\n')
    indent_pattern = re.compile(r'^(\s*)\S')
    indents = []
    
    for line in lines:
        if line.strip():
            match = indent_pattern.match(line)
            if match:
                indent = match.group(1)
                if indent and indent not in indents:
                    indents.append(indent)
    
    # If we have more than one type of indent, check if they're multiples
    if len(indents) > 1:
        # Sort by length
        indents.sort(key=len)
        base_indent = indents[0]
        
        for indent in indents[1:]:
            if len(indent) % len(base_indent) != 0:
                return False
    
    return True


def has_long_lines(code, max_length=100):
    """Check if code has lines longer than max_length."""
    lines = code.split('\n')
    for line in lines:
        if len(line) > max_length:
            return True
    return False


def check_naming_conventions(code, language):
    """Check if code follows naming conventions for the language."""
    # This is a simplified check
    if language == 'java':
        # Check for camelCase methods and variables
        method_pattern = re.compile(r'(public|private|protected)?\s+\w+\s+([a-zA-Z0-9_]+)\s*\(')
        methods = method_pattern.findall(code)
        for _, method_name in methods:
            if not method_name[0].islower():
                return False
    
    elif language in ['c', 'cpp']:
        # Check for snake_case functions
        function_pattern = re.compile(r'\w+\s+([a-zA-Z0-9_]+)\s*\(')
        functions = function_pattern.findall(code)
        for function_name in functions:
            if '_' not in function_name and not function_name.islower():
                return False
    
    return True


def has_commented_code(code):
    """Check if code has commented out code blocks."""
    # Look for comment lines that contain code-like patterns
    comment_pattern = re.compile(r'^\s*//.*[;{}()].*$|^\s*/\*.*[;{}()].*\*/$', re.MULTILINE)
    return bool(comment_pattern.search(code)) 