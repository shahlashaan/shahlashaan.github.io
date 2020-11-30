from flask import Flask
from flask import render_template
import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup as bs
import re
from stackapi import StackAPI


myDict = {}
voted_url = 'https://stackoverflow.com/questions/tagged/android?sort=MostVotes&edited=true'
newest_url = "https://stackoverflow.com/questions/tagged/android?sort=Newest&edited=true"

def get_details(url_to_fetch):
	Link = []
	Question = []

	response = requests.get(url_to_fetch)
	# print(response.status_code)
	soup = bs(response.content, 'html.parser')

	tttag = soup.find('div',id="questions")
	# print(tttag)
	i = 0
	for a in tttag.find_all('a', href = re.compile(r'[/]questions[/][0-9]+[/][a-z]+')):
		if i == 10:
			break
		# print(a['href'])
		# print(a.text)
		# print(type(a['href']))
# <a href="http://example.com/{0}">link</a>
		question_id = re.findall(r'[0-9]+',a['href'])
		question_link_with_id= "/" + question_id[0]
		question_link = '<a href='+ question_link_with_id +' id='+question_id[0] + ' onClick="reply_click(this.id)"' +'>'+ a.text + '</a>'  
		# Link.append(a['href'])
		Link.append(question_link)
		Question.append(a.text)
		# myDict[a.text] = a['href']
		i+=1

	return Link,Question 


mostVotedLink,mostVotedQuestion = get_details(voted_url)
newestLink,newestQuestion = get_details(newest_url)




myDict['Most Voted Link'] = mostVotedLink
# myDict['mostVotedQuestion'] = mostVotedQuestion
myDict['Newest Link'] = newestLink
# myDict['newestQuestion'] = newestQuestion

# print(myDict)
df = pd.DataFrame(myDict)


app = Flask(__name__,template_folder='templates')

@app.route('/', methods=("POST", "GET"))
def hello():
	# message = "Hello"
	return render_template('index.html',  tables=[df.to_html(classes='data',escape=False)], titles=df.columns.values)
	# return render_template('index_1.html',message=message)


@app.route('/<int:postID>')
def details(postID):
	SITE = StackAPI('stackoverflow')
	x = SITE.fetch('questions/{ids}', ids=[postID], filter='withbody')
	y = SITE.fetch('questions/{ids}/answers', ids=[postID], filter='withbody')
	total_answers = x["items"][0]['answer_count']
	question_title = x["items"][0]['title']
	all_string = "<h1> Question:"+ question_title +" </h1>"+ x["items"][0]['body']
	for i in range(total_answers):
		all_string = all_string + "<h1> answer "+str(i) + " </h1>" + y["items"][i]['body']
		id = y['items'][i]['answer_id']
		comment =SITE.fetch('answers/{ids}/comments', ids=[id], filter='withbody')
		total_comments=len(comment['items'])
		for k in range(total_comments):
			comment_id = comment['items'][k]['comment_id']
			comment_text = SITE.fetch('comments/{ids}', ids=[comment_id], filter='withbody')
			all_string = all_string + "<h1> comment "+str(k) + " </h1>" + comment_text['items'][0]['body']
			print(comment_text['items'][0]['body'])

	return all_string

if __name__ == "__main__":
	app.run(debug=True)