from urllib.request import urlopen

from bs4 import BeautifulSoup
import tqdm

from paper_parser import BasePaperListParser, Paper
import pdb


class PaperListParser(BasePaperListParser):

    def __init__(self, args):
        self.base_url = f"https://proceedings.neurips.cc/paper/{args.year}"
        self.website_url = "https://proceedings.neurips.cc"


    def parse(self, html_soup):
        all_container = html_soup.select("div.col")[0].select('li')
        paper_list = []
        spotlight = 0
        oral = 0
        poster = 0
        overall = 0
        faild = 0
        for container in tqdm.tqdm(all_container):
            overall += 1
            try:
                # title = container.select('div.maincardBody')[0].get_text() + suffix
                # url = container.select('a.href_PDF')[0].get('href')
                # # assert "PDF" in container.select('a.href_PDF')[0].get_text()
                title = container.select('a')[0].get_text()
                url = container.select('a')[0].get('href')
                paper_list.append((title, url))
            except Exception as e:
                print(e)
                faild += 1
                pass
        print(f"Parse {self.base_url}, total: {len(all_container)}, fail: {faild}")
        return paper_list

    def cook_paper(self, paper_info):
        try:
            page_content = urlopen(self.website_url + paper_info[1]).read().decode('utf8')
            soup = BeautifulSoup(page_content, features="html.parser")
            soup = soup.select('div.col')[0]
            href_list = soup.select('div')[0].select('a')
            for item_href in href_list:
                if 'Paper' in item_href.get_text():
                    pdf_url = self.website_url + item_href.get('href')
                    break
            abstract = self.text_process(soup.select('p')[3].get_text())
            author_str = soup.select('p')[2]
            author_list = [author_str]
            if ',' in author_str:
                author_list = [self.text_process(item.trim()) for item in author_str.split(',')]
            return Paper(self.text_process(paper_info[0]), abstract, pdf_url, author_list)
        except Exception as e:
            print(e)
            return (paper_info[0], e, self.base_url, [])
