# GAP Wrapper

A simple Python wrapper for GAP (Groups, Algorithms, Programming).

## Installation

You can install the package directly from GitHub.

### 1. Using pip (non-editable)

This installs the latest version:

```bash
pip install git+https://github.com/kamalsaleh/gapwrapper.git
```

### Using editable install

If you want to modify the code locally and have changes reflected immediately:

```bash
git clone https://github.com/kamalsaleh/gapwrapper.git
cd gapwrapper
pip install -e .
```

##### Notes

* This requires Python 3.10 or higher.
* Make sure the GAP executable is installed and available in your system PATH.

### Verify Installation

Start Python and try:

```bash
>> from gapwrapper import GAP
>> gap = GAP()

>> gap("1+1;")
"2"
>> gap >> "Factorial(5);"
"120"
>> gap.close()
```
