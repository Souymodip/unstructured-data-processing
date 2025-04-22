import io
import traceback
from contextlib import redirect_stdout, redirect_stderr
from typing import Dict, Any, Optional


def execute_python_code(code: str, timeout: int = 30, globals_dict: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Execute a Python code string and return the results.

    Args:
        code (str): The Python code to execute.
        timeout (int, optional): Maximum execution time in seconds. Defaults to 30.
        globals_dict (Dict[str, Any], optional): Dictionary of global variables to include.
            Defaults to None (empty globals).

    Returns:
        Dict[str, Any]: A dictionary containing:
            - 'success': Boolean indicating if execution was successful
            - 'stdout': Captured standard output
            - 'stderr': Captured error output if an exception occurred
            - 'exception': Exception information if an error occurred
            - 'globals': Dictionary of global variables after execution (if successful)
    """
    # Initialize results dictionary
    result = {
        'success': False,
        'stdout': '',
        'stderr': '',
        'exception': None,
        'globals': {}
    }

    # Prepare globals dictionary
    if globals_dict is None:
        globals_dict = {}

    # Create string buffers for stdout and stderr
    stdout_buffer = io.StringIO()
    stderr_buffer = io.StringIO()

    try:
        # Set a timeout if supported
        # Note: This is a simplified approach; in production, you might want
        # to use multiprocessing or threading to implement timeouts

        # Execute the code with redirected output
        with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
            # Execute the code
            exec(code, globals_dict)

        # Capture stdout and update result
        result['stdout'] = stdout_buffer.getvalue()
        result['success'] = True

        # Filter out builtins and modules from globals
        filtered_globals = {
            k: v for k, v in globals_dict.items()
            if not k.startswith('__') and not k.endswith('__')
        }
        result['globals'] = filtered_globals

    except Exception as e:
        # Capture the exception details
        result['exception'] = {
            'type': type(e).__name__,
            'message': str(e),
            'traceback': traceback.format_exc()
        }
        result['stderr'] = stderr_buffer.getvalue()

    return result


def test():
    # Sample code to be executed
    code_to_run = """
    import math

    def calculate_circle_area(radius):
        return math.pi * radius ** 2

    # Test the function
    radius = 5
    area = calculate_circle_area(radius)
    print(f"The area of a circle with radius {radius} is {area:.2f}")
    """

    # Execute the code
    result = execute_python_code(code_to_run)
    print(result)


if __name__ == "__main__":
    test()
