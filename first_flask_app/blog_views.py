from first_flask_app import app
from flask import render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from webforms import PostForm
from db_classes import Posts
from db_config import db

# Add Post Page
@app.route('/add-post', methods=["GET","POST"])
# @login_required
def add_post():
   form = PostForm()

   if form.validate_on_submit():
      poster = current_user.id
      post = Posts(title = form.title.data,
                   content = form.content.data,
                  poster_id = poster,
                   slug = form.slug.data)
      # Clear the form
      form.title.data = ""
      form.content.data = ""
      # form.author.data = ""
      form.slug.data = ""
   # Add post data to databased
      db.session.add(post)
      db.session.commit()
      
      #Return a message
      flash("Blog Post Submitted Successfully!")

      #Redirect to the webpage
   return render_template("add_post.html", form = form)

@app.route('/post/<int:id>')
def post(id):
   post = Posts.query.get_or_404(id)
   return render_template('post.html', post = post)

@app.route('/posts/edit/<int:id>', methods =["GET","POST"])
@login_required
def edit_post(id):
   post = Posts.query.get_or_404(id)
   form = PostForm()
   if form.validate_on_submit():
      post.title = form.title.data
      # post.author = form.author.data
      post.slug = form.slug.data
      post.content = form.content.data

      # Update database
      db.session.add(post)
      db.session.commit()
      flash("Post Has Been Updated!")
      return redirect(url_for('post',id=post.blog_id))

# Pass in form information
   form.title.data = post.title
   # form.author.data = post.author
   form.slug.data = post.slug
   form.content.data = post.content
   return render_template('edit_post.html', form=form)
# Add blog post listing page

# Delete blog post
@app.route('/posts/delete/<int:id>')
@login_required
def delete_post(id):
   post_to_delete = Posts.query.get_or_404(id)
   id = current_user.id
   if id == post_to_delete.poster.id:
      try:
         db.session.delete(post_to_delete)
         db.session.commit()

         # Return a message
         flash("Blog Post Was Deleted!")

         posts = Posts.query.order_by(Posts.date_posted)
         return render_template ("posts.html",
                              posts = posts)

      except:
         flash("Whoops! There was a problem deleting post. Try again.")
         posts = Posts.query.order_by(Posts.date_posted)
         return render_template ("posts.html",
                              posts = posts)
   
   else: 
      flash("You are not authorized to delete that post.")
      posts = Posts.query.order_by(Posts.date_posted)
      return render_template ("posts.html",
                              posts = posts)
   
@app.route('/posts')
def posts():
   # Grab all the posts from the database
   posts = Posts.query.order_by(Posts.date_posted)
   return render_template ("posts.html",
                           posts = posts)
