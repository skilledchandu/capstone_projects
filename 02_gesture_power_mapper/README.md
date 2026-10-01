Gesture to Power Mapper
=======================

Run
  pip install -r requirements.txt
  streamlit run app.py

Optional real model
1. Train 4 classes in Teachable Machine: open_palm, fist, peace, point.
2. Export the Keras model.
3. Save it as model/keras_model.h5 and labels as model/labels.txt.
Without those files, the app uses a small demo classifier so it still runs.
