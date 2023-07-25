We use a combination of Sphinx (*.rst)  and MyST markdown (.md) to create our documentation.
The main entry point is `source/index.rst`.

In order to build the documentation manually, use following commands:

```
.\make html
.\make pdf
```

The configuration is defined by:
* `source/conf.py`, 
* `make.bat` (Makefile for Linux) and 
* `.gitlab-ci.yml` in root folder.