%%%% Template Adaptado para UCLM %%%%
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{ULBreport}
\LoadClass[a4paper,11pt]{report} % La clase 'report' permite usar Capítulos

%%%%Structure%%%%
\RequirePackage[utf8]{inputenc}
\RequirePackage[T1]{fontenc}
\RequirePackage{csquotes}
\RequirePackage[spanish,es-tabla]{babel} % <--- CAMBIADO A ESPAÑOL

% Comentado para permitir tu bibliografía manual (\begin{thebibliography})
% \RequirePackage[backend=biber,citestyle=alphabetic,bibstyle=authoryear]{biblatex}

\RequirePackage{tabularx}
\RequirePackage[top=2.5cm,bottom=2.5cm,left=2.5cm,right=2.5cm]{geometry} % Márgenes UCLM
\RequirePackage{hyperref}
\RequirePackage{enumitem}
\RequirePackage{xkeyval}
\RequirePackage{ifthen}

% Paquetes añadidos para tu diseño UCLM
\RequirePackage{eso-pic}     
\RequirePackage{transparent} 
\RequirePackage{float}       

%%%%package tikz%%%%
\RequirePackage{tikz}
\usetikzlibrary{mindmap}
\RequirePackage{chemfig}
\RequirePackage{pgfplots}
\pgfplotsset{compat=newest}

%%%%Forme%%%%
\RequirePackage[Bjornstrup]{fncychap} % <--- ESTO CREA LOS CUADROS GRISES AUTOMÁTICOS
\RequirePackage{graphicx}
\RequirePackage{textcomp}
\RequirePackage{eurosym}
\RequirePackage{mwe}
\RequirePackage{listings}
\RequirePackage{etoolbox}
\RequirePackage{setspace}
\RequirePackage{ccaption}
\RequirePackage{colortbl}
\RequirePackage{framed}
\RequirePackage{xcolor}
\RequirePackage{fourier}
\RequirePackage[pages=some]{background}

%%%%Math%%%%
\RequirePackage{mathtools}
\RequirePackage{amsmath}
\RequirePackage{amsfonts}
\RequirePackage{amssymb}
\RequirePackage{mathrsfs}
\usetikzlibrary{arrows,matrix,positioning}
\usetikzlibrary{3d,calc}
\RequirePackage[makeroom]{cancel}
\RequirePackage{esint}

%%%%Annexe%%%%
\RequirePackage[toc,page]{appendix}
\linespread{1.5}
\renewcommand{\appendixtocname}{Anexos}
\renewcommand{\appendixpagename}{Anexos}

%%%%Couleurs%%%%
\definecolor{apricot}{rgb}{0.98, 0.81, 0.69}
\definecolor{bleu}{rgb}{0.19, 0.55, 0.91}
\definecolor{rouge}{rgb}{0.77, 0.12, 0.23}
\definecolor{vert}{rgb}{0.13, 0.55, 0.13}
\definecolor{antiquefuchsia}{rgb}{0.57, 0.36, 0.51}
\colorlet{shadecolor}{cyan!30!white}
\colorlet{framecolor}{blue!50!black}

%%%%Custom command (PORTADA UCLM) %%%%
\makeatletter

% Llaves de configuración para la portada
\define@cmdkey [PRE] {fam} {title}{}
\define@cmdkey [PRE] {fam} {course}{}
\define@cmdkey [PRE] {fam} {author}{}
\define@cmdkey [PRE] {fam} {teacher}{}
\define@cmdkey [PRE] {fam} {date}{}
\define@cmdkey [PRE] {fam} {logoL}{}
\define@cmdkey [PRE] {fam} {logoR}{}
\define@cmdkey [PRE] {fam} {watermark}{}

\presetkeys [PRE] {fam} {
    title=Título, course=Curso, author=Autores, teacher=Profesor,
    date=\the\year, logoL=Logo_UCLM_40.jpg, logoR=esi.png, watermark=uclm_fondo.png
}{}

% Comando para la marca de agua UCLM
\newcommand\BackgroundPicUCLM{%
\put(0,0){%
\parbox[b][\paperheight]{\paperwidth}{%
\vfill
\centering
{\transparent{0.15}\includegraphics[width=0.85\textwidth, angle=15]{\cmdPRE@fam@watermark}}
\vfill
}}}

% Comando estructurado para imprimir tu portada UCLM
\newcommand*{\titleUCLM}[1]{\setkeys[PRE]{fam}{#1}
    \begingroup
    \begin{titlepage}
        \AddToShipoutPicture*{\BackgroundPicUCLM}

        \noindent
        \begin{minipage}{0.45\textwidth}
            \begin{flushleft}
                \includegraphics[height=1.5cm]{\cmdPRE@fam@logoL} 
            \end{flushleft}
        \end{minipage}
        \hfill
        \begin{minipage}{0.45\textwidth}
            \begin{flushright}
                \includegraphics[height=1.5cm]{\cmdPRE@fam@logoR}
            \end{flushright}
        \end{minipage}

        \vspace{3cm}

        \begin{center}
            \textbf{\cmdPRE@fam@course}
        \end{center}

        \vspace{1cm}

        \noindent\rule{\textwidth}{1pt}\\[-0.8\baselineskip]
        \noindent\rule{\textwidth}{0.4pt}
        
        \vspace{0.8cm}
        \begin{center}
            {\LARGE \textbf{\cmdPRE@fam@title}\par}
        \end{center}
        \vspace{0.4cm}
        
        \noindent\rule{\textwidth}{0.4pt}\\[-0.8\baselineskip]
        \noindent\rule{\textwidth}{1pt}

        \vspace{2.5cm}

        \begin{center}
            \cmdPRE@fam@author
        \end{center}

        \vspace{1.5cm}

        \begin{center}
            \textbf{Prof. \cmdPRE@fam@teacher}
        \end{center}

        \vfill

        \begin{center}
            \cmdPRE@fam@date
        \end{center}
    \end{titlepage}
    \ClearShipoutPicture
    \endgroup
}

% Fix on chapter overful hbox (Original del template)
\renewcommand{\DOCH}{%
    \settowidth{\py}{\CNoV\thechapter}%
    \addtolength{\py}{-10pt}%     
    \fboxsep=0pt%
    \colorbox[gray]{.85}{\rule{0pt}{40pt}\parbox[b]{\textwidth}{\hfill}}%
\kern-\myhi
    \kern-\py\raise20pt%
    \hbox{\color[gray]{.5}\CNoV\thechapter}%
\\%
  }
\makeatother