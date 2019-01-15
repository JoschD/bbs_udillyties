""" Example of Isolation Forest (from scikit-learn).

A bit updated:
    - assume training data is fully correct
    - mark samples as to how they are judged

Problem:
    - data has x/y correlation which is not taken into account. See:
    https://arxiv.org/pdf/1811.02141.pdf
"""

print(__doc__)

import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest

rng = np.random.RandomState(42)

# Generate train data
X = 0.3 * rng.randn(10000, 2)
X_train = np.r_[X + 2, X - 2]
# Generate some regular novel observations
X = 0.3 * rng.randn(20, 2)
X_test = np.r_[X + 2, X - 2]
# Generate some abnormal novel observations
X_outliers = rng.uniform(low=-4, high=4, size=(20, 2))

# fit the model
clf = IsolationForest(behaviour='new', max_samples=512,
                      random_state=rng, contamination="auto",
                      max_features=1.)

clf.fit(X_train)
y_pred_train = clf.predict(X_train)
y_pred_test = clf.predict(X_test)
y_pred_outliers = clf.predict(X_outliers)

# plot the line, the samples, and the nearest vectors to the plane
xx, yy = np.meshgrid(np.linspace(-5, 5, 50), np.linspace(-5, 5, 50))
Z = clf.decision_function(np.c_[xx.ravel(), yy.ravel()])
Z = Z.reshape(xx.shape)

plt.title("IsolationForest")
plt.contourf(xx, yy, Z, cmap=plt.cm.Blues_r)

b1 = plt.scatter(X_train[:, 0], X_train[:, 1], c='white',
                 s=20, edgecolor='k')

test_mask = y_pred_test == 1
outliers_mask = y_pred_outliers == 1

b2 = plt.scatter(X_test[test_mask, 0], X_test[test_mask, 1], c='green',
                 s=20, edgecolor='green')
c = plt.scatter(X_outliers[outliers_mask, 0], X_outliers[outliers_mask, 1], c='green',
                s=20, edgecolor='red')

b2 = plt.scatter(X_test[~test_mask, 0], X_test[~test_mask, 1], c='red',
                 s=20, edgecolor='green')
c = plt.scatter(X_outliers[~outliers_mask, 0], X_outliers[~outliers_mask, 1], c='red',
                s=20, edgecolor='red')
plt.axis('tight')
plt.xlim((-5, 5))
plt.ylim((-5, 5))
plt.legend([b1, b2, c],
           ["training observations",
            "new regular observations", "new abnormal observations"],
           loc="upper left")
plt.show()