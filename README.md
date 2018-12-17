
Zachaire is a static website generator that aims at being as simple as it can get. In that respect it pursues similar goals as [jekyll](https://github.com/jekyll/jekyll) or [hyde](https://github.com/hyde/hyde). It differenciate itself from Jekyll and Hyde in that it puts a lot of emphasis on files, more than on tools. It is still under development but can already prove itself useful (well, at least I am using it…).

To start building your own website:
 1. Clone the repository (should be replaced by a call to `zachaire init` in the future…)
 2. Edit `build.cfg` to indicate what is your base url (you can start by putting the result of `pwd out/`)
 3. Start writing your content in the `content/` folder, for instance `echo "# Hello world" > content/index.md`
 4. Tell Zachaire which builder and theme to use on `content/` by creating the corresponding `content/dirBuilding.cfg` file that specifies both informations: `echo "builderToUse = htmlPhpAndMarkdown" > "content/dirBuilding.cfg" && echo "themeToUse = myTheme" >> "content/dirBuilding.cfg"`
 5. Choose a theme in `theme/` and place a `menu.csv` file in its directory: `theme/myTheme/menu.csv`
 6. Build your website by calling `zachaire build` from the project root folder. This generates the content in `out/` directory
 7. Visit your website! E.g. `firefox out/index.html`

