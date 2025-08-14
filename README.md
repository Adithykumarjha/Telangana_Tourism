AI-Powered Telangana Tourist Guide

This project is an intelligent web application built with Streamlit that helps users explore Telangana’s tourist attractions, plan trips, receive AI-powered recommendations, and analyze sentiment from visitor reviews. It integrates multiple open-source AI models for Q&A, image recognition, trip planning, and sentiment analysis.

The application allows users to explore places by viewing top attractions in Telangana along with descriptions, images, and interactive maps. It features an AI chatbot that can answer questions about tourist places, history, and travel tips. Users can also upload an image to get AI-generated recommendations for similar tourist spots. A sentiment analysis tool is included to evaluate reviews or comments and determine visitor satisfaction. The trip planner generates itineraries based on user preferences, while interactive maps provide location details and directions.

The tech stack for this project includes Streamlit for the frontend and Python for backend processing. AI capabilities are powered by CLIP for image recognition, DistilBERT for sentiment analysis, and an open-source LLM for tourism Q&A. Mapping functionalities are implemented using Folium and Geopandas. Data is stored locally in JSON and CSV files.

To install the project, first clone the repository from GitHub and navigate into the project directory. Then, create and activate a virtual environment. Install all required dependencies from the requirements.txt file, and finally, run the application using the command streamlit run app.py. The app will open in your browser at http://localhost:8501.

The project directory is organized into a main app.py file, a utils folder containing helper modules such as AI processing, storage handling, and API integration, and a data folder containing datasets of tourist places and reviews. The README.md provides documentation, and a requirements.txt file lists all dependencies.

Once running, the application provides multiple sections: Explore Places, AI Chatbot, Image Search, Trip Planner, and Sentiment Analysis. Users can easily navigate between these features and make use of the AI-powered tools for planning and exploring Telangana.

Planned future enhancements include adding voice-based interaction, integrating real-time weather and transport APIs, and providing multi-language support for Telugu, Hindi, and English.

This project is licensed under the MIT License. Contributions are welcome via pull requests, and major changes should be discussed first by opening an issue.

The project has been developed by Adithy Kumar Jha along with the team members listed in the authors section.
