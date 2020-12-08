from __future__ import print_function

import importlib
import tqdm

import generator
from lxml import etree
import pdb

def sanitize_text(data):
    print('type(data): {}'.format(type(data)))
    replace_with = {
        u'\u2018': '\'',
        u'\u2019': '\'',
        u'\u201c': '"',
        u'\u201d': '"'
    }

    bad_chars = [c for c in data if ord(c) >= 127]
    if bad_chars:
        print('INVALID CHARACTERS: {}'.format(bad_chars))
    else:
        print('INVALID CHARACTERS: {}'.format(bad_chars))

    for uni_char in replace_with.keys():
        data = data.replace(uni_char, replace_with.get(uni_char))

    data = ''.join([c for c in data if ord(c) < 127])
    return data.encode('utf-8', 'xmlcharreplace')

def sanitize_text_v2(data):
    my_parser = etree.XMLParser(recover=True)
    xml = etree.fromstring(bytes(data, encoding='utf-8'), parser=my_parser)
    data = etree.tostring(xml)
    return data

def main(args):
    # first, we construct a paper parser
    try:
        _parser = importlib.import_module("paper_parser.%s" % args.conference).PaperListParser(args)
    except Exception as e:
        print(e), exit()
    # second, we parse and generate a paper list containing paper information
    paper_list = _parser.parse_paper_list(args)

    # Third, parser detail paper information one by one (Considering multiprocessing; do not want to)
    cooked_paper_list = []
    for paper in tqdm.tqdm(paper_list):
        cooked_paper_list.append(_parser.cook_paper(paper))
    # cooked_paper_list.append(_parser.cook_paper(paper_list[0]))

    # Finally, generate output to a file
    _generator = getattr(generator, 'generate_%s_page' % (args.outputformat))
    content_page = _generator(cooked_paper_list, args)
    # content_page = sanitize_text(content_page)
    # with open('%s_source/' % (args.outputformat) + args.conference + str(args.year) + '.xml', 'w', encoding='utf8') as f:
    #     f.write(content_page.decode(encoding='UTF-8'))
    content_page = sanitize_text_v2(content_page)
    with open('%s_source/' % (args.outputformat) + args.conference + str(args.year) + '.xml', 'w', encoding='utf8') as f:
        f.write(content_page.decode(encoding='UTF-8'))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser("RSS Helper")
    parser.add_argument("--conference", '-c', help='Conference name(NIPS for NeurIPS)', type=str)
    parser.add_argument('--year', '-y', help='Specific year', type=int)
    parser.add_argument('--outputformat', '-o', help='Output format', type=str, default='rss')
    args = parser.parse_args()

    main(args)
