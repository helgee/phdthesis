using Mustache

template = mt"""\documentclass{scrartcl}
\usepackage[utf8]{inputenc}
\usepackage{xspace}
\usepackage{tikz}
\usepackage{../tikz-uml}
\input{../uml}
\input{../macros}
\begin{document}
{{#texfiles}}
{{.}}
{{/texfiles}}
\end{document}
"""
output = joinpath(@__DIR__(), "diagrams.tex")
rm(output)
files = readdir(@__DIR__)
texfiles = ["\\include{$(splitext(f)[1])}" for f in files if endswith(f, ".tex")]
open(output, "w") do f
    write(f, render(template, Main))
end
cd(@__DIR__) do
    run(`latexmk -pdf $output`)
end
