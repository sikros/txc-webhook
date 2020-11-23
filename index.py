# -*- coding: utf-8 -*-
import logging,json,urllib,requests,os
webhook = os.environ.get('hook_url')
product_id =  os.environ.get('product_id')

def log(context): #写日志
    logger = logging.getLogger()
    logger.info(context)
    return context

def send(content,url): #发送信息
    headers = {'Content-Type': 'application/json'}    
    data = {
        "msgtype": "markdown",
        "markdown": {
            "content": content,
        }
    }
    r = requests.post(url, headers=headers, json=data)
    return r.content


def handler(environ, start_response):
    #获取回调内容
    try:        
        request_body_size = int(environ.get('CONTENT_LENGTH', 0))    
    except (ValueError):        
        request_body_size = 0   
    request_body = environ['wsgi.input'].read(request_body_size)
    param = json.loads(request_body.decode('utf8'))
    #设定通知变量
    action = param['type']
    content = param['payload']
    tid = param['id']    
    if "post" in action:
        post_user = content['post']['nick_name']
        post_content=content['post']['content']
        post_url=content['post']['post_url']
        post_extra = content['post'].get('extra')
        extra_content="\n"
        if len(post_extra) > 0:
            for k,v in post_extra.items():
                extra_content+=">"+str(k)+":"+str(v)+"\n"
        text="**"+action.replace('post', '主贴').replace('created', '创建').replace('updated', '更新')+"**\n\n["+post_user+":"+post_content+"]("+post_url+")"+extra_content

    if "reply" in action:
        reply_user = content['reply']['nick_name']
        reply_content=content['reply']['content']
        reply_url="https://support.qq.com/products/"+str(product_id)+"/post/"+str(content['reply']['f_title_id'])
        text="**"+action.replace('reply', '回复').replace('created', '创建').replace('updated', '更新')+"**\n\n["+reply_user+":"+reply_content+"]("+reply_url+")"
    #记录日志
    log(text.replace('\n', '').replace('\r', ''))
    #发送信息
    response_body=send(text,webhook)
    #响应回调
    status = '200 OK'
    response_headers = [('Content-type', 'text/plain')]
    start_response(status, response_headers)
    return [str(response_body).encode('UTF-8')]