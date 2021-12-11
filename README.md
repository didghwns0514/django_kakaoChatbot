# - django_kakaoChatbot -

An django framework that communicates with Kakao API server using provided front-end url. <br/>
<br/>
Will provide you `**Real-Time Top Stocks**` at any time.

> Checked running with local PC open PORT only, will be deploied in the future.

## Reference
1) [참조1](https://www.dongyeon1201.kr/9026133b-31be-4b58-bcc7-49abbe893044#b530dc75-789d-4e2e-9993-edb2b328c89b)
2) [참조2](https://django-doc-test-kor.readthedocs.io/en/old_master/intro/tutorial01.html)
3) [참조3-장고 개발 기본](https://076923.github.io/posts/Python-Django-1/)
4) Test - 기본
  1) [장고 test 기본-1](https://velog.io/@hj8853/Django-Unit-Test)
  2) [장고 test 기본-2](https://ugaemi.com/tdd/Django-unit-test/)
  3) [장고 test 기본-3](https://velog.io/@maintain0404/Django에서-Test하기)
5) Test - model
  1) [장고 test Model-1](https://dev-yakuza.posstree.com/ko/django/test/models/)
6) User Model
  1) [장고 User Model-1](https://dev-yakuza.posstree.com/ko/django/custom-user-model/)
7) Logging in Django
  1) [장고 logging-1](https://hikoding.tistory.com/49)

## 중요 참조
1) [비슷한 django 예시](https://github.com/Ryu0n/stock_analyzer)

## 개발 참조
1) Apscheduler 정리
  1) [App Scheduler](https://ediblepotato.tistory.com/3)
  2) [Scheduler 사용 예시](https://medium.com/@kevin.michael.horan/scheduling-tasks-in-django-with-the-advanced-python-scheduler-663f17e868e6)
  3) [Cronjob 추가하기 1](https://hello-bryan.tistory.com/216)
  4) [Cronjob 추가하기 2](https://m.blog.naver.com/varkiry05/221257249284~~~~)
2) [CORS setting](https://hyeonyeee.tistory.com/65)
3) Static 관련 정리
  1) [Static 경로 설정 후, template 사용법](https://0ver-grow.tistory.com/912) 
  2) [Static collect](https://nachwon.github.io/django-deploy-4-static/)
  3) [Static serving done by whitelabel](https://listed.to/@toolate/6967/heroku-x-django-static)
4) 주식 모듈 관련 정리
  1) [yahoo finance 정리 1](https://scribblinganything.tistory.com/377)

**Framework & library used :**
- Django
- Frontend : no webpage yet (communicates with Kakao API-chatbot with JSON format)
  > **Dealing with client request from kakao-chat application** <br/>
  > 1) Client(kakao-chat application user) types formatted text that API-chatbot can understand <br/>
  > 2) API-chatbot transfroms the text in JSON and sends to url-end(OR port) where django is running <br/>
  > 3) Parse Body and get the JSON, handle the request using query and returns the response in JSON format
  > 
- Server :
  - Service method:
    - will be using **wsgi** or **gunicorn** `(not available yet - will be added in the future)`
    - Now server is running on Gunicorn!
  - Business logic:
    - used apscheduler library to continuously crawl information on intervals
    - under scheduler, selenium based function is executed to parse stock information from the web
        ```python
        from apscheduler.schedulers.background import BackgroundScheduler
        from BusinessLogic import API_parser

        def start():
            scheduler = BackgroundScheduler()
            scheduler.add_job(API_parser.update_stock_list, 'interval', seconds=20)
            scheduler.add_job(API_parser.update_news, 'interval', seconds=10)

            scheduler.start()
        
        ```
    - overriding the following method, the following logic will run periodically when app starts.
      ![image](https://user-images.githubusercontent.com/47662495/114277110-d1ab3e80-9a64-11eb-953d-b6a26fc6aed1.png)
      ![image](https://user-images.githubusercontent.com/47662495/114277263-73cb2680-9a65-11eb-9f9a-951cda2355df.png)
  - mySQL
    - stores stock information parsed roughly every minute, stores it in the databse

        ```python
        class StockListData(models.Model):

            source = models.CharField(max_length=100) # 코스피/코스닥
            num = models.IntegerField()
            name = models.CharField(max_length=100)
            price_now = models.FloatField()
            price_compared = models.FloatField()
            price_ratio = models.FloatField()
            price_straight = models.FloatField()
            total_stock_sum = models.IntegerField()
            total_stock_num = models.IntegerField()
            total_foreign_ratio = models.FloatField()
            trade_sum = models.IntegerField()
            per = models.FloatField()
            roe = models.FloatField()
            timestamp = models.DateTimeField()

        def __str__(self):
            return self.name

        ```
    - uses bulk-create and bulk-update + few column indexes when possible for faster performance <br/>
    1)   dynamically select indexes and batchsize on django parsing state

            ```python
            class UpdateStockListState:
                """to check if SQL update with less columns is possible"""

                TOTAL_COL = ['source','num','name','price_now','price_compared','price_ratio',
                            'price_straight','total_stock_sum','total_stock_num','total_foreign_ratio',
                            'trade_sum','per','roe']

                NEW_COL = ['price_now','price_compared','price_ratio', 'total_foreign_ratio',
                        'trade_sum']

                LAST_UPDATE = None
                SAFE_BATCH = 20
                ORI_BATCH = 999

                @staticmethod
                def get():
                    """return column and batch size"""
                    if UpdateStockListState.LAST_UPDATE == None: # never parsed before
                        UpdateStockListState.LAST_UPDATE = datetime.now()
                        return int(UpdateStockListState.SAFE_BATCH), UpdateStockListState.TOTAL_COL
                    else:
                        if datetime.now() - timedelta(hours=7) >= UpdateStockListState.LAST_UPDATE: # exceeded time limit
                            UpdateStockListState.LAST_UPDATE = datetime.now()
                            return int(UpdateStockListState.SAFE_BATCH), UpdateStockListState.TOTAL_COL
                        else:

                            return int(UpdateStockListState.ORI_BATCH // (len(UpdateStockListState.NEW_COL)*2.5)), UpdateStockListState.NEW_COL

            ```
        
    2) bulk example used
        ```python
        ...

        for k in range( int( len(tmp_update)//_batch_size)+1 ):
			StockListData.objects.bulk_update(
                tmp_update[k*_batch_size : (k+1)*_batch_size], col_names)
        ...
        ```
    - parses stock news information and converts into sentiment analysis, stores it <br/> in the database `(not available yet - will be added in the future)`

---
<br/>

## Table of Contents

- Sections
  - [django_kakaoChatbot](https://github.com/didghwns0514/django_kakaoChatbot/blob/master/README.md#django_kakaoChatbot)
  - [Usage](https://github.com/didghwns0514/django_kakaoChatbot/blob/master/README.md#Usage)
  - [Maintainer](https://github.com/didghwns0514/django_kakaoChatbot/blob/master/README.md#Maintainer)


<br/>
<br/>

## Sections

---
### django_kakaoChatbot

**Status :** Live on Local PC( not always on )

**Used :**

- Frontend
  - JSON response to communicate with kakao-chatbot API

- Backend
  - Business logic :
    - Selenium crawler running under apscheduler <br/>
      [Selenium code link](https://github.com/didghwns0514/django_kakaoChatbot/blob/master/BusinessLogic/Parser.py)
  - Database : simple ``mysql`` and ``bulk methods``

<br/>

-----------

### Usage

**Simple usage :**

- image
  1) Add the chatbot in your application <br/>
  ![image](https://user-images.githubusercontent.com/47662495/114262703-57ef6280-9a1c-11eb-9f88-d363052ef357.png)

  2) Buttons will appear for your choice of methods <br/>
   **(only 실시간 급상승 종목 추천(Top Stocks) Button works for now )** <br/>
  ![image](https://user-images.githubusercontent.com/47662495/114262712-68074200-9a1c-11eb-94b8-db64741e4935.png)

  3) Type in which stock catagory you are looking for <br/>
  ![image](https://user-images.githubusercontent.com/47662495/114262722-73f30400-9a1c-11eb-92fb-97756d9b93d5.png)<br/>
  ![image](https://user-images.githubusercontent.com/47662495/114262724-7c4b3f00-9a1c-11eb-83d6-1c434ad4a473.png)

-----------

### Maintainer

**People**: Yang HoJun(양호준)(didghwns0514@gmail.com)

**More Info:**

- Github link : [Link](https://github.com/didghwns0514/django_kakaoChatbot)
- Personal Blog : [Link](https://korshika.tistory.com/)

**Suggestions:**

- Feel free to contact

-----------

## Definitions

*These definitions are provided to clarify any terms used above.*

- **Documentation repositories**: Feel free to share. Thank you!