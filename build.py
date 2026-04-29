import os
import sys

sys.path.insert(0, '.')

from src.components.data_ingestion import DataIngestion
from src.components.data_transformation import DataTransformation
from sklearn.ensemble import RandomForestRegressor
from src.utils import save_object

print("Starting model training for deployment...")

obj = DataIngestion()
train_path, test_path = obj.initiate_data_ingestion()

dt = DataTransformation()
train_arr, test_arr, _ = dt.initiate_data_transformation(train_path, test_path)

X_train, y_train = train_arr[:, :-1], train_arr[:, -1]
X_test,  y_test  = test_arr[:, :-1],  test_arr[:, -1]

model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
model.fit(X_train, y_train)

from sklearn.metrics import r2_score
score = r2_score(y_test, model.predict(X_test))
print(f"Model trained. R2 Score: {score:.4f}")

save_object('artifacts/model.pkl', model)
print("model.pkl saved to artifacts/")
