#!/usr/local/miniconda2/bin/python
# _*_ coding: utf-8 _*_

"""
@author: MarkLiu
@time  : 17-7-16 下午2:11
"""

from __future__ import print_function

import argparse
import mistune
import os
import shutil
import socket

import bs4 as BeautifulSoup
import requests
from six.moves.urllib.error import HTTPError


def download_pdf(link, location, name):
    try:
        response = requests.get(link)
        with open(os.path.join(location, name), 'wb') as f:
            f.write(response.content)
            f.close()
    except HTTPError:
        print('>>> Error 404: cannot be downloaded!\n')
        raise
    except socket.timeout:
        print(" ".join(("can't download", link, "due to connection timeout!")))
        raise


def clean_text(text, replacements={':': '_', ' ': '_', '/': '_', '.': '', '"': ''}):
    for key, rep in replacements.items():
        text = text.replace(key, rep)
    return text


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Download all the PDF/HTML links into README.md')
    parser.add_argument('-d', action="store", dest="directory", default='downloaded_papers')
    parser.add_argument('--no-html', action="store_true", dest="nohtml", default=False)
    parser.add_argument('--overwrite', action="store_true", default=False)
    results = parser.parse_args()

    output_directory = results.directory

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    forbidden_extensions = ['html', 'htm'] if results.nohtml else []

    if results.overwrite and os.path.exists(output_directory):
        shutil.rmtree(output_directory)

    with open('README.md') as readme:
        readme_html = mistune.markdown(readme.read())
        readme_soup = BeautifulSoup.BeautifulSoup(readme_html, "html.parser")

    cate_points = readme_soup.find_all('h3')
    failures = []
    success = 0
    for cate_point in cate_points:
        cate = cate_point.text
        directory = os.path.join(output_directory, clean_text(cate))
        current_directory = directory
        if not os.path.exists(current_directory):
            os.makedirs(current_directory)
        print('download {} papers...'.format(cate))
        ul = cate_point.find_next('ul')
        if ul:
            lis = ul.find_all('li')
            for li in lis:
                a = li.find('a')
                if a:
                    paper_name = a.text
                    print("---> download <<{}>>".format(paper_name))
                    link = a['href']
                    try:
                        download_pdf(link, current_directory, paper_name + '.pdf')
                        success += 1
                    except Exception:
                        failures.append(paper_name)

    print('Done!')
    print('downloaded {} papers'.format(success))
    if len(failures) > 0:
        print('Some downloads have failed:')
        for fail in failures:
            print('> ' + fail)
