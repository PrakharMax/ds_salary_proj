# -*- coding: utf-8 -*-
"""
Created on Mon Aug 11 12:27:08 2025

@author: prakasp2
"""

from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import GridSearchCV, cross_val_score, train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression, Lasso
import statsmodels.api as sm
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load data
df = pd.read_csv('EDA_Data.csv')

# Select relevant columns
df_model = df[['avg_salary', 'rating', 'hourly',
               'job_simp', 'state', 'job_seniority']]

# One-hot encode categorical variables
df_dum = pd.get_dummies(df_model).astype(int)

# Prepare X and y
X = df_dum.drop('avg_salary', axis=1)
y = df_dum['avg_salary'].values

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42)

# Multiple Linear Regression with statsmodels (use separate variable for OLS)
X_sm = sm.add_constant(X)
ols_model = sm.OLS(y, X_sm).fit()
print(ols_model.summary())

# Linear Regression with sklearn
lm = LinearRegression()
lm.fit(X_train, y_train)
print("Linear Regression CV Neg MAE:", np.mean(cross_val_score(lm, X_train, y_train,
                                                               scoring='neg_mean_absolute_error', cv=3)))

# Lasso Regression - tune alpha manually
lasso = Lasso()
print("Lasso CV Neg MAE:", np.mean(cross_val_score(lasso, X_train, y_train,
                                                   scoring='neg_mean_absolute_error', cv=3)))

alpha = []
error = []
for i in range(1, 1000):
    a = i / 1000
    alpha.append(a)
    lasso_model = Lasso(alpha=a)
    cv_score = np.mean(cross_val_score(lasso_model, X_train, y_train,
                                       scoring='neg_mean_absolute_error', cv=3))
    error.append(cv_score)

plt.plot(alpha, error)
plt.xlabel('Alpha')
plt.ylabel('CV Neg MAE')
plt.title('Lasso Alpha vs Neg MAE')
plt.show()

# Get alpha with best error
err = list(zip(alpha, error))
df_err = pd.DataFrame(err, columns=['alpha', 'error'])
best_alpha_row = df_err[df_err.error == max(df_err.error)]
print("Best alpha for Lasso:", best_alpha_row)

# Random Forest without tuning
rf = RandomForestRegressor(random_state=42)
print("Random Forest CV Neg MAE:", np.mean(cross_val_score(rf, X_train, y_train,
                                                           scoring='neg_mean_absolute_error', cv=3)))

# Tune Random Forest with GridSearchCV (corrected parameters)
parameters = {
    'n_estimators': range(10, 300, 10),
    'criterion': ('squared_error', 'absolute_error'),  # updated values
    'max_features': ('sqrt', 'log2')  # removed 'auto'
}

gs = GridSearchCV(
    rf, parameters, scoring='neg_mean_absolute_error', cv=3, n_jobs=-1)
gs.fit(X_train, y_train)

print("Best params found by GridSearchCV:", gs.best_params_)
print("Best CV Neg MAE from GridSearchCV:", gs.best_score_)


# test ensembles


# Best alpha from your earlier Lasso tuning
best_alpha = df_err.loc[df_err.error.idxmax(), 'alpha']

# Train Lasso with best alpha on full training data
best_lasso = Lasso(alpha=best_alpha)
best_lasso.fit(X_train, y_train)

# Predictions
tpred_lm = lm.predict(X_test)
tpred_lasso = best_lasso.predict(X_test)
tpred_rf = gs.best_estimator_.predict(X_test)

# Calculate MAEs
mae_lm = mean_absolute_error(y_test, tpred_lm)
mae_lasso = mean_absolute_error(y_test, tpred_lasso)
mae_rf = mean_absolute_error(y_test, tpred_rf)
mae_ensemble = mean_absolute_error(y_test, (tpred_lm + tpred_rf) / 2)

print(f"Linear Regression MAE: {mae_lm:.2f}")
print(f"Lasso Regression MAE: {mae_lasso:.2f}")
print(f"Random Forest MAE: {mae_rf:.2f}")
print(f"Ensemble (LM + RF) MAE: {mae_ensemble:.2f}")
