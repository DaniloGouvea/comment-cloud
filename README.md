#CommentCloud for Youtube
version 1.0 
8 Nov 2020

CommentCloud for YouTube is a web application whose purpose is to create colored word clouds using the comments and replies of any public YouTube video. It runs on Flask and communicates with Google API to access the YoutTube comment threads and statistics of Youtube videos.

This web application was created as the final projet for the CS50x 2020.

##Installation

The web application naturally does not need installation whenever being hosted online. However, it is not hosted anywhere at the moment and it will only run when served locally (with Live Server extension for VS Code Studio for instance).

CommentCloud was written in Python 3.8.6 and all the modules which were used and their versions can be found in the file 'requirements.txt' in the project root folder. If you want serve the web app locally, it's advisable that you create a virtual environment and install all the requiremtns with the terminal command 'pip install -r requirements.txt'

Also, the application requires a functioning Google API key. A key can be generated on 'console.developers.google.com'.

##Usage

The web app usage if very straightforward: it consists of one page, with two form fields and a button. A second button appears after the first word cloud is generated.

On the first field, the user is supposed to paste (or type in) any YouTube video complete URL as such 'https://www.youtube.com/watch?v=EaOhKg5pKV8'. Any type of string can be inserted in this field. However, the app will point out to the user different error messages in case: 1. the string is not a valid YouTube video URL or 2. the video the URL points too has disabled comments.

The second field, the user can select one of the several predetermined color schemes which will be used to generate the word cloud. If no color scheme is chosen, the web will use a default scheme (Viridis).

When the button 'GENERATE CLOUD' is clicked, 3 things will happen: 1. a word cloud will be generated; 2. a section with the video's information and relevant statistics will be populated and; 3. the video will be embedded on then in a small player.

After the word cloud is generated and shown on the page, a new button will appear ('SAVE CLOUD!'), which allows the user to download the wordcloud figure into their computer.

And that's it!

##Under the hood

Written in Python 3.8.6, CommentCloud is powered by the following modules: Flask, Pillow, Numpy, WordCloud and Matplotlib. 

Additionally, the communication with YouTube Data API is core to the functioning of the application. CommentCloud communicates with and uses information from two YouTube API resources: videos().list() and commentThreads().list().

The web app also relies heavily on Regular Expressions to handle the URL provided by uses and to parse the YouTube video's comments and replies, normalizing the text and extracting only the words.

Lastly, I choose to do all the page CSS styling by myself instead of using external resources such as Bootstrap and such.

##Author and acknowledgments

This web application was conceived and coded exclusively by myself, Danilo Gouvea Silva.

However, I found on the internet many great and useful tutorials and articles on the most diverse themes, made by all kinds of creators. It would be hard to mention all of them but I'll try to name a few: Corey Schafer (YouTube channel), An Object is A (YouTube channel), Treversy Media (YouTube channel), Google Chrome Developers (YouTube Channel), Augusto S. M. Barbosa ('www.itsmeguto.com'), Duong Vu on DataCamp ('www.datacamp.com').

Special mention do W3schools ('www.w3schools.com'), an awesome resource for HTML, CSS and other programming languages.

Also, I'd like to register here a huge thank you to Professor David J. Malan, to Doug Lloyd and Bryan Yu, and to the entire CS50x community on Discord, a lively and helpful bunch of people!

##License
MIT License
