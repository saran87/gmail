import gmail

g = gmail.login("saran87","L0veuforever1")

print g.logged_in

totalCount = g.all_mail().count()
sentCount = g.sent_mail().count()
ratio =  totalCount / sentCount
print "Total Emails Recieved :" + str(totalCount)

print "Total Emails Sent :" + str(sentCount)

print "Recieved / Sent ratio :" + str(ratio)
