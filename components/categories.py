from flask import render_template, redirect, flash, url_for
from sqlalchemy import func
from werkzeug.exceptions import abort

from data import db_session
from data.problem_category import ProblemCategory
from data.user import User
from forms.edit_category import EditCategoryForm
from forms.submit_category import SubmitCategoryForm

from global_app import get_app
from utils.permissions_required import teacher_required, admin_required
from utils.utils import get_message_from_form

app = get_app()
current_user: User


@app.route('/categories', methods=['GET'])
@admin_required
def categories():
    db_sess = db_session.create_session()
    students = db_sess.query(ProblemCategory).all()
    return render_template('categories.html', **locals())


@app.route('/categories/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit_category(id):
    db_sess = db_session.create_session()
    category = db_sess.query(ProblemCategory).filter(ProblemCategory.id == id).first()
    if not category:
        abort(404)
    form = EditCategoryForm(
        name=category.name
    )
    if form.validate_on_submit():
        if db_sess.query(ProblemCategory).filter(
                func.lower(ProblemCategory.name) == func.lower(form.name.data)). \
                filter(ProblemCategory.id != category.id).first():
            flash('Category with such name already exists', category='danger')
            return render_template('edit_category.html', **locals())
        category.name = form.name.data
        db_sess.commit()
        flash(f'Successfully edited category "{category.name}"', category='success')
        return redirect(url_for('categories'))
    else:
        for i in get_message_from_form(form):
            flash(i, category='danger')
    return render_template('edit_category.html', **locals())


@app.route('/delete_category/<int:id>', methods=['GET'])
@admin_required
def delete_category(id):
    db_sess = db_session.create_session()
    category = db_sess.query(ProblemCategory).filter(ProblemCategory.id == id).first()
    if not category:
        abort(404)
    db_sess.delete(category)
    db_sess.commit()
    flash(f'Successfully deleted category "{category.name}"', category='success')
    return redirect(url_for('categories'))


@app.route('/add_category', methods=['GET', 'POST'])
@admin_required
def add_category():
    db_sess = db_session.create_session()
    form = SubmitCategoryForm()
    if form.validate_on_submit():
        if db_sess.query(ProblemCategory).filter(
                func.lower(ProblemCategory.name) == func.lower(form.name.data)).first():
            flash('Category with such name already exists', category='danger')
            return render_template('add_category.html', **locals())
        category = ProblemCategory()
        category.name = form.name.data
        db_sess.add(category)
        flash(f'Successfully added category "{category.name}"', category='success')
        db_sess.commit()
        return redirect(url_for('categories'))
    else:
        for i in get_message_from_form(form):
            flash(i, category='danger')
    return render_template('add_category.html', **locals())
