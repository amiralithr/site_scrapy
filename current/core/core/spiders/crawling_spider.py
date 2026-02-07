from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

class CrawlingSpider(CrawlSpider):
    name = 'mycrawler'
    allowed_domains = ['divar.ir']
    start_urls = ['https://divar.ir/s/iran/']

    rules = (
        Rule(LinkExtractor(allow=r'/v/'), callback='parse_item', follow=False),
    )

    def parse_item(self, response):
        # بررسی وجود محتوا
        if not response.css("div#post-list-container-id"):
            return

        # URL صفحه
        div_url = response.url

        # Breadcrumbs
        category = [
            t.strip() for t in response.css(
                'nav[aria-label="breadcrumbs"] ol.kt-breadcrumbs li span.kt-breadcrumbs__action-text::text'
            ).getall() if t.strip()
        ]

        # ad_name و address
        ad_name = response.css('div.kt-page-title__texts h1.kt-page-title__title::text').get()
        ad_name = ad_name.strip() if ad_name else None

        address = response.css('div.kt-page-title__texts div.kt-page-title__subtitle::text').get()
        address = address.strip() if address else None

        # status
        status = []
        for div in response.css('div.kt-base-row.kt-base-row--large.kt-unexpandable-row'):
            key = div.css('p.kt-base-row__title::text').get()
            value = div.css('p.kt-unexpandable-row__value::text').get()
            if key and value:
                status.append({key.strip(): value.strip()})

        # description
        description = {}
        for sec in response.css('section.post-page__section--padded > div.post-page__section--padded'):
            key = sec.css('h2.kt-title-row__title--secondary::text').get()
            value = sec.css('p.kt-description-row__text--primary::text').get()
            if key and value:
                description[key.strip()] = value.strip()

        # images
        images = []
        for sec in response.css('section.post-page__section--padded'):
            imgs = sec.css('img.kt-image-block__image::attr(src)').getall()
            if imgs:
                images.extend(imgs)

        yield {
            "div_url": div_url,
            "category": category,
            "ad_name": ad_name,
            "address": address,
            "status": status,
            "description": description,
            "images": images
        }
