# 知乎话题抓取
通过话题入口抓取话题下所有问题和回答

## 数据存储
MySQL: topic question answer

## 数据抓取
requwsts/xpath/re

## 配置
mac 

## cookie
解密chrome cookie文件

## 变更
知乎答案获取接口发生变化，之前是随意访问的get:<br>
https://www.zhihu.com/api/v4/questions/{}/answers?sort_by=default&include={}&limit=20&offset={}<br>
现在变成了post：<br>
https://www.zhihu.com/node/QuestionAnswerListV2<br>
Form Data:<br>
- method:next<br>
- params:{"url_token":36535039,"pagesize":10,"offset":30}<br>

接口返回数据格式由原来的json数据变成了html,需要进一步xpath解析.<br>
几个topic数据已在变化前全部抓下来了,后面会放到百度云上.

## 抓取结果
topic记录: 30<br>
question记录: 8868<br>
answer记录: 3145338<br>
链接: https://pan.baidu.com/s/1slW6cSt 密码: 5fs4

## 建议
知乎有封禁策略，建议使用小号抓取

## 示例
topic
![save-to-screen][1]

question
![save-to-screen][2]

answer
![save-to-screen][3]

[1]: https://raw.githubusercontent.com/hectorhua/zhihu_topic/master/pic/topic.png
[2]: https://raw.githubusercontent.com/hectorhua/zhihu_topic/master/pic/question.png
[3]: https://raw.githubusercontent.com/hectorhua/zhihu_topic/master/pic/answer.png

