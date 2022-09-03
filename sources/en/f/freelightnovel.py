# -*- coding: utf-8 -*-
import logging
import re

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class FreeLightNovel(Crawler):
    base_url = 'https://www.freelightnovel.com/'

    def read_novel_info(self):
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one('h1.page-header')
        assert possible_title, 'No novel title'
        self.novel_title = possible_title.text
        logger.info('Novel title: %s', self.novel_title)

        possible_image = soup.select_one('.content img.img-responsive')
        if possible_image:
            self.novel_cover = self.absolute_url(possible_image['src'])
        logger.info('Novel cover: %s', self.novel_cover)

        self.volumes.append({'id': 1})
        for a in soup.select('.book-toc .dropdown-menu li.leaf a'):
            title = a.text.strip()

            chap_id = len(self.chapters) + 1
            match = re.findall(r'ch(apter)? (\d+)', title, re.IGNORECASE)
            if len(match) == 1:
                chap_id = int(match[0][1])
            # end if

            self.chapters.append({
                'volume': 1,
                'id': chap_id,
                'title': title,
                'url':  self.absolute_url(a['href']),
            })
        # end for
    # end def

    def download_chapter_body(self, chapter):
        logger.debug('Visiting %s', chapter['url'])
        soup = self.get_soup(chapter['url'])

        content = soup.select_one('.content')
        self.cleaner.clean_contents(content)

        return ''.join([
            str(p) for p in content.select('p')
            if len(p.text.strip()) > 1
        ])
    # end def
# end class