# -*- coding: utf-8 -*-
"""
Created on Tue Apr  4 15:53:03 2017

@author: santosh
"""

import os
# We'll render HTML templates and access data sent by POST
# using the request object from flask. Redirect and url_for
# will be used to redirect the user once the upload is done
# and send_from_directory will help us to send/show on the
# browser the file that the user just uploaded
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug import secure_filename
import pandas as pd
# Initialize the Flask application
app = Flask(__name__)

# This is the path to the upload directory
app.config['UPLOAD_FOLDER'] = 'uploads/'
# This is the path to the output directory
app.config['output'] = 'output/'
# These are the extension that we are accepting to be uploaded
app.config['ALLOWED_EXTENSIONS'] = set(['txt'])

# For a given file, return whether it's an allowed type or not
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

# This route will show a form to perform an AJAX request
# jQuery is loaded to execute the request and update the
# value of the operation
@app.route('/')
def index():
    return render_template('index.html')

#page for any errors
@app.route('/error')
def error():
    return render_template('Error.html')

# Route that will process the file upload
@app.route('/upload', methods=['POST'])
def upload():
    #delete any previously calculated outputs
    try:
        os.remove('output/p.txt')
    except OSError:
        pass
    try:
        os.remove('output/z.txt')
    except OSError:
        pass
    # Get the name of the uploaded file
    file = request.files['file']
    print file
    # Check if the file is one of the allowed types/extensions
    if file and allowed_file(file.filename):
        # Make the filename safe, remove unsupported chars
        filename = secure_filename(file.filename)
        # Move the file form the temporal folder to
        # the upload folder we setup
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # Redirect the user to the uploaded_file route, which
        # will basicaly show on the browser the uploaded file
        return redirect(url_for('uploaded_file',
                                filename=filename))
    else:
        #redirect to error page
        return redirect(url_for('error'))
# This route is expecting a parameter containing the name
# of a file. Then it will locate that file on the upload
# directory and show it on the browser, so if the user uploads
# an image, that image is going to be show after the upload

#upload address
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    #read txt as a data frame file using pandas                            
    data = pd.read_csv(os.path.join(app.config['UPLOAD_FOLDER'], filename), sep="\t", header = None)
    column=["Sample", "Cohort", "Fragment Name", "Intensity","Metabolite Name"]
    #check if the uploaded file is valid    
    if len(data.columns)!=5 or sum(data.iloc[0]==column)!=5:
        print ":("
        return redirect(url_for('error'))
    #rename columns of data frame
    data.columns = ["Sample", "Cohort", "FragmentName", "Intensity","MetaboliteName"] 
    #change the type of Intensity to numeric
    data.Intensity=pd.to_numeric(data.Intensity, errors='coerce')
    #pattern for matching in Cohort    
    pattern= r'.*std.*'
    #filter data rows in which Cohort column contains the pattern 'std'
    x=data[data.Cohort.str.contains(pattern)]
    del x['FragmentName']
    #gouping by interested columns
    x=x.groupby(["Sample", "Cohort", "MetaboliteName"]).sum()
    #reseting index
    x=x.reset_index()
    #converting to matrix 
    q=x.as_matrix()
    b=q[:,3]
    a=q[:,1]
    i=0
    z=dict()
    for items in a:
        if(items not in z):
            z[items]=list()
        z[items].append(b[i])
        i=i+1
    
    z=pd.DataFrame(z).T
    z=z.reset_index()
    z.columns = ["Cohort"]+["Intensity"+str(j) for j in range(1,len(z.columns))]
    
    #k=p.groupby('Cohort')['Intensity'].apply(list)
    #k=k.reset_index()
    
    z.to_csv(r'output/z.txt',index=None, sep='\t', mode='a')
    x.to_csv(r'output/p.txt',index=None, sep='\t', mode='a')
    return redirect(url_for('output'))
    #return redirect(url_for('output_files',out1='z.txt',out2='p.txt'))
    #return send_from_directory(app.config['output'],'z.txt')

@app.route('/output')
def output():
    return render_template('output.html')


@app.route('/output/p.txt')
def outp():
    return send_from_directory(app.config['output'],'p.txt')

@app.route('/output/z.txt')
def outz():
    return send_from_directory(app.config['output'],'z.txt')
    
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
