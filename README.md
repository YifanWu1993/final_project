# Feature Engineering 
  This part we are going to explain the Feature Engineering that we did for our project and the purpose of doing it.
  
Bascially there are 4 big part for the whole feature enginnering that we are going to explain about it.
  

-----

### ['P_emaildomain'] Feature 
- Handle the Nonsense value and transfer them in some value in order to make computer to read it:https://github.com/Adouken133/final_project/blob/master/FIGURE/unique_of_email.png

- Python script for your analysis:/final%20project.py
- Results figure/saved file:/FIGURE
- Dockerfile for your experiment
- runtime-instructions in a file named RUNME.md

-----

## Research Question

As a Video game freak, i am curious about which type of game has the better sales in each area
i would like to know can we predcit the connection between the game type and the sales in each area

### Abstract

So the dataset i have contains every areas sale such as NA_sales
and EU_Sales. It also contains every single Genre which is my
target. My challenge isto trying to classify the game genre and 
trying to figure out if there is any conncection with sales.As i classify all the Genre such as Shooting, First_Role_Play. 
i will try to find out if there is any specific Genre has related to the sales


### Introduction

The dataset i got is from Kaggle(https://www.kaggle.com/gregorut/videogamesales).
The script to scrape the data is available at https://github.com/GregorUT/vgchartzScrape. 
It is based on BeautifulSoup using Python. There are 16,598 records. 2 records were dropped due to incomplete information.

### Methods

classification case.
it can not only solve the simple classification case but also can handle the multiple classification case.
in the project, there are over 10 types of game which i need to classify
![PCA](https://github.com/Adouken133/final_project/blob/master/FIGURE/PCA.png)



### Results
![Report](https://github.com/Adouken133/final_project/blob/master/FIGURE/Report.png)
In my F1 and classification report can show me my precision is actually super low here. So it is actually hard to classify the relationship between Genre and the other features
![compare](https://github.com/Adouken133/final_project/blob/master/FIGURE/Comparsion_image.png)

After i drop some features and got an new result actually isolate the JP_SALES the precision actually increase a little 

![new_report](https://github.com/Adouken133/final_project/blob/master/FIGURE/new_report.png) 

And this is an JP_SALE Compare Genre plot here 

![new_compare](https://github.com/Adouken133/final_project/blob/master/FIGURE/NEW_COMPARE.png)

Here is the new PCA 

![new_PCA](https://github.com/Adouken133/final_project/blob/master/FIGURE/PCA_AFTER_NEW_EXPLOATION.png)

As we can see As i isolate the jp_sales and drop some other features. the result is getting better 




### Discussion
Bascially in my opinion my method did not sovle this problem since the F1 score and precision is so low. There are a few probability that could make this happened. Maybe my algorithm is not be able to solve this, or maybe this dataset is not appropriate for the classification case
![corr](https://github.com/Adouken133/final_project/blob/master/FIGURE/corr.png)

### References
All of the links
https://www.kaggle.com/gregorut/videogamesales
https://github.com/GregorUT/vgchartzScrape
-------
