import os
import os.path
import subprocess
import sys
import textwrap


def pypirc_content(api_token):
    pypirc = f"""\
    [distutils]
    index-servers =
      pypi
    [pypi]
    repository: https://upload.pypi.org/legacy/
    username: __token__
    password: {api_token}
    """
    return textwrap.dedent(pypirc)


def create_pypirc(api_token):
    path = os.path.join(os.path.expanduser("~"), ".pypirc")
    with open(path, "w") as file:
        file.write(pypirc_content(api_token))


def upload(api_token):
    create_pypirc(api_token)
    subprocess.check_call([sys.executable, 'setup.py', 'sdist', 'bdist_wheel'])
    subprocess.check_call(['twine', 'upload', 'dist/*'])


if __name__ == "__main__":
    api_token = os.environ['PYPI_API_TOKEN']
    upload(api_token)
