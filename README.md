# The Visible Zorker: an interactive fiction visualizer

- Designed by Andrew Plotkin <erkyrath@eblong.com>
- Web site: https://eblong.com/infocom/visi-zork1/

This is the framework for a web app that plays Zork, or another ZIL game, and displays the game state as you play. Call it an exercise in exploratory coding.

To try the Visible Zorker, [play it here][visizork]. For more about the intent and origins of the project, see my [blog post on the subject][post].

[post]: https://blog.zarfhome.com/2025/01/the-visible-zorker
[visizork]: https://eblong.com/infocom/visi-zork1/

Since the Visible Zorker can (or will soon) play more than one Zork, I have divided it into two parts. This repository contains the common framework: the instrumented Z-code interpreter and display layer. A second repository contains the [information about Zork itself][vzork1].

[vzork1]: https://github.com/erkyrath/visizork

Thus, the code in this repository is incomplete. It won't work on its own. It's only meaningful as part of the [visizork][vzork1] repo.

## The contents of this repository

### The [`pyana`](./pyana) directory

Python scripts which parse the [`gamedat`][z1gamedat] and [`gamesrc`][z1gamesrc] files and convert them into JSON data in `js` for the Visible Zorker to load.

Roughly, we need to parse all the ZIL source *and* the disassembled data, match up numeric addresses with source code names, and write it out in a format that the Javascript app can handle. We use a motley boatload of strategies to accomplish this. The [`game-info`][z1gameinfo] gives us a lot of the needed mappings. Others are based on source code order, memory address order, or whatever else works.

[z1gamedat]: https://github.com/erkyrath/visizork/blob/master/gamedat
[z1gamesrc]: https://github.com/erkyrath/visizork/blob/master/gamesrc
[z1gameinfo]: https://github.com/erkyrath/visizork/blob/master/gamedat/game-info

### The [`src`](./src) directory

Javascript and Typescript sources for the Visible Zorker app itself.

- `src/visi`: The front-end UI of the app. This is React code written in Typescript.
- `src/gnusto`: The Gnusto Z-machine engine. This is a part of the [Parchment][] IF web app. I modified Gnusto to track game activity and export it to the `visi` UI.
- `src/parchment`: Another component of Parchment, responsible for loading the game file and launching the app.
- `src/ifvms.js`: Another component of Parchment which acts as a glue layer between Gnusto and the browser display. Also a component which is responsible for the save-file format.
- `src/glkio`: The [GlkOte][] IF display library. Also a glue layer which allows Gnusto/IFVMS to use GlkOte.
- `src/lib`: Low-level JS libraries used by Gnusto and GlkOte. This includes [jQuery][].

[GlkOte]: https://eblong.com/zarf/glk/glkote.html
[jQuery]: https://jquery.com/

Yeah, there's a lot of glue layers in there. It's the usual software-engineering story. Gnusto was originally written in 2003 as a browser extension. Then it was modified into a browser *application*, which was turned into a [web site][iplayif], which was expanded to support other formats besides Z-code. Each of these steps added more layers of abstraction.

[iplayif]: https://iplayif.com/

I unwound a lot of that work in creating the Visible Zorker. I wanted a *simple* interpreter engine, and I didn't need the web site or any of the newer formats. But there's still traces of some of the layers.

### The [`js`](./js) directory

Javascript used in running the app. This is all generated, compiled, or minified from the contents of the [`src`](./src), [`gamesrc`](./gamesrc), and [`gamedat`](./gamedat) directories.

### The [`css`](./css) directory

CSS files. Also some icon images in SVG, PNG, and animated-GIF format.

### The [`font`](./font) directory

Open-source fonts used in the app.

- [Courier Prime](https://fonts.google.com/specimen/Courier+Prime)
- [Lato](https://fonts.google.com/specimen/Lato)
- [Libre Baskerville](https://fonts.google.com/specimen/Libre+Baskerville)

## Sources and acknowledgements

The Visible Zorker is built on a seriously customized version of the [Parchment][] Z-machine interpreter by Marnanel Thurman, Atul Varma, and Dannii Willis.

[Parchment]: https://github.com/curiousdannii/parchment

The fonts used are Courier Prime, Lato, and Libre Baskerville. The header background is copied from Infocom's [Zork hint maps][zorkmap].

[zorkmap]: https://infodoc.plover.net/maps/zork1.pdf

Zork itself was originally written by Tim Anderson, Marc Blank, Bruce Daniels, and Dave Lebling. The commercial versions are copyright 1981 (etc) by Infocom, then Activision, then renamed to Mediagenic, then Bobby Kotick bought it and renamed it Activision, then Vivendi bought it and merged it with Blizzard, then Microsoft consumed the lot.

The Visible Zorker is copyright 2025 by Andrew Plotkin. My work on this project is under the MIT license.


