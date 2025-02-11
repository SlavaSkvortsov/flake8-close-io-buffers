# flake8-close-io-buffers

A Flake8 plugin to detect unclosed IO buffers in your Python code. This tool helps ensure that IO objects (such as `io.BytesIO` and `io.StringIO`) are properly closed either via a context manager or an explicit `.close()` call.

## Features

- **Detects Unclosed IO Objects:**  
  Reports an error (`IO100`) when an IO object is instantiated but not closed.

- **Supports Different Import Styles:**  
  Works with both:
  - Qualified imports:  
    ```python
    import io
    io.BytesIO()
    ```
  - Direct imports:  
    ```python
    from io import BytesIO, StringIO
    BytesIO()
    ```

- **Multiple Assignment Support:**  
  Correctly handles cases where IO objects are assigned to variables, including tuple/list assignments.

## Installation

You can install the plugin from PyPI:

```bash
pip install flake8-close-io-buffers
```

Or install it in editable mode from source:

```bash
git clone https://github.com/your-username/flake8-close-io-buffers.git
cd flake8-close-io-buffers
pip install -e .
```

## Usage

Once installed, Flake8 will automatically load the plugin. Run Flake8 on your Python files as usual:

```bash
flake8 your_python_file.py
```

### Configuration

By default, Flake8 may not display errors from custom plugins. To ensure that `IO100` errors are reported, add the following to your Flake8 configuration file (e.g., `.flake8`, `setup.cfg`, or `tox.ini`):

```ini
[flake8]
extend-select = IO100
```

Or, run Flake8 with the select flag:

```bash
flake8 --select=IO100 your_python_file.py
```

## Example

Consider the following code in `example.py`:

```python
import io

def foo():
    io.BytesIO()  # Unclosed IO object: will trigger IO100 error
```

Running Flake8:

```bash
flake8 --select=IO100 example.py
```

Will produce an error like:

```text
example.py:4:5: IO100 unclosed IO object instantiation not assigned to a variable
```

## Running Tests

The project uses pytest for testing. To run the tests:

1. Ensure you have the development dependencies installed (e.g., `pytest`).
2. From the project root, run:

```bash
pytest
```

## Contributing

Contributions are welcome! Please feel free to open issues or submit pull requests on [GitHub](https://github.com/your-username/flake8-close-io-buffers).

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
