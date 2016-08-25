try:
    from markdown import markdown
except ImportError:
    from markdown2 import markdown

from BeautifulSoup import BeautifulSoup
import sys
import re
import logging

markdown_file = sys.argv[1]
http_methods = ("DELETE", "POST", "GET", "PUT", "OPTIONS", "PATCH")
logging.basicConfig(level=logging.INFO)
foundLinks = []
markdownLines = []


def findPathLine():
    # look for the first line containing '## Paths' and return the line number
    for c, l in enumerate(markdownLines):
        if re.search("^[#]{2} Paths$", l):
            logging.info("Found '%s' at line %d" % (l.strip(), c))
            return c
    logging.critical("Exit: ## Paths or ### Paths not found in markdown file")
    sys.exit(1)


def newPathMarkdown():
    newPathBlock = []

    # Converting file to HTML in memory
    md_str = open(markdown_file, "r").read()
    html = markdown(md_str)
    soup = BeautifulSoup(html)

    for e in soup.findAll("code"):
        if len(e) == 1 and e.text.startswith(http_methods):
            link = e.findPrevious('a').get("name")
            pathLine = "- [%s](#%s)\n" % (e.text, link)
            logging.info("Adding %s to path block" % (str(pathLine).strip()))
            foundLinks.append(link)
            newPathBlock.append(pathLine)
    newPathBlock.append("\n\n___")
    return newPathBlock


def insertVerticalSeperator():
    pattern = re.compile("^<a name=\"(.*)\"></a>")

    count = 0

    for c, l in enumerate(markdownLines[:]):
        if pattern.match(l) and pattern.match(l).groups()[0] in foundLinks[1:]:
            anchor = str(pattern.match(l).groups()[0])
            logging.info("Adding vertical line sperator at line: %d, right on top of anchor: %s" % (c + count - 2, anchor))
            markdownLines.insert(c + count - 2, "___")
            count += 1


def insertNewPathMarkdown():
    pathLocation = findPathLine()
    newMarkdown = newPathMarkdown()

    for c, l in enumerate(newMarkdown):
        markdownLines.insert(pathLocation + c + 1, l)


def replaceEmptyTableCells():
    global markdownLines
    t = []
    for c, l in enumerate(markdownLines):
        if "||" in l:
            logging.info("Replacing empty cell in following line: %s" % (l.strip()))
            l = l.replace("||", "| |")
            l = l.replace("||", "| |")
            t.append(l)
        else:
            t.append(l)
    markdownLines = t[:]


def insertPrefix():
    pattern = re.compile("^#\s(.)+$")
    for c, l in enumerate(markdownLines):
        if pattern.match(l) and pattern.match(l).groups()[0] is not None:
            logging.info("Using '%s' as the document title" % (l.strip()))
            markdownLines.pop(c)
            titleInPrefix = l
            break

    titleInPrefix = titleInPrefix.replace("#", "").strip()

    markdownLines.insert(0, """---
title: %s
taxonomy:
    category: docs
api: true
---""" % (titleInPrefix))

with open(markdown_file, "r") as f:
    markdownLines = f.readlines()

insertPrefix()
insertNewPathMarkdown()
insertVerticalSeperator()
replaceEmptyTableCells()

for l in markdownLines:
    print str(l),
