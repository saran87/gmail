#!/usr/bin/python

import MySQLdb
import re
import gmail
import yaml

def delete(gmail,uids):
  if uids != '':
    flag = '\\Deleted'
    gmail.imap.uid('STORE', uids, '+FLAGS', flag)
    print "Total Message deleted :"  + str(len(gmail.imap.expunge()[1]))
  else:
    print "Total Message deleted :0"

f = open('spec/account.yaml')
configMap = yaml.load(f)
f.close()

g = gmail.login(configMap['email'],configMap['password'])

'''
print g.logged_in

print "========================================================="
print " Labels Available "
print g.labels()
print "========================================================="

#totalCount = g.all_mail().count()
#sentCount = g.sent_mail().count()
#ratio =  totalCount / sentCount

#print "Total Emails Recieved :" + str(totalCount)

#print "Total Emails Sent :" + str(sentCount)

#print "Recieved / Sent ratio :" + str(ratio)

#print "messages count: " + str(len(messages))
test = []
emails = g.all_mail().mail(sender="lrrgla@rit.edu")
print len(emails)
flag = '\\Deleted'
for mail in emails:
  #mail.fetch()
  print mail.uid + "----" + str(mail.labels)
  print mail.flags
  #mail.remove_label("\\Important")
  mail.add_label("\\Trash")
  test.append(mail.uid)

uids = ','.join(test)
print g.imap.uid('STORE', uids, '+FLAGS', flag)
# What are the flags now?
typ, response = g.imap.fetch(uids, '(FLAGS)')
print 'Flags after:', response
print g.imap.expunge()
g.imap.close()'''


# Open database connection
db = MySQLdb.connect("54.225.226.195",db="causbuzz_production",user="root",passwd="dev123" )

# prepare a cursor object using cursor() method
cursor = db.cursor()
messages = g.all_mail().mail(sender="mailer-daemon@amazonses.com")
print "number of messages :" + str(len(messages))
print "email,code,message"
count  = 0
deleteUids = []
notProcess = []
for msg in messages :
    # fetch the message for processing

    msg.fetch()
    code = -1
    email = ''
    message = ''
    if msg.message.get_content_maintype() == "multipart":
        # walk through the message
        for content in msg.message.walk():
            if content.get_content_type() == "message/delivery-status":
                subMsg = content.get_payload()
                for m in subMsg:
                  #Get the Diganostic code for better error message
                  #Dignostic code has below format smtp; 550 5.1.1 <beanshank@comcast.net>
                  if "Diagnostic-code" in m:
                      codes = m["Diagnostic-code"].split(';',2)
                      if len(codes) > 1:
                          codes = codes[1].strip().split(' ', 1)
                          statCodes = re.findall(r'\d+',codes[0].strip())
                          #if there is any status code found take it
                          if len(statCodes) > 0:
                            code = int (statCodes[0])
                            message = codes[1]
                      else:
                          message = codes[0]
                  # Extract the email address from the bounced email
                  # Recipient email will be of the below format
                  if 'Final-Recipient' in m:
                      error = m["Final-Recipient"].split(';')
                      if len(error) > 1:
                        email = error[1].strip()
    else:
      print msg
    if email != '':
        count += 1
        # execute SQL query using execute() method.
        cursor.execute("UPDATE message_status SET status=%s,details=%s WHERE email=%s",(code,message,email))
        deleteUids.append(msg.uid);
        msg.add_label("\\Trash")
        print str(code) + ", " + email + ", " + message
    #else:
    #    notProcess.append(msg.uid)
    #    print msg.body

db.commit()
print "Total Message Processed: " + str(count)
uids = ",".join(deleteUids)
delete(g,uids)
# disconnect from server
db.close()
