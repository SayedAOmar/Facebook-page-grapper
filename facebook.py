#!/usr/bin/python
# -*- coding: utf-8 -*-
import requests
import time
import random
import codecs
import json
import sys
import re
reload(sys)  
sys.setdefaultencoding('utf8')
class FacebookAPI():
	"""docstring for FacebookAPI"""
	def __init__(self):
		self.env			= json.loads(open('env.conf','r').read())
		self.version  		= self.env['version']
		self.accessToken 	= self.env['facebook_accessToken']
		self.posts_file     = open(self.env['posts_file'],'w+')
		self.comments_file  = open(self.env['comments_file'],'w+')
		self.posts_file.write("page_id,post_id,post_text,comments_count,shares_count,post_time\n")
		self.comments_file.write("post_id,commen_id,message,comment_time\n")
	def clean(self,text):

		text 				= re.sub(r','," ",text)
		text 				= re.sub(r'\n'," ",text)
		text 				= re.sub(r'\r'," ",text)
		text 				= re.sub(r'\''," ",text)
		text 				= re.sub(r'\"'," ",text)
		return text.encode('utf-8')
		

	def get_page_posts(self,page_id):
		url 				= "https://graph.facebook.com/"+str(page_id)+"/posts?access_token="+str(self.accessToken)+""
		r 					= requests.get(url)
		r 					= json.loads(r.text)
		posts_count			= len(r['data'])
		for post in r['data']:
			try:
				message 	= post['message']
			except Exception as e:
				message 	= post['story']
			post['message'] = message.encode('utf-8')

			comments_count  = self.get_post_comments(post['id'])
			shares_count    = self.get_post_shares_count(post['id'])
			post_data 		= {
					            'post_id'         : post['id'].split('_')[1]        ,
					            'page_id'         : page_id       ,
					            'post_text'       : self.clean(post['message'])      ,
					            'comments_count'  : str(comments_count)          ,
					            'shares_count'    : str(shares_count)          ,
					            'post_time'       : str(post['created_time'])
					    	  }
			self.posts_file.write(str(post_data['page_id'])+','+str(post_data['post_id'])+','+str(post_data['post_text'])+','+\
				str(post_data['comments_count'])+','+str(post_data['shares_count'])+','+str(post_data['post_time'])+'\n')


	def get_post_comments(self,post_id):
		url 				= "https://graph.facebook.com/v2.12/"+str(post_id)+"/comments?access_token="+str(self.accessToken)+""
		r 					= requests.get(url)
		comments			= json.loads(r.text)
		comments_count 		= len(comments['data'])
		for comment in comments['data']:
			message         = self.clean(comment['message'].encode('utf-8'))
			#print comment
			self.comments_file.write(post_id+','+comment['id']+','+message+','+comment['created_time']+'\n')
		return comments_count


	def get_post_shares_count(self,post_id):
		url 				= "https://graph.facebook.com/v2.12/"+str(post_id)+"?fields=shares&access_token="+str(self.accessToken)+""
		r 					= requests.get(url)
		data    			= json.loads(r.text)
		try:
			shares_count 	= data['shares']['count']
		except Exception as e:
			shares_count 	= 0
		return shares_count



if __name__=='__main__':
	fb 					= FacebookAPI()
	page_id 			= 151146158251940
	fb.get_page_posts(page_id)