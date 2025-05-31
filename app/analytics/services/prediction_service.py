import io
import joblib
import pandas as pd
import numpy as np
from django.core.files.base import ContentFile
from django.db.models import Avg
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer

from app.authentication.models import Student
from app.academic.models import Grade, Trimester, Enrollment, Period
from base.storage import PrivateMediaStorage

class PerformancePredictionService:
    MODEL_FILENAME = 'student_performance_model.joblib'
    SCALER_FILENAME = 'student_performance_scaler.joblib'
    
    FEATURE_COLUMNS = [
        'avg_grade_prev_trimester',
        'num_assessments_prev_trimester',
        'attendance_percentage_overall'
    ]

    def __init__(self):
        self.storage = PrivateMediaStorage(custom_path='ml_models', file_overwrite=True)
        self.model = None
        self.scaler = None
        self._load_model_and_scaler()

    def _load_model_and_scaler(self):
        if self.storage.exists(self.MODEL_FILENAME) and self.storage.exists(self.SCALER_FILENAME):
            try:
                with self.storage.open(self.MODEL_FILENAME, 'rb') as model_file:
                    self.model = joblib.load(model_file)
                with self.storage.open(self.SCALER_FILENAME, 'rb') as scaler_file:
                    self.scaler = joblib.load(scaler_file)
            except Exception:
                self.model = None
                self.scaler = None
        else:
            self.model = None
            self.scaler = None
            
    def _get_trimester_data(self, student, trimester, course):
        grades_in_trimester = Grade.objects.filter(
            student=student,
            assessment_item__trimester=trimester,
            assessment_item__course=course
        )
        
        avg_grade = grades_in_trimester.aggregate(Avg('value'))['value__avg']
        num_assessments = grades_in_trimester.values('assessment_item').distinct().count()
        
        return {
            'avg_grade': avg_grade if avg_grade is not None else np.nan,
            'num_assessments': num_assessments
        }

    def _prepare_training_data(self):
        dataset = []
        active_students = Student.objects.filter(user__is_active=True)

        for student in active_students:
            enrollments = Enrollment.objects.filter(student=student, status='active').select_related('course', 'period')
            for enrollment in enrollments:
                trimesters = Trimester.objects.filter(period=enrollment.period).order_by('start_date')
                
                if len(trimesters) < 2:
                    continue

                for i in range(1, len(trimesters)):
                    prev_trimester = trimesters[i-1]
                    current_trimester_as_target = trimesters[i]

                    prev_trimester_data = self._get_trimester_data(student, prev_trimester, enrollment.course)
                    target_trimester_data = self._get_trimester_data(student, current_trimester_as_target, enrollment.course)
                    
                    if pd.isna(prev_trimester_data['avg_grade']) or pd.isna(target_trimester_data['avg_grade']):
                        continue

                    attendance_percentage = np.nan
                    if hasattr(student, 'attendance_percentage') and student.attendance_percentage is not None:
                         attendance_percentage = student.attendance_percentage

                    features = {
                        'avg_grade_prev_trimester': prev_trimester_data['avg_grade'],
                        'num_assessments_prev_trimester': prev_trimester_data['num_assessments'],
                        'attendance_percentage_overall': attendance_percentage,
                    }
                    dataset.append({**features, 'target_avg_grade': target_trimester_data['avg_grade']})
        
        if not dataset:
            return None, None
            
        df = pd.DataFrame(dataset)
        X = df[self.FEATURE_COLUMNS]
        y = df['target_avg_grade']
        return X, y

    def train_performance_model(self):
        X, y = self._prepare_training_data()

        if X is None or X.empty:
            return {"status": "error", "message": "Not enough data to train the model."}

        preprocessor = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='mean')),
            ('scaler', StandardScaler())
        ])

        regressor = RandomForestRegressor(n_estimators=100, random_state=42, oob_score=True)
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        X_train_processed = preprocessor.fit_transform(X_train)
        X_test_processed = preprocessor.transform(X_test)
        
        regressor.fit(X_train_processed, y_train)
        
        score = regressor.score(X_test_processed, y_test)
        oob_score = regressor.oob_score_ if hasattr(regressor, 'oob_score_') else 'N/A'
        
        model_buffer = io.BytesIO()
        joblib.dump(regressor, model_buffer)
        model_buffer.seek(0)
        self.storage.save(self.MODEL_FILENAME, ContentFile(model_buffer.read()))

        scaler_buffer = io.BytesIO()
        joblib.dump(preprocessor, scaler_buffer)
        scaler_buffer.seek(0)
        self.storage.save(self.SCALER_FILENAME, ContentFile(scaler_buffer.read()))
        
        self._load_model_and_scaler()

        return {
            "status": "success",
            "message": "Model trained successfully and saved to S3.",
            "test_r2_score": score,
            "oob_score": oob_score,
        }

    def _get_features_for_prediction(self, student: Student):
        last_graded_trimester_data = {
            'avg_grade_prev_trimester': np.nan,
            'num_assessments_prev_trimester': np.nan,
            'attendance_percentage_overall': np.nan,
        }

        if hasattr(student, 'attendance_percentage') and student.attendance_percentage is not None:
            last_graded_trimester_data['attendance_percentage_overall'] = student.attendance_percentage
        
        active_enrollments = Enrollment.objects.filter(student=student, status='active').select_related('course', 'period').order_by('-period__start_date')
        
        found_data = False
        for enrollment in active_enrollments:
            completed_trimesters = Trimester.objects.filter(
                period=enrollment.period,
                assessment_items__grades__student=student
            ).distinct().order_by('-start_date')

            if completed_trimesters.exists():
                last_completed_trimester_for_features = completed_trimesters.first()
                trimester_data = self._get_trimester_data(student, last_completed_trimester_for_features, enrollment.course)
                
                last_graded_trimester_data['avg_grade_prev_trimester'] = trimester_data['avg_grade']
                last_graded_trimester_data['num_assessments_prev_trimester'] = trimester_data['num_assessments']
                found_data = True
                break

        df_features = pd.DataFrame([last_graded_trimester_data], columns=self.FEATURE_COLUMNS)
        return df_features

    def predict_student_performance(self, student_id: int):
        if self.model is None or self.scaler is None:
            return {"error": "Model or preprocessor not trained/loaded. Please train the model first."}

        try:
            student = Student.objects.get(pk=student_id)
        except Student.DoesNotExist:
            return {"error": f"Student with ID {student_id} not found."}

        features_df = self._get_features_for_prediction(student)
        
        try:
            processed_features = self.scaler.transform(features_df)
        except Exception as e:
             return {"error": f"Error during feature preprocessing for prediction: {str(e)}", "raw_features": features_df.to_dict()}

        try:
            prediction = self.model.predict(processed_features)
            predicted_avg_grade = round(float(prediction[0]), 2)
        except Exception as e:
            return {"error": f"Error during model prediction: {str(e)}"}

        return {
            "student_id": student_id,
            "predicted_next_trimester_avg_grade": predicted_avg_grade,
            "comment": "Prediction based on historical performance and overall attendance."
        }

performance_prediction_service = PerformancePredictionService()