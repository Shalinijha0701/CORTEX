# CORTEX External Test Dataset

## Purpose
This package is for external, new-user testing of the CORTEX prototype.

## Dataset properties
- Dataset type: Synthetic demonstration data
- Rows: 90
- Completely new users: 3
- User IDs: TEST_U01, TEST_U02, TEST_U03
- Days per user: 30
- Date range: 2025-06-01 to 2025-06-30
- Training-user overlap: None with U001-U005
- Health-state distribution:
  - Normal: 38
  - Fatigued: 20
  - Stressed: 18
  - Recovery Needed: 14

## Files
- external_test_features_only.csv: Give this file to the trained model.
- external_test_labels.csv: Keep this separate until predictions are generated.
- external_test_data.csv: Combined convenience copy containing features and true labels.

## Correct evaluation procedure
1. Train the model only on the original training dataset.
2. Do not retrain or tune the model using these rows.
3. Run predictions on external_test_features_only.csv.
4. Join predictions with external_test_labels.csv using user_id and date.
5. Report:
   - Recovery-score MAE
   - Health-state accuracy
   - Per-class precision and recall
   - Confusion matrix

## Observed demonstration result

Using the saved demonstration model artifacts:

- Recovery-score MAE: 11.462
- Health-state accuracy: 0.667

See `test_predictions.csv` for the row-level actual-versus-predicted output.

## Important limitation
The dataset is synthetic and designed for functional model evaluation. Results do not establish clinical or medical accuracy.
