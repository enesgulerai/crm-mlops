import os
import sys

import onnxmltools
import optuna
import xgboost as xgb
from dotenv import load_dotenv
from onnxmltools.convert.common.data_types import FloatTensorType
from sklearn.metrics import accuracy_score, f1_score

# Path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.utils.common import load_config
from src.utils.exception import CustomException
from src.utils.logger import get_logger

# Initialize Logger
logger = get_logger(__name__)

load_dotenv()


class ModelTrainer:
    def __init__(self):
        try:
            logger.info("Initializing Model Trainer configuration...")
            self.config = load_config()
            self.trainer_config = self.config["model_trainer"]
            self.n_trials = self.trainer_config["n_trials"]
            self.onnx_path = self.trainer_config["output_path"]

        except Exception as e:
            logger.error("Failed to initialize Model Trainer.")
            raise CustomException(e, sys)

    def optimize_hyperparameters(self, X_train, y_train, X_test, y_test) -> dict:
        def objective(trial):
            param = {
                "verbosity": 0,
                "objective": "binary:logistic",
                "booster": "gbtree",
                "tree_method": "hist",
                "n_estimators": trial.suggest_int("n_estimators", 50, 300),
                "max_depth": trial.suggest_int("max_depth", 3, 10),
                "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3),
                "subsample": trial.suggest_float("subsample", 0.5, 1.0),
                "colsample_bytree": trial.suggest_float("colsample_bytree", 0.5, 1.0),
                "random_state": 42,
            }

            model = xgb.XGBClassifier(**param)
            model.fit(X_train, y_train)
            preds = model.predict(X_test)
            accuracy = accuracy_score(y_test, preds)
            return accuracy

        logger.info(f"Starting Offline Optuna Optimization ({self.n_trials} trials)...")
        study = optuna.create_study(direction="maximize")
        study.optimize(objective, n_trials=self.n_trials)

        logger.info(f"Best params found: {study.best_params}")
        return study.best_params

    def train_and_save_onnx(self, X_train, y_train, X_test, y_test):
        try:
            # 1. Optimization
            best_params = self.optimize_hyperparameters(X_train, y_train, X_test, y_test)

            # 2. Final Model Training
            logger.info("Training Final Model (Offline)...")
            final_model = xgb.XGBClassifier(**best_params)
            final_model.fit(X_train, y_train)

            # 3. Calculate Metrics
            y_pred = final_model.predict(X_test)
            acc = accuracy_score(y_test, y_pred)
            f1 = f1_score(y_test, y_pred)
            logger.info(f"Metrics -> Accuracy: {acc:.4f}, F1: {f1:.4f}")

            # 4. ONNX Conversion and Local Registration
            logger.info("Converting to ONNX and Saving Locally...")
            initial_type = [("float_input", FloatTensorType([None, X_train.shape[1]]))]
            onnx_model = onnxmltools.convert_xgboost(final_model, initial_types=initial_type)

            # Folder Control
            os.makedirs(os.path.dirname(self.onnx_path), exist_ok=True)

            # Save Model
            onnxmltools.utils.save_model(onnx_model, self.onnx_path)

            logger.info(f"Model saved locally at: {self.onnx_path}")

        except Exception as e:
            logger.error("Error in training pipeline")
            raise CustomException(e, sys)


if __name__ == "__main__":
    from src.components.data_ingestion import DataIngestion
    from src.components.data_transformation import DataTransformation

    try:
        logger.info(">>>>> Offline Training Started <<<<<")
        ingestion = DataIngestion()
        df = ingestion.initiate_data_ingestion()

        transformer = DataTransformation()
        X_train, X_test, y_train, y_test, _ = transformer.initiate_data_transformation(df)

        trainer = ModelTrainer()
        trainer.train_and_save_onnx(X_train, y_train, X_test, y_test)
        logger.info(">>>>> Execution Finished <<<<<")

    except Exception as e:
        logger.error(e)
        print(e)
