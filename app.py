from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from bs4 import BeautifulSoup 
import requests

#don't change this
matplotlib.use('Agg')
app = Flask(__name__) #do not change this

#insert the scrapping here
url_get = requests.get('https://www.imdb.com/search/title/?release_date=2021-01-01,2021-12-31')
soup = BeautifulSoup(url_get.content,"html.parser")

#find your right key here
table = soup.find('div', attrs={'class':'lister list detail sub-list'})
Title = table.find_all('h3', attrs={'class':'lister-item-header'})

row_length = len(Title)

temp = [] #initiating a tuple

for i in range(0, row_length):
    #get Title
    Title = table.find_all('h3', attrs={'class':'lister-item-header'})[i].text
    Title = Title.split('.')[1] #to remove number with split character "."
    Title = Title.split('(')[0] #to remove number with split character "."
    Title = Title.strip() #to remove excess white space
    Title = Title.replace('\n','') #to remove special character ('\n')
      
    #get Ratings
    Ratings = table.find_all('div', attrs={'class':'inline-block ratings-imdb-rating'})[i].text
    Ratings = Ratings.strip() #to remove excess white space
     
    #get MetaScore
    MetaScore = table.find_all('div', attrs={'class':'ratings-bar'})[i].text.replace('\n','').split('/')[1].replace('10X\xa0','').replace('Metascore','')
    MetaScore = MetaScore.strip() #to remove excess white space  
    
    #get Votes
    Votes = table.find_all('p', attrs={'class':'sort-num_votes-visible'})[i].text
    Votes = Votes.strip() #to remove excess white space
    Votes = Votes.replace('\n','') #to remove special character ('\n')
    Votes = Votes.split(':')[1] 
    Votes = Votes.split('|')[0]
        
    #append for each i
    temp.append((Title,Ratings,MetaScore,Votes))
    
temp 

#change into dataframe
Movie2021 = pd.DataFrame(temp, columns = ('Title','Ratings','MetaScore', 'Votes'))

#insert data wrangling here
Movie2021['Ratings'] = Movie2021['Ratings'].astype('float64')
Movie2021['Votes'] = Movie2021['Votes'].str.replace(',','')
Movie2021['Votes'] = Movie2021['Votes'].astype('int64')
Movie2021['MetaScore'] = Movie2021['MetaScore'].replace('', "0", regex=False) #Fill blank Value with 0
Movie2021['MetaScore'] = Movie2021['MetaScore'].astype('int64')
Movie2021 = Movie2021.set_index('Title')
#end of data wranggling 

@app.route("/")
def index(): 
	
	card_data = f'{Movie2021["Ratings"].mean().round(2)}' #be careful with the " and ' 

	# generate plot
	ax = Movie2021.plot(figsize = (20,9)) 
	
	# Rendering plot
	# Do not change this
	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True)
	figfile.seek(0)
	figdata_png = base64.b64encode(figfile.getvalue())
	plot_result = str(figdata_png)[2:-1]

	# render to html
	return render_template('index.html',
		card_data = card_data, 
		plot_result=plot_result
		)


if __name__ == "__main__": 
    app.run(debug=True)