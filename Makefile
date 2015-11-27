.PHONY: clean all

all:
	latexmk -pdf -pdflatex="pdflatex -interactive=nonstopmode" thesis.tex

clean:
	latexmk -CA
