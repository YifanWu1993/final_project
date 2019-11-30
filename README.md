# cebd1160_Final_project


| Name | Date |
|:-------|:---------------|
|Yifan Wu |2019/11/29|

-----

### Resources
Your repository should include the following:

- Python script for your analysis
- Results figure/saved file
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
![PCA](https://github.com/Adouken133/final_project/blob/master/PCA.png)



### Results
In my F1 and classification report ![Report](https://github.com/Adouken133/final_project/blob/master/Report.png)
it can show me my precision is actually super low here. So it is actually hard to classify the relationship between Genre 
and the other features



### Discussion
Bascially in my opinion my method did not sovle this problem since the F1 score and precision is so low. There are a few probability that could make this happened. Maybe my algorithm is not be able to solve this, or maybe this dataset is not appropriate for the classification case


### References
All of the links

-------
