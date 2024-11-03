answer = ""
import smtplib
from email.mime.text import MIMEText
from email.header import Header
def main():
  # 第三方 SMTP 服务
  mail_host="smtp.163.com"  # 设置服务器
  mail_user="srszzw@163.com"  # 用户名
  mail_pass="MSTyiN4LULRPzQ9E"  # 口令
  sender = 'srszzw@163.com'
  receivers = ['741992282@qq.com']  # 接收邮件，可设置为你的邮箱地址
  # 创建一个带附件的实例
  message = MIMEText(answer, 'plain', 'utf-8')
  message['From'] = sender
  message['To'] = receivers[0]
  subject = '国庆临近提醒'
  message['Subject'] = Header(subject, 'utf-8')
  try:
      smtpObj = smtplib.SMTP()
      smtpObj.connect(mail_host, 25)    # 25 为 SMTP 端口号
      smtpObj.login(mail_user,mail_pass)
      smtpObj.sendmail(sender, receivers, message.as_string())
      return {"mail_send_status":"success"}
  except smtplib.SMTPException as e:
      return {"mail_send_status":"fail"}
print(main())