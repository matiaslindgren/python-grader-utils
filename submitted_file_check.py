"""
Minimal file validation from the command line.
TODO: This could be merged into importvalidator.
"""
import importlib.util
import importlib
import htmlgenerator
import sys
import argparse
import imghdr

# Non-interactive rendering to png
MATPLOTLIB_RENDERER_BACKEND = "AGG"


def get_image_type_errors(image, expected_type):
    errors = {}
    actual_type = imghdr.what(image)

    if actual_type != expected_type:
        errors["image_type_error"] = True
        errors["expected_type"] = expected_type
        errors["actual_type"] = actual_type

    return errors


def get_import_errors(module):
    errors = {}
    try:
        importlib.import_module(module)
    except ImportError as import_error:
        errors["import_error"] = str(import_error)
    except SyntaxError as syntax_error:
        errors["syntax_error"] = syntax_error.text
        errors["lineno"] = syntax_error.lineno
    except TypeError as type_error:
        errors["type_error"] = str(type_error)
    except ValueError as value_error:
        errors["value_error"] = str(value_error)
    except Exception as error:
        errors["misc_error"] = str(error)

    return errors

def get_labview_errors(filename):
    errors = {}
    with open(filename, "rb") as f:
        header = f.read(16)
        if header != b'RSRC\r\n\x00\x03LVINLBVW':
            errors["file_type_error"] = "The file wasn't a proper labVIEW-file"
    return errors


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--python")
    parser.add_argument("--image")
    parser.add_argument("--labview")
    args = parser.parse_args()

    errors = None

    if args.python:
        import matplotlib
        matplotlib.use(MATPLOTLIB_RENDERER_BACKEND)
        module_name = args.python.split(".py")[0]
        errors = get_import_errors(module_name)
    elif args.image:
        image_file = args.image
        image_type = image_file.split(".")[-1]
        errors = get_image_type_errors(image_file, image_type)
    elif args.labview:
        filename = args.labview
        errors = get_labview_errors(filename)

    if errors:
        print(htmlgenerator.errors_as_html(errors), file=sys.stderr)
        sys.exit(1)
