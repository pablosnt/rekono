Thank you for making Rekono greater.

## Issues

You can create different kinds of [Issues](https://github.com/pablosnt/rekono/issues/new/choose) to report bugs, request new features or ask for help.

Please, don't report security vulnerabilities in GitHub Issues. See our [Security Policy](https://github.com/pablosnt/rekono/security/policy).


## Contributing to Rekono

**You can create Pull Requests to the `develop` branch of this project**. All the Pull Requests should be reviewed and approved before been merged. After that, your code will be included on the next Rekono release.

In this section you can see how to achieve that and the things that you should to take into account.

### Development environment

You can check this Wiki sections to prepare your Rekono contributions:

- Documentation about the database and architecture [Design](https://github.com/pablosnt/rekono/wiki/3.-Design)
- [From Source](https://github.com/pablosnt/rekono/wiki/4.-Installation#from-source) installation guide
- [Configuration](https://github.com/pablosnt/rekono/wiki/5.-Configuration) guidelines

Note that you can also execute the unit tests using the following command:

```
# pwd: rekono/
coverage run manage.py test
```

### Add support for a new hacking tool

The support of external hacking tools in Rekono is based on the following steps:

1. Define the hacking tools in the [tools/fixture](https://github.com/pablosnt/rekono/tree/main/rekono/tools/fixtures) files. There are one file for each required entity:
    
    - [`1_tools.json`](https://github.com/pablosnt/rekono/blob/main/rekono/tools/fixtures/1_tools.json): basic definition of the tool including information like name, command or reference link.
    
    - [`2_intensities.json`](https://github.com/pablosnt/rekono/blob/main/rekono/tools/fixtures/2_intensities.json): intensity levels supported by the hacking tools and the related argument needed to configure the executions.
    
    - [`3_configurations.json`](https://github.com/pablosnt/rekono/blob/main/rekono/tools/fixtures/3_configurations.json): tool configurations available in Rekono based on an argument pattern and identified by a name.

    - [`4_arguments.json`](https://github.com/pablosnt/rekono/blob/main/rekono/tools/fixtures/4_arguments.json): tool arguments whose value should be obtained from an input (previous findings, wordlists or target information).

    - [`5_inputs.json`](https://github.com/pablosnt/rekono/blob/main/rekono/tools/fixtures/5_inputs.json): different input types that could be valid for a tool argument sorted by priority.

    - [`6_outputs.json`](https://github.com/pablosnt/rekono/blob/main/rekono/tools/fixtures/6_outputs.json): different input types that a tool configuration can detect in the target.

2. Implement the parser to obtain findings from the tool results. You have to do that in the [tools/tools](https://github.com/pablosnt/rekono/tree/main/rekono/tools/tools) package:

    - Create a new Python file with the tool name (defined in the previous step) in lower case and without whitespaces.
    
    - Create a new Python class with the tool name (defined in the previous step) capitalized and with the word `Tool` at the end. This class needs to extend the `tools.tools.base_tool.BaseTool` class.

    - Override the method `parse_output_file` or `parse_plain_output` depending on the tool output type.

3. Implement unit tests to check the parser correct working. You can use some [tool reports](https://github.com/pablosnt/rekono/tree/main/rekono/testing/data/reports) as example for that.

4. Add the tool reference in the [README.md](https://github.com/pablosnt/rekono#supported-tools).

### CI/CD

This project has the following checks in _Continuous Integration_:

1. `Code style`: check the source code style using the tools `mypy`, `flake8` and `eslint`.

2. `SCA`: check the project dependencies to find libraries with known vulnerabilities. Software Composition Analysis.

3. `Secrets scanning`: check the source code to find leaked passwords, tokens or other credentials that could be exposed in the GitHub repository.

4. `Unit testing`: check if the project works executing the unit tests.

**All CI/CD checks should be passed before merging any Pull Request**, so it's advised to install the pre-commit hooks in your local repositories using this commands:

```
# pwd: root directory
python3 -m pip install pre-commit
pre-commit install
```

### Way of Code

There are some guidelines to keep the code clean and ensure the correct working of the application:

- Comment your code, specially to document the classes and methods.
- Make unit tests for all your code to ensure its correct working. It's important to keep the testing coverage over a 95% coverage.
- Don't include code vulnerabilities or vulnerable libraries.
