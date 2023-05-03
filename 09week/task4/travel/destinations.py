from flask import Blueprint, render_template, request, redirect, url_for
from .models import Destination, Comment
from .forms import DestinationForm, CommentForm
from . import db
import os
from werkzeug.utils import secure_filename

bp = Blueprint('destination', __name__, url_prefix='/destinations')

@bp.route('/<id>')
def show(id):
    destination = db.session.execute(db.select(Destination).filter_by(id=id)).scalar_one()
    # create the comment form
    cform = CommentForm()    
    return render_template('destinations/show.html', destination=destination, form=cform)

@bp.route('/create', methods = ['GET', 'POST'])
def create():
  print('Method type: ', request.method)
  form = DestinationForm()
  if form.validate_on_submit():
    #call the function that checks and returns image
    db_file_path=check_upload_file(form)
    destination=Destination(name=form.name.data,description=form.description.data, 
    image=db_file_path,currency=form.currency.data)
    # add the object to the db session
    db.session.add(destination)
    # commit to the database
    db.session.commit()
    print('Successfully created new travel destination', 'success')
    #Always end with redirect when form is valid
    return redirect(url_for('destination.create'))
  return render_template('destinations/create.html', form=form)

def check_upload_file(form):
  #get file data from form  
  fp=form.image.data
  filename=fp.filename
  #get the current path of the module file… store image file relative to this path  
  BASE_PATH=os.path.dirname(__file__)
  #upload file location – directory of this file/static/image
  upload_path=os.path.join(BASE_PATH,'static/image',secure_filename(filename))
  #store relative path in DB as image location in HTML is relative
  db_upload_path='/static/image/' + secure_filename(filename)
  #save the file and return the db upload path  
  fp.save(upload_path)
  return db_upload_path

@bp.route('/<id>/comment', methods=['GET','POST'])
def comment(id):
    form = CommentForm()
    destination = db.session.execute(db.select(Destination).filter_by(id = id)).scalar_one()
    if form.validate_on_submit():
        comment = Comment(text = form.text.data, destination_id = destination.id)
        db.session.add(comment) 
        db.session.commit()
        flash('Your comment has been added', 'success')
    # using redirect sends a GET request to destination.show
    return redirect(url_for('destinations.show',id = id))
    
