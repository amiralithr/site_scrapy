import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

class CrawlingSpider(CrawlSpider):
    # Spider name for command line usage
    name = 'mycrawler'

    # Only URLs under this domain will be crawled
    allowed_domains = ['divar.ir']

    # Starting URL(s) for crawling
    start_urls = ['https://divar.ir/s/iran/']

    # Rules define which links to follow and which pages to parse
    rules = (
        # Process individual ad pages
        Rule(LinkExtractor(allow=r'/v/'), callback='parse_item', follow=False),
    )

    def start_requests(self):
        yield scrapy.Request(
            url='https://divar.ir/s/iran/',
            meta={
                "playwright": True
            }
        )
    def parse_item(self, response):
        """
        Parse individual ad page.
        Extract:
        - URL
        - Breadcrumbs
        - ad_name, address
        - status (3 dictionaries)
        - description (key/value)
        - image URLs
        """

        # فقط در صورتی که div#post-list-container-id وجود دارد ادامه بده
        post_div = response.css("div#post-list-container-id")
        if not post_div:
            return

        # --------- 1. URL صفحه ----------
        div_url = response.url

        # --------- 2. Breadcrumbs (لیست category) ----------
        category = []
        breadcrumb_li = response.css('nav[aria-label="breadcrumbs"] ol.kt-breadcrumbs.kt-breadcrumbs--padded.kt-breadcrumbs--extended-items-on-mobile li.kt-breadcrumbs__item span.kt-breadcrumbs__action-text::text').getall()
        if breadcrumb_li:
            category = [text.strip() for text in breadcrumb_li if text.strip()]

        # --------- 3. ad_name و address ----------
        ad_name = response.css('div.kt-page-title__texts h1.kt-page-title__title.kt-page-title__title--responsive-sized::text').get()
        if ad_name:
            ad_name = ad_name.strip()

        address = response.css('div.kt-page-title__texts div.kt-page-title__subtitle.kt-page-title__subtitle--responsive-sized::text').get()
        if address:
            address = address.strip()

        # --------- 4. status (لیست دیکشنری ها) ----------
        status = []
        status_divs = response.css('div.kt-base-row.kt-base-row--large.kt-unexpandable-row')
        for div in status_divs:
            key = div.css('p.kt-base-row__title.kt-unexpandable-row__title::text').get()
            value = div.css('p.kt-unexpandable-row__value::text').get()
            if key and value:
                status.append({key.strip(): value.strip()})

        # --------- 5. description ----------
        description = {}
        description_section = response.css('section.post-page__section--padded > div.post-page__section--padded')
        for sec in description_section:
            key = sec.css('h2.kt-title-row__title.kt-title-row__title--secondary::text').get()
            value = sec.css('p.kt-description-row__text.kt-description-row__text--primary::text').get()
            if key and value:
                description[key.strip()] = value.strip()

        # --------- 6. images ----------
        image = []
        image_section = response.css('section.post-page__section--padded')
        for sec in image_section:
            imgs = sec.css('img.kt-image-block__image.kt-image-block__image--fading::attr(src)').getall()
            if imgs:
                image.extend(imgs)

        # --------- Yield final result ----------
        yield {
            "div_url": div_url,
            "category": category,
            "ad_name": ad_name,
            "address": address,
            "status": status,
            "description": description,
            "image": image
        }
