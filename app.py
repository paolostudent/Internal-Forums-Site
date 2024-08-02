from flask import send_from_directory
from website import create_app

# Create an instance of the Flask app using the factory function
app = create_app()

# Route to serve uploaded files from the upload folder
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    # Send the requested file from the UPLOAD_FOLDER directory
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Run the app in debug mode if this script is executed directly
if __name__ == "__main__":
    app.run(debug=True)
