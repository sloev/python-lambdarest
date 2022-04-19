"""For use with pytest-readme pytest plugin"""

print("Running conftest.py", flush=True)

with open("test_readme.py", "w") as out, open("./docs/README.md") as readme:
    mode = None
    output = []
    for i, line in enumerate(readme.readlines()):
        output.append("\n")
        if mode is None and line.strip() == "```python":
            mode = "first_line"
            output[i] = "def test_line_%s():\n" % i
            continue
        elif line.strip() == "```":
            if mode == "doctest":
                output[i] = '    """\n'
            mode = None
            continue
        elif mode == "first_line":
            if line.strip() == "":
                mode = None
                output[i - 1] = "\n"
                continue
            if line.strip().startswith(">>>"):
                mode = "doctest"
                output[i - 2] = (
                    output[i - 1][:-1] + "  " + output[i - 2]
                )  # move the def line one line up
                output[i - 1] = '    """\n'
            else:
                mode = "test"
        if mode in ("doctest", "test"):
            output[i] = "    " + line
        else:
            output[i] = "# %s" % line

    out.writelines(output)
