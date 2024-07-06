from flask import send_from_directory
from website import create_app

# Create the Flask application instance
app = create_app()

# Example route to serve uploaded files
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Run the Flask application
if __name__ == "__main__":
    app.run(debug=True)
