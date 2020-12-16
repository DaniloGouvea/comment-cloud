import os
import re
import sys
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# YouTube API KEY
api_key = os.environ.get("YOUTUBE_API")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        stats = {}
        return render_template("index.html", stats=stats)
    
    else:
        # Get video id from URL provided by user
        url = request.form.get("url")

        if not url:
            flash("Sorry! You must provide a valid YouTube video URL!")
            return redirect("/")

        # Use RegEx to parse url and get video id
        pattern = re.compile(r'https?://www\.youtube\.com/watch\?v=(.{11}).*') 
        videoId = pattern.sub(r'\1', url)

        # Get color scheme for the word cloud
        scheme = request.form.get("scheme")

        
        # Set up communication with YouTube commentThreads().list() API
        youtube = build('youtube', 'v3', developerKey=api_key)

        # Catch expecption in case video id isn't valid or if it the video has disabled comments
        try:
            ytRequest = youtube.commentThreads().list(
                    part="snippet,replies",
                    maxResults=100,
                    order="relevance",
                    textFormat="plainText",
                    videoId=videoId
                )
            response = ytRequest.execute()
        except HttpError as e:
            if e.resp.status == 404:
                flash("Sorry! You must provide a valid YouTube video URL!")
                return redirect("/")
            elif e.resp.status == 403:
                flash("Sorry! The YouTube video you provided has disabled comments. Try another video!")
                return redirect("/")
            else:
                flash("Sorry! We've found an unexpected error with the video. Please try another one!")
                return redirect("/")

        # Stores number o results (top level comments) returned
        results = len(response["items"])

        # RegEx pattern (for extracting words from comments and replies)
        # This pattern removes punctuation and symbols but does not remove contractions nor hyphenated words
        pattern = re.compile(r'\w+(\'?-?\w+)?')

        # Create empty list to store words from comments and from replies
        commentWords = []
        replyWords = []

        # Parse results accessing comments and their replies
        for i in range(results):
            # Stores a top level comment
            topLevelComment = response["items"][i]["snippet"]["topLevelComment"]["snippet"]["textDisplay"]

            # Parse top leveL comment  string with RegEx and add each word found to words[], eliminating punctuation and other symbols   
            matches = pattern.finditer(topLevelComment)
            for word in matches:
                word = word.group(0)
                commentWords.append(word.lower())

            # Store the number of replies a top level comment has
            topLevelCommentReplyCount = response["items"][i]["snippet"]["totalReplyCount"]

            if topLevelCommentReplyCount > 0:
                # Store the number of replies to a top level comment returned by the Api response
                # It might be different from the actual number of existing replies
                # Api documentation suggests using the resource "comments.list() for getting all the existing replies for a comment
                responseReplyCount = len(response["items"][i]["replies"]["comments"])
            
                # Parse each actual reply for words in case there are replies
                for j in range(responseReplyCount):
                    # Store each reply (string) in a variable
                    replyStr = response["items"][i]["replies"]["comments"][j]["snippet"]["textDisplay"]
                    
                    # Parse reply string with RegEx and add each word found to words[], eliminating punctuation and other symbols
                    matches = pattern.finditer(replyStr)
                    for word in matches:
                        word = word.group(0)
                        replyWords.append(word.lower())

        # Create a list containing all words from comments and its replies
        words = commentWords + replyWords
        # Add each word from the words[] to a string which will be used to generate the word cloud
        string = " ".join([str(word) for word in words])
        
        # Stores the number of words in comments
        worc = len(commentWords)
        # Stores the number of words in replies
        worr = len(replyWords)
        # Stores total number of words
        totalwords = "{:,}".format(worc + worr)

        # Create stopword list:
        stopwords = set(STOPWORDS)
        stopwords.update(["não", "na", "uma", "um", "o", "os", "mas", "em", "esse", "essa", "ao", "dele", "essas", "desse",
                            "desses", "dessa", "dessas", "sim", "seu", "seus", "dos", "de", "da", "das", "pra", "meu", "seu", "para",
                            "por", "que", "se", "sua", "eu", "tem", "vai", "still", "will", "são", "só", "lá", "vou", "vai", "sou", "te",
                            "estão", "lá", "está", "estão", "você", "já", "ele", "nós", "nem", "isso", "aí", "né", "aqui", "tá",
                            "ser"])

        mask = np.array(Image.open("static/mask.png"))

        # Temporary string for clouds (just in case)
        # temp_string = "Comment Cloud YouTube"

        # Create and generate a word cloud image:
        wordcloud = WordCloud(width=600, stopwords=stopwords, mode="RGB", background_color="white", colormap=scheme,
                    mask=mask, font_path="Anton-Regular.ttf").generate(string)

        # Matplotlib configuration
        plt.figure()    
        plt.imshow(wordcloud, interpolation="bilinear")
        plt.axis("off")
        # Save the generate word cloud into a file
        plt.savefig("static/cloud.png", transparent=True, bbox_inches="tight")

        # Contact Youtube videos().list() API for video statistics
        ytRequest = youtube.videos().list(
                    part="snippet,statistics",
                    id=videoId
                )
        response = ytRequest.execute()

        # Create empty dict and fill with response data
        stats = {}
        stats["title"] = response["items"][0]["snippet"]["title"]
        stats["channel"] = response["items"][0]["snippet"]["channelTitle"]
        stats["views"] = "{:,}".format(int(response["items"][0]["statistics"]["viewCount"]))
        
        # Handle KeyErrors in case video has disabled likes and dislikes
        try:
            stats["likes"] = "{:,}".format(int(response["items"][0]["statistics"]["likeCount"]))
        except KeyError:
            stats["likes"] = "Not available"
        
        try:
            stats["dislikes"] = "{:,}".format(int(response["items"][0]["statistics"]["dislikeCount"]))
        except KeyError:
            stats["dislikes"] = "Not available"

        stats["comments"] = "{:,}".format(int(response["items"][0]["statistics"]["commentCount"]))
        
        # Finally render the page
        return render_template("cloud.html", videoId=videoId, totalwords=totalwords, stats=stats)
