$definitions.typst()$

#let callout(kind, body) = {
  let colors = (
    note: (rgb("3568b8"), rgb("eef4fc")),
    tip: (rgb("287a52"), rgb("edf8f1")),
    warning: (rgb("b5542d"), rgb("fff3ec")),
  )
  let style = colors.at(kind, default: colors.note)
  block(
    width: 100%,
    fill: style.at(1),
    stroke: (left: 2.5pt + style.at(0)),
    inset: (x: 10pt, y: 8pt),
    above: 1em,
    below: 1em,
  )[
    #text(weight: "bold", fill: style.at(0))[#upper(kind)]
    #body
  ]
}

#show terms: it => {
  it.children
    .map(child => [
      #strong[#child.term]
      #block(inset: (left: 1.5em, top: -0.4em))[#child.description]
      ])
    .join()
}

#let conf(
  title: none,
  authors: none,
  date: none,
  abstract: none,
  cols: 1,
  margin: (x: 22mm, y: 22mm),
  paper: "a4",
  lang: "en",
  region: "US",
  font: (),
  fontsize: 11pt,
  sectionnumbering: "1.",
  doc,
) = {
  set document(title: title) if title != none
  set page(
    paper: paper,
    margin: margin,
    numbering: "1",
  )
  set par(justify: true)
  set text(
    lang: lang,
    region: region,
    font: font,
    size: fontsize,
  )
  set heading(numbering: sectionnumbering)
  show figure.where(kind: table): set block(breakable: true)

  if title != none {
    align(center)[#block(inset: 2em)[
      #text(weight: "bold", size: 1.5em)[#title]
    ]]
  }

  if authors != none {
    let count = authors.len()
    let ncols = calc.min(count, 3)
    grid(
      columns: (1fr,) * ncols,
      row-gutter: 1.5em,
      ..authors.map(author => align(center)[
        #author.name \
        #author.affiliation \
        #author.email
      ]),
    )
  }

  if date != none {
    align(center)[#block(inset: 1em)[#date]]
  }

  if abstract != none {
    block(inset: 2em)[
      #text(weight: "semibold")[Abstract] #h(1em) #abstract
    ]
  }

  if cols == 1 {
    doc
  } else {
    columns(cols, doc)
  }
}

#show: doc => conf(
$if(title)$
  title: [$title$],
$endif$
$if(author)$
  authors: (
$for(author)$
$if(author.name)$
    ( name: [$author.name$],
      affiliation: [$author.affiliation$],
      email: [$author.email$] ),
$else$
    ( name: [$author$],
      affiliation: [],
      email: [] ),
$endif$
$endfor$
    ),
$endif$
$if(date)$
  date: [$date$],
$endif$
$if(lang)$
  lang: "$lang$",
$endif$
$if(region)$
  region: "$region$",
$endif$
$if(abstract)$
  abstract: [$abstract$],
$endif$
$if(margin)$
  margin: ($for(margin/pairs)$$margin.key$: $margin.value$,$endfor$),
$endif$
$if(papersize)$
  paper: "$papersize$",
$endif$
$if(mainfont)$
  font: ("$mainfont$",),
$endif$
$if(fontsize)$
  fontsize: $fontsize$,
$endif$
$if(section-numbering)$
  sectionnumbering: "$section-numbering$",
$endif$
  cols: $if(columns)$$columns$$else$1$endif$,
  doc,
)

$for(header-includes)$
$header-includes$

$endfor$
$for(include-before)$
$include-before$

$endfor$
$if(toc)$
#outline(title: auto, depth: none)

$endif$
$body$

$if(citations)$
$if(bibliographystyle)$
#set bibliography(style: "$bibliographystyle$")
$endif$
$for(bibliography)$
#bibliography("$bibliography$")
$endfor$
$endif$
$for(include-after)$
$include-after$

$endfor$
