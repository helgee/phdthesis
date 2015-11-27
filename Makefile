.PHONY: clean

all: thesis.pdf

thesis.pdf: thesis.tex
	latexmk -pdf -pdflatex="pdflatex -interactive=nonstopmode" thesis.tex

clean:
	latexmk -CA
