# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from Zhiyouji.items import ZhiyoujiItem
import time
from scrapy_redis.spiders import RedisCrawlSpider


class ZhiyoujiSpider(RedisCrawlSpider):
    name = 'zhiyouji'
    # allowed_domains = ['jobui.com']
    # start_urls = ['http://www.jobui.com/cmp/']

    def __init__(self, *args, **kwargs):
        domain = kwargs.pop('domain', '')
        self.allowed_domains = list(filter(None, domain.split(',')))
        super(ZhiyoujiSpider, self).__init__(*args, **kwargs)

    redis_key = 'Zhiyouji'

    rules = (
        # 列表页规则
        # Rule(LinkExtractor(allow=r'Items/'), callback='parse_item', follow=True),
        Rule(LinkExtractor(allow=r'/cmp\?n=\d+#listInter'), follow=True),

        # 详情页页规则
        Rule(LinkExtractor(allow=r'/company/\d=/$'), callback='parse_item'),

    )

    def parse_item(self, response):

        # 创建item实例
        item = ZhiyoujiItem()

        # 提取数据，存放到item实例中
        item['timestamp'] = time.time()
        item['url'] = response.url

        item['company'] = response.xpath('//*[@id="companyH1"]/a/text()').extract_first()
        item['views'] = response.xpath('//div[@class="grade cfix sbox"]/div[1]/text()').extract_first().split('人')[0].strip()
        item['category'] = response.xpath('//*[@id="cmp-intro"]/div/div[2]/dl/dd[1]/text()|//*[@id="cmp-intro"]/div/div/dl/dd[1]/text()').extract_first().split('/')[0]
        item['number'] = response.xpath('//*[@id="cmp-intro"]/div/div[2]/dl/dd[1]/text()|//*[@id="cmp-intro"]/div/div/dl/dd[1]/text()').extract_first().split('/')[-1]
        item['trade'] = ' '.join(response.xpath('//*[@id="cmp-intro"]/div/div[2]/dl/dd[2]/a/text()').extract())
        item['short_name'] = response.xpath('//*[@id="cmp-intro"]/div/div[2]/dl/dd[3]/text()').extract_first()
        item['desc'] = ''.join(response.xpath('//*[@id="textShowMore"]/text()').extract())
        item['praise'] = response.xpath('//div[@class="swf-contA"]/div/h3/text()').extract_first()
        item['salary'] = response.xpath('//div[@class="swf-contB"]/div/h3/text()').extract_first()

        # 获取产品信息
        data_list = []
        node_list  = response.xpath('//div[@class="jk-matter jk-box"]/div/div')
        for node in node_list:
            temp = {}
            temp['name'] = node.xpath('./div/a/text()').extract_first()
            temp['desc'] = node.xpath('./p/text()').extract_first()
            data_list.append(temp)
        item['products'] = data_list

        # # 获取融资信息
        data_list = []
        node_list = response.xpath('//div[@class="jk-matter jk-box fs16"]/ul/li')
        # # print(len(node_list))
        for node in node_list:
            temp = {}
            temp['date'] = node.xpath('./span[1]/text()').extract_first()
            temp['status'] = node.xpath('./h3/text()').extract_first()
            temp['sum'] = node.xpath('./span[2]/text()').extract_first()
            temp['investors'] = node.xpath('./span[3]/text()').extract_first()
            data_list.append(temp)
        item['finance_info'] = data_list

        # 获取融资信息
        data_list = []
        node_list = response.xpath('//div[@class="fs18 honor-box"]/div')
        # print(len(node_list))
        for node in node_list:
            temp = {}
            key = node.xpath('./a/text()').extract_first()
            temp[key] = node.xpath('./span[2]/text()').extract_first()
            data_list.append(temp)
        item['rank'] = data_list
        #

        item['address'] = response.xpath('//dl[@class="dlli fs16"]/dd[1]/text()').extract_first()
        item['website'] = response.xpath('//dl[@class="dlli fs16"]/dd[2]/a/text()').extract_first()
        item['contact'] = response.xpath('//dl[@class="dlli fs16"]/div[1]/dd/text()').extract_first().replace('\xa0','')
        item['qq'] = response.xpath('//span[@class="contact-qq"]/text()').extract_first()

        # 返回数据
        yield item

