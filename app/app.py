# Import dependencies
import pandas as pd
import numpy as np
from config import google_api_key
from utils import  address2api, api2latlng, str2num
import json
import requests
import sqlite3
from sqlalchemy import create_engine
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.externals import joblib
from sklearn.metrics import f1_score, accuracy_score
import pickle
from flask import (
    Flask,
    render_template,
    request, 
    redirect,
    jsonify)

app = Flask(__name__)

# load data
engine = create_engine('sqlite:///../data/lender_data1.db')
df = pd.read_sql_table('Lender', engine)

# load model
model = pickle.load(open("../model/model_rf.pkl", 'rb'))

# load features
filename = '../model/features.pkl'
features = pickle.load(open(filename, 'rb'))

# load imputer
filename = '../model/imputer.pkl'
missing_imputer = pickle.load(open(filename, 'rb'))
columns_to_impute = [col for col in features if "MF" not in col]

# load scaler
scaler_filename = "../model/scaler.save"
scaler = joblib.load(scaler_filename) 

# index webpage receives user input text for model
@app.route('/')
@app.route('/index')
def index():
    """Display home page"""
    return render_template('master.html')

@app.route("/api_lender_data")
def api_lender_data():
    """Display render data in API"""
    lenderData = json.loads(df.to_json(orient='records'))
    return jsonify(lenderData)

# web page that handles user query and displays model results
@app.route('/go', methods=["GET", "POST"])
def go():
    """Display prediction of lenders"""

    if request.method == "POST":

        # save user input
        cityEntry = request.form["cityEntry"]
        stateDropdown = request.form["stateDropdown"]
        mfDropdown = request.form.getlist("mfDropdown")
        yearBuilt = request.form["yearBuilt"]
        numberUnits = request.form["numberUnits"]
        originalLoan = request.form["originalLoan"]
        noteRate = request.form["noteRate"]
        loanTerm = request.form["loanTerm"]
        appraisedValue = request.form["appraisedValue"]

        # retrieve lat and lng based on city and state
        address = f"{cityEntry}, {stateDropdown}"
        api_results = address2api(address)
        lat, lng = api2latlng(api_results)

        # convert user input to dataframe
        user_input_df = pd.DataFrame(columns=features)
        user_input_df['Built'] = [str2num(yearBuilt)]
        user_input_df['Units'] = [str2num(numberUnits)]
        user_input_df['Original Loan'] = [str2num(originalLoan)]
        user_input_df['Note Rate'] = [str2num(noteRate)]
        user_input_df['Loan Term (Original)'] = [str2num(loanTerm)]
        user_input_df['Appraised Value'] = [str2num(appraisedValue)]
        user_input_df['lat'] = [lat]
        user_input_df['lng'] = [lng]

        for mf_col in [col for col in features if "MF" in col]:
            if mf_col.lstrip("MF_") in mfDropdown:
                user_input_df[mf_col] = [1]
            else:
                user_input_df[mf_col] = [0]
        
        # in case of missing values, impute by median
        user_input_df[columns_to_impute] = missing_imputer.transform(user_input_df[columns_to_impute])

        # apply feature scaling (excluding binary features)
        to_scale = [col for col in features if ('MF' not in col)]
        user_input_df[to_scale] = scaler.transform(user_input_df[to_scale])

        # use model to predict top 3 most likely lenders
        probabilities = model.predict_proba(user_input_df.iloc[0:1])[0]
        classes = model.classes_
        top3 = pd.Series(data=probabilities, index=classes).sort_values(ascending=False).iloc[:3]
        top3_lenders = top3.index.tolist()
        top3_prob = top3.values.tolist()

        # import pdb; pdb.set_trace()

        # render the go.html
        return render_template(
            'go.html',
            top3_lenders=top3_lenders,
            top3_prob=top3_prob
        )

    return render_template("master.html")

def main():
    app.run(host='0.0.0.0', port=3001, debug=True)


if __name__ == '__main__':
    main()