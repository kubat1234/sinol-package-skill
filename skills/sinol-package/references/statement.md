# Statement

**Default: don't write the story.** Ask the user. Fill only what must match
the package (subtask table, `\RAM`, examples) unless asked for more.

## Skeleton (`doc/<id>zad.tex`, Polish)

```latex
\documentclass[zad,zawodnik,utf8,pl]{sinol}
\title{Tytuł}
\id{abc}
\signature{10grodek27}
\konkurs{10Gródek27}
\day{1}
\date{12.01.2027}
\RAM{512}               % MB = memory_limit / 1024
\iomode{stdin}          % interactive tasks: \iomode{interactive}
\pagestyle{fancy}
\setlength{\parindent}{0pt}  % no paragraph indent
\setlength{\parskip}{0.6em}  % visible gap between paragraphs instead

\begin{document}
\begin{tasktext}
\vspace{-0.5cm}  % smaller gap above the first paragraph
\noindent {}%
Historia i polecenie.

\section{\sinolSNameInput}   % "Wejście"
W pierwszym wierszu wejścia znajduje się jedna liczba całkowita $n$
($1 \le n \le 200\,000$) ...

\section{\sinolSNameOutput}  % "Wyjście"
Wypisz ...

\section{Przykład}
\makecompactexample{0}       % in/abc0.in + out/abc0.out, from g.example(...)
% several examples: \makecompactexample{0a}, \makecompactexample{0b}, ... instead of {0}

\section{Podzadania}
\begin{center}
\begin{tabular}{|l|l|l|l|}
\hline
\textbf{\sinolSNameSubtask} & \textbf{\sinolSNamePoints} &
\textbf{\sinolSNameConditions} & \textbf{\sinolSNameTimeLimit} \\ \hline
1 & $30$ & $n \le 1000$ & $1$ s \\ \hline
2 & $70$ & brak dodatkowych założeń & $1$ s \\ \hline
\end{tabular}
\end{center}
\end{tasktext}
\end{document}
```

`\makecompactexample` reads the generated files, so run `sinol-make gen`
before `sinol-make doc`. `contest.py lint` parses the table rows `group & $points$ & … & $time$ s \\`
and compares them with `scores` / `time_limit(s)` — keep that row format.
Optional sections: `\section{Wyjaśnienie przykładu}`, `\section{Komunikacja}`
(library / interactive — exact function signatures or message formats, query
limits, flushing).

## Style (Polish olympiad conventions)

- Numbers in math mode, thousands separated with `\,` (`$200\,000$`), `$10^9$`.
- "W pierwszym wierszu wejścia znajduje się…", "Wypisz jedną liczbę całkowitą…".
- Every variable defined with its range in the input section.
- Say explicitly what to print when there are several answers / no answer.
- The story should not hide the actual task; final sentence states it precisely.
- Layout: keep the `\parindent` / `\parskip` lines and the `\vspace{-0.5cm}\noindent {}` at the start
  of `tasktext` from the skeleton. Paragraphs are separated by an empty line only;
  don't add `\noindent` before or `\\` after blocks.

## Translations

Extra file `doc/<id>zad-en.tex` with `\documentclass[zad,zawodnik,utf8,en]{sinol}`
(sinol.cls switches section names), `title_en:` in config.yml. Keep both files
in sync when anything changes. `sinol-make doc` builds all `.tex` files in `doc/`.
