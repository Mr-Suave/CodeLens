# CodeLens
## Group 9
## Note : To run the tool, naviagate to the root directory of the cloned repo and then run the command : 
```
pip install -r req.txt
```
### What is our project all about?
If you were to contribute to an open source project, or take over your collagues project - you would have to look at their codebase **and understand it throughly.**
Now take a moment to think about how much time you would spend doing that.
>*Understanding someone else's codebase can take a variable amount of time, ranging from a few days to several months, depending on the codebase's size, complexity, and the developer's experience and familiarity with the technologies used.*

Google Search: "how much time does it take to analyse someone else codebase"

Our tool **CodeLens** is all about effectively summarizing entire GitHub repositories and providing the user with a comprehensive report of is really going on.

### How does our tool work?
![Add text](https://hackmd.io/_uploads/HyrWY7b0Jg.png)

- A user who is developing software uses our tool to generate documentation for his code (on three different levels - client, novice developer, senior developer)
- He does so using the command `codelens generate` in his terminal **just before committing his changes.**
 
>**Note:** This tool works on untracked files, if the user runs the command after committing to his repository, it is not going to work, because there are no modified, or untracked files after committing.

- The tool runs , generates documentation and uploads it to the backend database, ready to be fetvhed when some visitor visits the repo.
- Whenever any user tries to visit another person's public repo on his browser, our web extension enables a floating button on the screen which reads `View Documentation` which when clicked loads the documentation from the backend and displays it on the screen.
- If the owner of the repo has not generated a document ever using our command then the tool shall display "No Documentation Generated" or a similar message.

### Technical Details
- **Languages used:** 
    - Python (Backend), 
    - Powershell Scripting Language (For executable bash script), 
    - JavaScript/HTML/CSS (For web extension)
- **Backend Services used:** 
    - Google Drive API ( For storing files )
    - MongoDB ( For storing link to those files )
- **LLMs used to test the model so far:**
    - deepseek-coder-v2:latest
    - deepsek-coder:6.7b
    - Gemini 1.5 Pro (most satisfying results)

### Future developments:
- Add support for various levels of abstractions as described ( novice, senior developer etc)
- Work on accuracy of developed documentation.
- Check if it is feasible to provide a visual representation of the file structure and dependencies using our tool.
- Add support for UML diagrams using modules like `pylint`'s `pyreverse` etc.
- Optimise the documentation process for faster results.
- Add support for multi-language analysis and documentation.

### [GitHub Repo Link](https://github.com/Mr-Suave/CodeLens)

### Contributions:
#### Akshat Kumar
- Worked on creating chrome extension appearing on github repositories for code documentation
- Explored some ML models like CodeT5 and Plbart for documentation of code and helped with some documentation
- Worked on UI of Chrome Extension and ensuring that it opens only on desired URLs
#### Aryan Chauhan 
- Worked on creating backend JS for chrome extension and ensuring proper working of the same.
- Led research by reading a few papers to get insight on what can be done and what cannot.
- Tweaking of UI for chrome extension ( to be released in R2 ) to provide mechanism to display generated documentation.
#### Raghavendra 
* Implemented the authentication system using Google Service Account and created the file upload functionality to Google Drive.
* Set up proper folder organization with **FOLDER_ID** and generated shareable file URLs after upload.
* Implemented the connection to MongoDB which stores the file url, file name  when it is uploaded to the database.
* Created functions to store file URLs with timestamps and created a proper error handling for database operations.
* Worked  closely on connecting the database from localhost to the global server using mongoDB atlas(will successfully complete it by R2).
* Helped in integration of the tool an testing whether the files generated are being stored in drive and mongoDB or not.

#### Sai Krishna

- Worked closely in forming the idea of what is the flow and working of the tool.
- Explored research work that supports the idea of using LLMs for documention task.
- Worked on the python script that takes the GitHub repo link and path of the repo and then scans the repo in the local machine of the developer and extracts the files which are untracked or modified (according to Git Version Control) and writes those files into a folder which is fed to LLM.
- Worked closely in idea of how to effieciently pass the propmt to the LLM and explored ideas like using previous documentation and newly modified files for updating the documantation. 
- Worked closely in testing the use of APIs instead of local models for generating the documentation.
- Involved in integration of different components of the tool and testing.
#### Sri Krishna
- Worked on the python script that takes untracked files and the previous documentation to generate the documentation for various user types using llm.
- Explored how to use ollama to generate documentation using the local model (deepseek coder:6.7b).
- Compared the accuracy of deepseek coder and deepseek coder v2.
- Tested the performance of llm in documentation for merge sort in various languages.
- Implemented code documentation for users- client, senior developer and novice developer using various artifacts like code, readme, commit messages.
- Helped in integration of tool and testing.
#### Anvay Joshi

- Played key role in ideation, goal setting and flowcharting the workflow for the tool.
- Worked on python script to fetch GitHub repo URL and path to root directory of local location of repo on user's PC.
- Explored `pylint`'s' `pyreverse` module for effective generation of UML diagrams.
![WhatsApp Image 2025-03-20 at 13.22.42_5512f78a](https://hackmd.io/_uploads/HJ046db0ke.jpg)
*An example UML Diagram generated from a 280 line object oriented code implementation of School Database*
- Explored and compared accuracies of tool when powered by various local LLMs namely: `deepseek-coder-v2` and `deepseek-coder`
- Integration of code and testing of the tool.
- Worked on prompt to ensure accurate and efficient documentation of code, to suit the needs of the user.
