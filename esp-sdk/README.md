# ESP SDK
These modules enables ESP developers to create and run ESP experiments.

[ESP SDK Documentation](docs/index.md)

# Running Python unit tests

1. Clone esp-sdk repository

- `git clone https://github.com/leaf-ai/esp-sdk.git`

2. Using Python 3.10.&ast or 3.11.&ast, create and then activate a virtual environment

- `python3 -m venv venv`
- `. ./venv/bin/activate`

3. Generate a classic personal access token on Github (https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-personal-access-token-classic)

- Select 'repo' and 'workflow' checkboxes
- After token is generated, select 'leaf-ai' in 'Configure SSO' dropdown
- Set the following environment variables to the generated personal access token\

  `export LEAF_SOURCE_CREDENTIALS=PersonalAccessToken`\
  `export LEAF_PRIVATE_SOURCE_CREDENTIALS=PersonalAccessToken`

4. Install packages specified in requirements.txt

- `pip install -r requirements.txt`

5. To run a specifc unit test

- `pytest -v PathToPythonTestFile::TestClassName::TestMethodName`
- `pytest -v esp_sdk/tests/test_esp_experiment_filer.py`

6. To run all unit tests

- `pytest -v esp_sdk/tests`

8. To debug a specific unit test

- Import pytest in the test source file
  - `import pytest`
- Set a trace to stop the debugger on the next line
  - `pytest.set_trace()`
- Run pytest with '--pdb' flag
  - `pytest -v --pdb esp_sdk/tests/test_esp_experiment_filer.py`

# Publishing esp-sdk

1. Have your pull request (PR) reviewed/approved/merged.

2. Go to `https://github.com/leaf-ai/esp-sdk/releases` and click on `Draft a new release` on top right of the page.

3. Click on `Choose a tag` and enter a new tag number. Make sure it’s the next logical release number -- for new features, update the minor number; for bug fixes update the patch number.

4. Set the 'Release title' to `ESP SDK Major.Minor.Patch`. E.g., `ESP SDK 4.0.8`

5. In the `Describe this release` box, list all the PRs and the full changelog -- refer to a previous release for the formatting.

6. Create a PR in unileaf repo that updates all of the requirements.txt files everywhere (do a find and/or grep) that already use esp_sdk with the new release number.
