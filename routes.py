# In fspp/projects/live_webcam/routes.py
from flask import Blueprint, render_template

live_webcam_bp = Blueprint(
    'live_webcam',
    __name__,
    template_folder='templates'
)

# Route to run the actual webcam viewer
@live_webcam_bp.route('/')
def webcam_home():
    return render_template('live_webcam/webcam_project.html')

# Route for the project's detail page
@live_webcam_bp.route('/details')
def details():
    return render_template('live_webcam/project_detail.html')