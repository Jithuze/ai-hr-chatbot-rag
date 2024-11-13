# AI-HR-Chatbot-RAG
**RAG-Based HR Chatbot** | Bytestrone Internship Project

## Resume Bot

### Overview
The **Resume Bot** is a web application designed to help users upload, manage, and query resumes efficiently. Powered by advanced AI capabilities, this bot can summarize and search through uploaded resumes. The application is developed using the **Flet framework** and integrates with various libraries for document processing and vector database management, enabling a seamless and interactive experience.

### Features
- **Upload Resumes**: Users can upload multiple PDF resumes, which are stored in a dedicated directory. The system supports handling multiple files with ease.
- **Interactive Chat Interface**: The bot features a user-friendly chat interface that allows users to interact with the bot and ask questions related to the uploaded resumes.
- **Document Summarization**: The bot can intelligently summarize the content of uploaded resumes, providing concise and relevant information based on user queries.
- **Search Functionality**: Users can search for specific details within uploaded resumes. The bot returns precise and relevant information from the documents based on the search query.
- **File Management**: The application supports file management features such as handling file replacements and skipping uploads if a file with the same name already exists.
- **Snack Bar Notifications**: Users are notified of successful uploads and actions with snack bar notifications, improving user experience and interaction.

### Requirements
To run this project, ensure you have the following Python packages installed:

- `chroma-hnswlib==0.7.6`
- `chromadb==0.5.5`
- `flet==0.24.1`
- `flet-core==0.24.1`
- `flet-runtime==0.24.1`
- `ollama==0.3.3`
- `PyPDF2==3.0.1`

You can install the required packages using the following command:

```bash
pip install -r requirements.txt
```

### Running the Application
1. **Clone the Repository**: Start by cloning the repository to your local machine.
   ```bash
   git clone https://github.com/your-username/ai-hr-chatbot-rag.git
   ```
2. **Navigate to the Project Directory**: After cloning, move to the project directory:
   ```bash
   cd ai-hr-chatbot-rag
   ```
3. **Install Dependencies**: Ensure that all required dependencies are installed:
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the Application**: Start the application using the following command:
   ```bash
   flet -r main.py
   ```

This will launch the chatbot, and you can interact with it through the web interface.

### Future Improvements
- **Support for more document formats**: Extend file support beyond PDFs, such as DOCX or plain text files.
- **Enhanced Search Capabilities**: Implement more advanced search features, like keyword-based searching and phrase matching.
- **Machine Learning Integration**: Incorporate machine learning models to better analyze resumes, such as skills extraction and experience classification.
