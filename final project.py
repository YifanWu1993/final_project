import pandas as pd
import numpy as np
from sklearn import preprocessing
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import Imputer
from sklearn.decomposition import PCA

np.warnings.filterwarnings('ignore')

vgsale = pd.read_csv('vgsales.csv')


# Transforming the target information in numerical information
Tf = preprocessing.LabelEncoder()
new_Genre = Tf.fit_transform(vgsale['Genre'])
vgsale['Genre_new'] = new_Genre


# Encoding categorical variables using dummy variables
encoded_Publisher = pd.get_dummies(vgsale['Publisher'], drop_first=True)
encoded_Platform = pd.get_dummies(vgsale['Platform'], drop_first=True)
vgsale = pd.concat([vgsale, encoded_Publisher, encoded_Platform], axis=1)

# Drop useless Column
vgsale.drop(['Name', 'Genre', 'Platform', 'Publisher', 'EU_Sales', 'NA_Sales', 'Other_Sales', 'Global_Sales', 'Rank'], axis=1, inplace=True)


#fill Nan and infinte values
imputer = Imputer(strategy='median')
FN = imputer.fit_transform(vgsale)
vgsale = pd.DataFrame(FN, columns=vgsale.columns)


#Apply machine model
X = vgsale.drop('Genre_new', axis=1)
y = vgsale['Genre_new']



X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.35)



from sklearn.linear_model import LogisticRegression
lr = LogisticRegression()
lr.fit(X_train, y_train)

predicted = lr.predict(X_test)

#test model
# Printing the classification report
from sklearn.metrics import classification_report, confusion_matrix, f1_score
print('Classification Report')
print(classification_report(y_test, predicted))

# Printing the classification confusion matrix (diagonal is true)
print('Confusion Matrix')
print(confusion_matrix(y_test, predicted))

print('Overall f1-score')
print(f1_score(y_test, predicted, average="macro"))


# Visualizing structure of dataset in 2D
pca = PCA(n_components=2)
proj = pca.fit_transform(X)
plt.figure(figsize=(20,20))
plt.scatter(proj[:, 0], proj[:, 1], c=y, edgecolors='black')
plt.colorbar()
plt.show()

# This time we plot multiple plots on the same axes, to get some perspective on their comparisons
plt.figure(figsize=(10,10))
plt.scatter(vgsale['Genre_new'], vgsale['JP_Sales'], alpha=0.7, label='JP_Sales')
plt.xlabel('Genre_new')
plt.ylabel('JP_Sales')
plt.title(f'Genre_new comparisons')
plt.legend()
plt.show()

plt.close()
