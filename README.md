# Data Preprocessing 

- This part bascially we need handle the NAN values in our dataset 

- Transfer 'object' values into digital data

- Reduce Memory

-----

# Handle NAN Value

- NAN Value has crucial part in data preprocessing. what we did is fill in the float and integer columns with their median, fill in 'unknow' into the 'object' columns.

- Since if we fill in average values may has a chance to get very unbalanced dataset,therefore median values should be more Suitable

- Here is the code we use:

![Handle_nan](https://github.com/Adouken133/final_project/blob/master/FIGURE/handle%20Nan.png)

-----

# Reduce Memory and Transfer values

- Since computer can only read the digital values that we have to transfer all the 'object' values into the digital values.

- Memory Reduce can help us save the time when we run our model, it can improve our effiency of work.

-----

# Feature Engineering 

- This part we are going to explain the Feature Engineering that we did for our project and the purpose of doing it.
  
Bascially there are 4 big part for the whole feature enginnering that we are going to explain about it.
  
-----

### ['P_emaildomain'] Feature 
- Handle the Nonsense value and transfer them in some value in order to make computer to read it:

- The red circle is the one that we need to take care of it:

![P_email](https://github.com/Adouken133/final_project/blob/master/FIGURE/unique_of_email.png)

- Therefore we would like to replace those value then when we will get less pressure when we train our model.

- Also we create an new feature called ['Region_emaildomain']:

- what we did is transfer all the information that we got in ['P_emaildomain'] and then to get all the exact country where those email    sent, which we think the location of those email is going to help our model a lot since each country must have their characteristic。 Here is the code below: ![P_email](https://github.com/Adouken133/final_project/blob/master/FIGURE/email_code.png)


-----

## ['TransactionAmt'] Feature

- This feature bascilly has lots of outlier that we need to handle since we displot it out and find out this one is long_tail type: 

![long_tail](https://github.com/Adouken133/final_project/blob/master/FIGURE/long_amt.png)

- we think that if this feature has too many outliers it might make our model unsteadable, therefore we decide to drop the outlier values in this feature. 

- Here is the code that we use:

![code_for drop_outlier](https://github.com/Adouken133/final_project/blob/master/FIGURE/code_for_drop_outlier.png)

- we decide to drop the value which is greater than the 99 percent of the values also the values which is less than 1 percent. Here is the Figure after drop: 

![drop_outlier](https://github.com/Adouken133/final_project/blob/master/FIGURE/drop_outlier.png)



## ['TransactionDT'] Feature

- This feature contains all the transaction date time which is an object type in the oringal dataframe. Therefore we think we need to transfer them to the dateobject in order to let our computer read it and run.

- More specify we need to add some columns like: 'df['day']', ' df['year']' etc, which is some importance features that transfer it from the ['TransactionDT'].

- Here is the code that we use:

![code_date](https://github.com/Adouken133/final_project/blob/master/FIGURE/code_date_transfer.png)


### ['Card1'], ['Card2'] Features

- .There are some importance features such as ['Card1'], ['Card2'] that has huge amounts of values which is really complex and messed. we think these feature need to be handle it into the category type value. 

- Category values are going to relase some pressure when we are going to train our model. Therefore we find those features and set up some bins(threshold). in this way, the data is more clean and orangize. 

- Also we think only some importance features that need it to be handle in category type since they can affect the model a lot.

- Here is the code that we use:

![other_feature](https://github.com/Adouken133/final_project/blob/master/FIGURE/other_feature_code.png)




### References
All of the links
https://www.kaggle.com/gregorut/videogamesales
https://github.com/GregorUT/vgchartzScrape
-------
