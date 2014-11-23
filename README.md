HTML citations
==============

Use your BibTeX files in your website or your HTML presentation.


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
python3 cite.py index.html
```
you will get a updated file
```
...
<p>Lorem ipsum <cite>1</cite></p>

<bibligraphy><li><span class="ref">1</span>Entry details</li></bibligraphy>
...
```