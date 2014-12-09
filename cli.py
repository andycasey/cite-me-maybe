#/usr/bin.python

""" J-Sick's *awesome* citation buddy CLI idea """

import collections
import difflib
import logging
import operator
import sys

import ads

logging.basicConfig(format="%(asctime)s %(message)s",level=logging.INFO)


def recommend_references(bibcode, num=3, ratio=0.5):
    """
    Return bibcodes of recommended articles that might have been worth citing
    in the bibcode provided.

    :param bibcode:
        The bibcode of the article that you would like to have recommended
        citations for.

    :type bibcode:
        str

    :param num:
        Number of article bibcodes to recommend.

    :type num:
        int

    :param ratio:
        Self-similarity ratio in names in order to identify two author names as
        being the same person.

    :type ratio:
        float

    :returns:
        Article bibcodes that probably should have been cited.
    """


    # OK I have used crazy variable names for "humans" because this is otherwise
    # a conceptually annoying problem.

    num = int(num)
    if 1 > num:
        raise ValueError("number of requested articles must be a a positive integer")

    if not (1 >= ratio > 0):
        raise ValueError("self-similarity ratio must be between (0, 1]")

    # First get the article
    try:
        original_article = list(ads.query(bibcode))[0]

    except:
        raise ValueError("could not find original article with bibcode {0}".format(bibcode))

    logging.debug("Article has bibcode, title: {0} {1}".format(
        original_article.bibcode, original_article.title))

    # Find all the citations that the paper made
    articles_i_cited = list(original_article.references)

    logging.debug("This article cited {0} papers".format(len(articles_i_cited)))

    bibcodes_of_articles_i_cited = [each.bibcode for each in articles_i_cited]

    # Who else cited the papers that I cited?
    which_articles_cite_what_we_cite = []

    # Go to all of those papers
    for article in articles_i_cited:

        # Find all of the references from those papers
        # (let's call them "all_references")
        which_articles_cite_what_we_cite.extend(
            [each.bibcode for each in article.citations])

    most_popular_articles_cited = [article for article in which_articles_cite_what_we_cite \
        if article not in bibcodes_of_articles_i_cited]

    # Create a collection counter for these items
    most_popular_articles_cited = collections.Counter(most_popular_articles_cited)

    # Sort by most values
    most_popular_articles_cited = sorted(
        most_popular_articles_cited.items(), key=operator.itemgetter(1))[::-1]

    # Let's not include papers written by the current author
    recommended_bibcodes = []
    original_author = original_article.author[0].lower().replace(".", "")
    for bibcode, popularity in most_popular_articles_cited:

        article = list(ads.query(bibcode))[0]
        this_author = article.author[0].lower().replace(".", "")

        if difflib.SequenceMatcher(a=this_author, b=original_author).ratio() > ratio:
            # Same same
            continue

        else:
            recommended_bibcodes.append(bibcode)
            if len(recommended_bibcodes) == num:
                break

    for bibcode in recommended_bibcodes:
        article = list(ads.query(bibcode))[0]
        logging.debug("Recommend this paper: {0} by {1} at {2}".format(
            article.title, article.author[0], article.url))

    return recommended_bibcodes


if __name__ == "__main__":

    # citation-buddy bibtex_code
    # bibtex_code = 2014MNRAS.443..828C


    # one paper
    # One paper has a bunch of citations
    # We want to know who else we should cite

    # OK< so basically we want to know *which* papers also cite the papers we cite,
    # and then from those papers which papers they cite that we don't.


    # ^^^^^^^ cited papers

    # ^^^^^^^^^^ who else cited those papers

    # ^^^^^^^^^^^^^^^ papers that those papers cited that you haven't.

    # STEPS
    # (1) Find all the citations that the paper made
    # (2) Go to all of those papers, and find out who else cited those papers
    # (3) Go to all of those those papers, and find out which papers they cited that
    #     you didn't. Count the frequency and find the highest ones

    if len(sys.argv) > 1:
        recommend_references(sys.argv[1:])