HTML citations
==============

Use your BibTeX files in your website or your HTML presentation. This app also works with markdown files, so you can combine this maybe with Jekyll. In case of markdown the app generates some extra tags, that should be removed after processing. This step will be automated in a later version.

## Install

```
pip3 install -r requirements.txt
```

## Usage

If you have an `index.html` file with a cite like the following
```
...
<p>Lorem ipsum <cite>{A_BIBTEX_KEY}</cite></p>

<bibligraphy>MY_BIBTEX_FILE_PATH</bibligraphy>
...
```
and you perform the command
```
python3 app.py index.html index.html
```
you will get a updated file
```
...
<p>Lorem ipsum <cite>1</cite></p>

<bibligraphy><li><span class="ref">1</span>Entry details</li></bibligraphy>
...
```

## Styles

At the moment I have only implemented most of the IEEE referencing style. This could also be improved in the future, but I don't need it for my own work.

## Dependencies

 * `lxml` for html parsing
 * `pybtex` for BibTeX parsing 