import re
import time
import datetime
from urllib.parse import urlencode

from requests import Session
from lxml import etree

from utils import init_log, DBClass, get_settings, get_database, request
from settings import headers, index_url, type_mappings

logger = init_log('my')
DATABASE, TABLE = get_database()
DOMAIN, CALCULATE_DATE, RUN_INTERVAL = get_settings()
headers['Host'] = re.search('//(.*?)(/|$)', DOMAIN).group(1)
headers['Origin'] = DOMAIN
DB = DBClass(DATABASE, 'sqlserver')


class EvaluationRank(object):

    def __init__(self):
        self.session = Session()

        self.view_state = None
        self.view_state_generator = None
        self.event_validation = None

    def get_parm(self, text):
        self.view_state = re.search('id="__VIEWSTATE" value="(.*?)"', text).group(1)
        self.view_state_generator = re.search('id="__VIEWSTATEGENERATOR" value="(.*?)"', text).group(1)
        self.event_validation = re.search('id="__EVENTVALIDATION" value="(.*?)"', text).group(1)

    def parser(self, text: str, query_date: str, score_type: str):
        html = etree.HTML(text)

        for tr in html.xpath('//table[@id="gridView"]//tr')[1:]:
            try:
                obj = {
                    'score_type': type_mappings.get(score_type),
                    'ranking': str(tr.xpath('./td[1]')[0].xpath("string(.)")),
                    'company': str(tr.xpath('./td[2]/span/@title')[0]),
                    'organization_code': str(tr.xpath('./td[3]')[0].xpath("string(.)")),
                    'credit_code': str(tr.xpath('./td[4]')[0].xpath("string(.)")),
                    'normal_score': str(tr.xpath('./td[5]')[0].xpath("string(.)")),
                    'promise_score': str(tr.xpath('./td[6]')[0].xpath("string(.)")),
                    'quality_score': str(tr.xpath('./td[7]')[0].xpath("string(.)")),
                    'total_score': str(tr.xpath('./td[8]')[0].xpath("string(.)")),
                    'calculate_date': query_date
                }
                pk = DB.select_condition(
                    TABLE,
                    'id',
                    [
                        ['score_type', '=', obj.get('score_type')],
                        ['organization_code', '=', obj.get('organization_code')],
                        ['calculate_date', '=', query_date]
                    ]
                )
                if pk:
                    DB.update_many(TABLE, [obj], [{'id': pk[0][0]}])
                else:
                    DB.insert_many(TABLE, [obj])
            except Exception as e:
                pass

    def get_total_page(self, now_date: str, query_date: str, score_type: str) -> int:
        data = {
            '__EVENTTARGET': 'linkBtnQuery',
            '__EVENTARGUMENT': '',
            '__LASTFOCUS': '',
            '__VIEWSTATE': self.view_state,
            '__VIEWSTATEGENERATOR': self.view_state_generator,
            '__VIEWSTATEENCRYPTED': '',
            '__EVENTVALIDATION': self.event_validation,
            'head1$nowtime': now_date,
            'id': '',
            'datetime': '',
            'FSTYPE': '',
            'a': score_type,
            'txtcsepname': '',
            'txtcsepcode': '',
            'txtSCOREDATE': query_date,
            'ddl': 1
        }
        data = urlencode(data).replace("+", "%2B").replace("/", "%2F").encode('utf8')
        response, status_code = request(self.session, DOMAIN + index_url.format(now_date), 'post', headers,
                                        data=data)
        self.get_parm(response.text)
        html = etree.HTML(response.text)
        total_page = html.xpath('//span[@id="lblpagecount"]')[0].xpath("string(.)")
        return int(total_page)

    def get_html(self, now_date: str, query_date: str, score_type: str, ddl: int):
        print('开始扫描 计算日期={} 类型={} 页数={}'.format(query_date, type_mappings.get(score_type), ddl))
        logger.info('开始扫描 计算日期={} 类型={} 页数={}'.format(query_date, type_mappings.get(score_type), ddl))
        try:
            data = {
                '__EVENTTARGET': 'ddl',
                '__EVENTARGUMENT': '',
                '__LASTFOCUS': '',
                '__VIEWSTATE': self.view_state,
                '__VIEWSTATEGENERATOR': self.view_state_generator,
                '__VIEWSTATEENCRYPTED': '',
                '__EVENTVALIDATION': self.event_validation,
                'head1$nowtime': now_date,
                'id': '',
                'datetime': '',
                'FSTYPE': '',
                'a': score_type,
                'txtcsepname': '',
                'txtcsepcode': '',
                'txtSCOREDATE': query_date,
                'ddl': ddl
            }
            data = urlencode(data).replace("+", "%2B").replace("/", "%2F").encode('utf8')
            response, status_code = request(self.session, DOMAIN + index_url.format(now_date), 'post', headers,
                                            data=data)
            self.get_parm(response.text)
            self.parser(response.text, query_date, score_type)
        except Exception as e:
            print(e)
            logger.error(
                '开始扫描 计算日期={} 类型={} 页数={} 错误={}'.format(query_date, type_mappings.get(score_type), ddl, str(e)))

    def run(self):
        date_start = datetime.datetime.strptime(CALCULATE_DATE, '%Y-%m-%d')
        date_end = datetime.datetime.now()
        now_date = date_end.strftime('%Y-%m-%d')
        while date_start <= date_end:
            query_date = date_start.strftime('%Y-%m-%d')
            for score_type in type_mappings:
                response, status_code = request(self.session, DOMAIN + index_url.format(now_date), 'get', headers)
                self.get_parm(response.text)  # 刷新参数__VIEWSTATE/__VIEWSTATEGENERATOR/__EVENTVALIDATION
                total_page = self.get_total_page(now_date, query_date, score_type)
                for n in range(1, total_page + 1):
                    self.get_html(now_date, query_date, score_type, n)
                date_start += datetime.timedelta(days=1)


def main():
    if RUN_INTERVAL:
        while True:
            EvaluationRank().run()
            time.sleep(60 * 60 * int(RUN_INTERVAL))
    else:
        EvaluationRank().run()


if __name__ == '__main__':
    main()
