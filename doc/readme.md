We use a combination of Sphinx (*.rst)  and MyST markdown (.md) to create our documentation.
Only the main entry point `source/index.rst` is written in *.rst. 
For the individual content files we use MySt markdown: 

https://mystmd.org/guide
https://jupyterbook.org/en/stable/reference/cheatsheet.html
 

The usage of extended markdown flavor MyST instead of *.rst allows us to easier transfer 
content between readme files, issue tickets, wiki pages and this documentation. 

**a)** The documentation is **automatically built** online by GitHub workflow actions:

[https://github.com/fraunhofer-isi/micat/blob/main/.github/workflows/doc.yml](https://github.com/fraunhofer-isi/micat/blob/main/.github/workflows/doc.yml)

and published at

[https://fraunhofer-isi.github.io/micat](https://fraunhofer-isi.github.io/micat)

[https://fraunhofer-isi.github.io/micat/latex/micat.pdf](https://fraunhofer-isi.github.io/micat/latex/micat.pdf)

**b)** In order to **edit** the documentation you can use an IDE that supports markdown preview.

Also see

https://pypi.org/project/jupyterlab-myst/

https://github.com/executablebooks/myst-vs-code

https://marketplace.visualstudio.com/items?itemName=ExecutableBookProject.myst-highlight

https://plugins.jetbrains.com/search?search=markdown%20editor

https://mystmd.org/guide

https://jupyterbook.org/en/stable/reference/cheatsheet.html

Unfortunately, even when using the MyST extension vor VsCodium, the markdown **preview does not support all MyST** directives, yet.


**c)** In order to build the documentation **locally**, use following commands from within the `doc` folder:

./make.bat html
./make.bat pdf        (experimental preview, based on rst2pdf, does not require extra software; different look & feel)
./make.bat latexpdf   (production build, based on latex, requires extra installation of MikTex and Perl, see below)

**d)** The configuration is defined by:

* `source/conf.py` Sphinx configuration file
* `make.bat` (`Makefile` for Linux) Sphinx make file
* `.github/workflow/doc.yml` GitHub workflow actions

**e)** In order to build the `pdf` output locally using the command  `./make.bat latexpdf`:

* Download **MkTex** from https://miktex.org/download/ctan/systems/win32/miktex/setup/windows-x64/basic-miktex-23.4-x64.exe
* Rename file to miktex-portable.exe
* Install/unzip it to `C:\miktex`


* Download **Perl** from https://strawberryperl.com/download/5.32.1.1/strawberry-perl-5.32.1.1-64bit-portable.zip
* Unzip it to `C:\perl`


* Include following paths to your Windows **PATH** variable (or include them for example in your PyCharm configuration)

  * LATEX=`C:\miktex\miktex\bin\x64`
  * PERL=`C:\perl\perl\bin`
