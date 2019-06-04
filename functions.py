import re

def simple_get(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
    """
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None


def is_good_response(resp):
    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200 
            and content_type is not None 
            and content_type.find('html') > -1)


def log_error(e):
    """
    It is always a good idea to log errors. 
    This function just prints them, but you can
    make it do anything.
    """
    print(e)
    
def clean_text(t):
    resp = t
    resp = resp.replace('\t',"").replace('\xa0',"")
    resp = re.sub('[\\n]$','',re.sub('^[\\n]','',re.sub('[\\n]+','\\n',resp)))
    return(resp)

def data_topic_extract(forum_html):
    
    data_topic = []
    
    for article in forum_html.findAll('article', class_ = ["cPost"]):

        data_article = {}

        data_article['author'] = clean_text(article.select("aside")[0].select("strong")[0].text)
        nb_mess = article.select("aside")[0].findAll('li',class_='ipsType_light')
        if len(nb_mess)>0 : data_article['nb_messages'] = nb_mess[0].text
        else: data_article['nb_messages'] = "Not_member"
        data_article['date_message'] = article.findAll("time")[0]['datetime']

        #Extracting data from quotes
        quoted_people = []
        quoted_text = []

        for blockquote in article.findAll("blockquote"):
            
            if "data-ipsquote-username" in blockquote.attrs.keys():
                quoted_people.append(blockquote["data-ipsquote-username"])
            else: quoted_people.append("PB_EXTRACTION_namequote")
            content = blockquote.findAll("div",class_="ipsQuote_contents")
            
            if len(content)==0: quoted_text.append("PB_EXTRACTION_content_quote")
            else: quoted_text.append(clean_text(blockquote.findAll("div",class_="ipsQuote_contents")[0].text))

        data_article['quoted_people'] = quoted_people
        data_article['quoted_text'] = quoted_text

        #Extracting data from comment
        comment = article.findAll("div",class_="cPost_contentWrap")[0].findAll("div",class_=["ipsType_normal",
                                                                                             "ipsType_richText",
                                                                                             "ipsContained"])[0]   

        #Extracting refs
        references = []
        for hrefs in comment.findAll("a",attrs={"href":True}):
            references.append(hrefs["href"])

        data_article['references'] = references

        #Extracting comment
        comment_text = []
        children = comment.findChildren(recursive=False)
        for tag in children:
            if tag.name != 'blockquote':
                comment_text.append(clean_text(tag.text))
        data_article['comment_text'] = comment_text

        #Appending data_article to topic data
        data_topic.append(data_article)

    return(data_topic)