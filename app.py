from flask import Flask, request, redirect, render_template, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from datetime import datetime

############################################################
# SETUP
############################################################

app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb://localhost:27017/plantsDatabase"
mongo = PyMongo(app)

############################################################
# ROUTES
############################################################

@app.route('/')
def plants_list():
    """Display the plants list page."""
    plants_data = list(mongo.db.plant.find())

    context = {
        'plants': plants_data,
    }
    return render_template('plants_list.html', **context)

@app.route('/about')
def about():
    """Display the about page."""
    return render_template('about.html')

@app.route('/create', methods=['GET', 'POST'])
def create():
    """Display the plant creation page & process data from the creation form."""
    if request.method == 'POST':
        new_plant = {
            'name': request.form.get('plant_name'),
            'variety': request.form.get('variety'),
            'photo_url': request.form.get('photo'),
            'date_planted': request.form.get('date_planted')
        }
        plant_insert = mongo.db.plants.insert_one(new_plant).inserted_id
        return redirect(url_for('detail', plant_id=plant_insert))
    else:
        return render_template('create.html')


@app.route('/plant/<plant_id>')
def detail(plant_id):
    """Display the plant detail page & process data from the harvest form."""
    # Fetch the plant with the given 'plant_id' from the 'plants' collection
    plant_to_show = mongo.db.plants.find_one({'_id': ObjectId(plant_id)})
    # Fetch all harvests associated with the plant's id from the harvest's collection
    harvests = list(mongo.db.harvests.find({'plant_id': ObjectId(plant_id)}))

    context = {
        'plant' : plant_to_show,
        'harvests': harvests
    }
    return render_template('detail.html', **context)

@app.route('/harvest/<plant_id>', methods=['POST'])
def harvest(plant_id):
    """
    Accepts a POST request with data for 1 harvest and inserts into database.
    """
    # Create a new harvest object using data from the form
    harvested_amount = request.form.get('harvested_amount')
    date_harvested = request.form.get('date_harvested')

    # Convert date_harvested to a datetime object
    date_harvested = (
        datetime.strptime(date_harvested, '%Y-%m-%d')
        if date_harvested else None
    )

    new_harvest = {
        'quantity': harvested_amount,
        'date': date_harvested,
        'plant_id': ObjectId(plant_id)
    }

    # Insert the new harvest into the 'harvests' collection
    mongo.db.harvests.insert_one(new_harvest)
    return redirect(url_for('detail', plant_id=plant_id))

@app.route('/edit/<plant_id>', methods=['GET', 'POST'])
def edit(plant_id):
    """Shows the edit page and accepts a POST request with edited data."""
    if request.method == 'POST':
        # Retrieve updated plant data from the form
        updated_plant = {
            'name': request.form.get('plant_name'),
            'variety': request.form.get('variety'),
            'photo_url': request.form.get('photo'),
            'date_planted': request.form.get('date_planted')
        }
        # Update the plant in the database
        mongo.db.plants.update_one(
            { '_id': ObjectId(plant_id) },
            { '$set': updated_plant }
            )
        
        return redirect(url_for('detail', plant_id=plant_id))
    else:
        # Retrieve the plant to edit
        plant_to_show = mongo.db.plants.find_one({'_id': ObjectId(plant_id)})

        context = {
            'plant': plant_to_show
        }
        return render_template('edit.html', **context)

@app.route('/delete/<plant_id>', methods=['POST'])
def delete(plant_id):
    # TODO: Make a `delete_one` database call to delete the plant with the given
    # id.

    # TODO: Also, make a `delete_many` database call to delete all harvests with
    # the given plant id.

    return redirect(url_for('plants_list'))

if __name__ == '__main__':
    app.run(debug=True)
