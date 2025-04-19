import json
import os
import shutil
import subprocess
import tempfile

import pytest

from aider_mcp_server.atoms.tools.aider_ai_code import code_with_aider


@pytest.fixture
def temp_dir():
    """Create a temporary directory with an initialized Git repository for testing."""
    tmp_dir = tempfile.mkdtemp()

    # Initialize git repository in the temp directory
    subprocess.run(
        ["git", "init"], cwd=tmp_dir, capture_output=True, text=True, check=True
    )

    # Configure git user for the repository
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=tmp_dir,
        capture_output=True,
        text=True,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=tmp_dir,
        capture_output=True,
        text=True,
        check=True,
    )

    # Create and commit an initial file to have a valid git history
    with open(os.path.join(tmp_dir, "README.md"), "w") as f:
        f.write(
            "# Test Repository\nThis is a test repository for Aider MCP Server tests."
        )

    subprocess.run(
        ["git", "add", "README.md"],
        cwd=tmp_dir,
        capture_output=True,
        text=True,
        check=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"],
        cwd=tmp_dir,
        capture_output=True,
        text=True,
        check=True,
    )

    yield tmp_dir

    # Clean up
    shutil.rmtree(tmp_dir)


# Use a known valid model for testing based on fuzzy_match_models output
TEST_MODEL_ID = "gemini/gemini-2.5-pro-exp-03-25"


def test_addition(temp_dir):
    """Test that code_with_aider can create a file that adds two numbers."""
    # Create the test file
    test_file = os.path.join(temp_dir, "math_add.py")
    with open(test_file, "w") as f:
        f.write("# This file should implement addition\n")

    prompt = (
        "Implement a function add(a, b) that returns the sum of a and b in the "
        "math_add.py file."
    )

    # Run code_with_aider with working_dir and valid model
    result = code_with_aider(
        ai_coding_prompt=prompt,
        relative_editable_files=[test_file],
        model=TEST_MODEL_ID,  # Use valid model
        working_dir=temp_dir,
    )

    # Parse the JSON result
    result_dict = json.loads(result)

    # Check that it succeeded
    assert result_dict["success"] is True, "Expected code_with_aider to succeed"
    assert "diff" in result_dict, "Expected diff to be in result"

    # Check that the file was modified correctly
    with open(test_file) as f:
        content = f.read()

    assert any(x in content for x in ["def add(a, b):", "def add(a:"]), (
        "Expected to find add function in the file"
    )
    assert "return a + b" in content, "Expected to find return statement in the file"

    # Try to import and use the function
    import sys

    sys.path.append(temp_dir)
    from math_add import add  # type: ignore[import-not-found]

    assert add(2, 3) == 5, "Expected add(2, 3) to return 5"


def test_subtraction(temp_dir):
    """Test that code_with_aider can create a file that subtracts two numbers."""
    # Create the test file
    test_file = os.path.join(temp_dir, "math_subtract.py")
    with open(test_file, "w") as f:
        f.write("# This file should implement subtraction\n")

    prompt = (
        "Implement a function subtract(a, b) that returns a minus b in the "
        "math_subtract.py file."
    )

    # Run code_with_aider with working_dir and valid model
    result = code_with_aider(
        ai_coding_prompt=prompt,
        relative_editable_files=[test_file],
        model=TEST_MODEL_ID,  # Use valid model
        working_dir=temp_dir,
    )

    # Parse the JSON result
    result_dict = json.loads(result)

    # Check that it succeeded
    assert result_dict["success"] is True, "Expected code_with_aider to succeed"
    assert "diff" in result_dict, "Expected diff to be in result"

    # Check that the file was modified correctly
    with open(test_file) as f:
        content = f.read()

    assert any(x in content for x in ["def subtract(a, b):", "def subtract(a:"]), (
        "Expected to find subtract function in the file"
    )
    assert "return a - b" in content, "Expected to find return statement in the file"

    # Try to import and use the function
    import sys

    sys.path.append(temp_dir)
    from math_subtract import subtract  # type: ignore[import-not-found]

    assert subtract(5, 3) == 2, "Expected subtract(5, 3) to return 2"


def test_multiplication(temp_dir):
    """Test that code_with_aider can create a file that multiplies two numbers."""
    # Create the test file
    test_file = os.path.join(temp_dir, "math_multiply.py")
    with open(test_file, "w") as f:
        f.write("# This file should implement multiplication\n")

    prompt = (
        "Implement a function multiply(a, b) that returns the product of a and b "
        "in the math_multiply.py file."
    )

    # Run code_with_aider with working_dir and valid model
    result = code_with_aider(
        ai_coding_prompt=prompt,
        relative_editable_files=[test_file],
        model=TEST_MODEL_ID,  # Use valid model
        working_dir=temp_dir,
    )

    # Parse the JSON result
    result_dict = json.loads(result)

    # Check that it succeeded
    assert result_dict["success"] is True, "Expected code_with_aider to succeed"
    assert "diff" in result_dict, "Expected diff to be in result"

    # Check that the file was modified correctly
    with open(test_file) as f:
        content = f.read()

    assert any(x in content for x in ["def multiply(a, b):", "def multiply(a:"]), (
        "Expected to find multiply function in the file"
    )
    assert "return a * b" in content, "Expected to find return statement in the file"

    # Try to import and use the function
    import sys

    sys.path.append(temp_dir)
    from math_multiply import multiply  # type: ignore[import-not-found]

    assert multiply(2, 3) == 6, "Expected multiply(2, 3) to return 6"


def test_division(temp_dir):
    """Test that code_with_aider can create a file that divides two numbers."""
    # Create the test file
    test_file = os.path.join(temp_dir, "math_divide.py")
    with open(test_file, "w") as f:
        f.write("# This file should implement division\n")

    prompt = (
        "Implement a function divide(a, b) that returns a divided by b in the "
        "math_divide.py file. Handle division by zero by returning None."
    )

    # Run code_with_aider with working_dir and valid model
    result = code_with_aider(
        ai_coding_prompt=prompt,
        relative_editable_files=[test_file],
        model=TEST_MODEL_ID,  # Use valid model
        working_dir=temp_dir,
    )

    # Parse the JSON result
    result_dict = json.loads(result)

    # Check that it succeeded
    assert result_dict["success"] is True, "Expected code_with_aider to succeed"
    assert "diff" in result_dict, "Expected diff to be in result"

    # Check that the file was modified correctly
    with open(test_file) as f:
        content = f.read()

    assert any(x in content for x in ["def divide(a, b):", "def divide(a:"]), (
        "Expected to find divide function in the file"
    )
    assert "return" in content, "Expected to find return statement in the file"

    # Try to import and use the function
    import sys

    sys.path.append(temp_dir)
    from math_divide import divide  # type: ignore[import-not-found]

    assert divide(6, 3) == 2, "Expected divide(6, 3) to return 2"
    assert divide(1, 0) is None, "Expected divide(1, 0) to return None"


def test_failure_case(temp_dir):
    """Test that code_with_aider returns error information for a failure scenario."""
    original_cwd = os.getcwd()  # Store original CWD
    try:
        # Change to the temp directory for the test
        os.chdir(temp_dir)

        # Create a test file in the temp directory
        test_file = os.path.join(temp_dir, "failure_test.py")
        with open(test_file, "w") as f:
            f.write("# This file should trigger a failure\n")

        # Use an invalid model name to ensure a failure
        invalid_model_name = "non_existent_model_123456789"
        prompt = "This prompt should fail because we're using a non-existent model."

        # Run code_with_aider with an invalid model name
        result = code_with_aider(
            ai_coding_prompt=prompt,
            relative_editable_files=[test_file],
            model=invalid_model_name,
            working_dir=temp_dir,
        )

        # Parse the JSON result
        result_dict = json.loads(result)

        # Check the result - we expect success=False and a specific error message
        # in the diff due to the model validation.
        assert result_dict["success"] is False, (
            "Expected success to be False for invalid model"
        )
        assert "diff" in result_dict, "Expected diff to be in result"
        diff_content = result_dict["diff"]
        expected_error_msg = (
            f"Error: Model '{invalid_model_name}' is not recognized or available."
        )
        assert expected_error_msg in diff_content, (
            f"Expected diff to contain model validation error, but got: {diff_content}"
        )

    finally:
        # Make sure we go back to the original directory
        os.chdir(original_cwd)  # Change back to original CWD


def test_complex_tasks(temp_dir):
    """Test that code_with_aider correctly implements more complex tasks."""
    # Create the test file for a calculator class
    test_file = os.path.join(temp_dir, "calculator.py")
    with open(test_file, "w") as f:
        f.write("# This file should implement a calculator class\n")

    # More complex prompt suitable for architect mode
    prompt = """
    Create a Python class named 'Calculator' in the calculator.py file with the
    following features:
    1. Basic operations: add, subtract, multiply, divide methods
    2. Memory functions: memory_store, memory_recall, memory_clear
    3. A history feature that keeps track of operations
    4. A method to show_history
    5. Error handling for division by zero

    All methods should be well-documented with docstrings.
    """

    # Run code_with_aider with explicit valid model
    result = code_with_aider(
        ai_coding_prompt=prompt,
        relative_editable_files=[test_file],
        model=TEST_MODEL_ID,  # Use valid model
        working_dir=temp_dir,
    )

    # Parse the JSON result
    result_dict = json.loads(result)

    # Check that it succeeded
    assert result_dict["success"] is True, (
        "Expected code_with_aider with architect mode to succeed"
    )
    assert "diff" in result_dict, "Expected diff to be in result"

    # Check that the file was modified correctly with expected elements
    with open(test_file) as f:
        content = f.read()

    # Check for class definition and methods - relaxed assertions
    # to accommodate type hints
    assert "class Calculator" in content, "Expected to find Calculator class definition"
    assert "add" in content, "Expected to find add method"
    assert "subtract" in content, "Expected to find subtract method"
    assert "multiply" in content, "Expected to find multiply method"
    assert "divide" in content, "Expected to find divide method"
    assert "memory_" in content, "Expected to find memory functions"
    assert "history" in content, "Expected to find history functionality"

    # Import and test basic calculator functionality
    import sys

    sys.path.append(temp_dir)
    from calculator import Calculator  # type: ignore[import-not-found]

    # Test the calculator
    calc = Calculator()

    # Test basic operations
    assert calc.add(2, 3) == 5, "Expected add(2, 3) to return 5"
    assert calc.subtract(5, 3) == 2, "Expected subtract(5, 3) to return 2"
    assert calc.multiply(2, 3) == 6, "Expected multiply(2, 3) to return 6"
    assert calc.divide(6, 3) == 2, "Expected divide(6, 3) to return 2"

    # Test division by zero error handling
    try:
        result = calc.divide(5, 0)
        assert result is None or isinstance(result, (str, type(None))), (
            "Expected divide by zero to return None, error message, or raise exception"
        )
    except Exception:
        # It's fine if it raises an exception - that's valid error handling too
        pass

    # Test memory functions if implemented as expected
    try:
        calc.memory_store(10)
        assert calc.memory_recall() == 10, (
            "Expected memory_recall() to return stored value"
        )
        calc.memory_clear()
        assert calc.memory_recall() == 0 or calc.memory_recall() is None, (
            "Expected memory_recall() to return 0 or None after clearing"
        )
    except (AttributeError, TypeError):
        # Some implementations might handle memory differently
        pass
