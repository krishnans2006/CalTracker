# CalTracker
A calorie intake and exercises recommendation app
![CalTracker Logo](https://cdn.glitch.com/187701c8-e333-4af5-bbc1-7f3bd83c84b0%2Fcatracker.png?v=1607868628032)
## Inspiration
Our inspiration was how during Covid, people weren't able to get enough exercise, which caused them to gain terrible, terrible, calories. With this in mind, we set out to create a program that would help people with incentive to lose calories by doing exercises they enjoyed.
## What it does
Our app let's you input the type of foods you've consumed and the amount, which searches a list of thousands of foods to find the average number of calories for that food. This adds to the daily total of calories consumed. From there, we use machine learning to recommend exercises you can do to lose those calories, which are also based on your previous exercises and habits. If any calories aren't burned in a day, they are shown on to the next day, leaving you with an effective exercise program.
## How we built it
We used Python Flask for the backend, and Flask SQLAlchemy with an SQL Database to store the data. We also used Food Database API to get calorie counts, and used JavaScript fetch requests with the jinja2 templating engine to transfer data between the frontend and backend.
## Our Contributions
### Krishnan Shankar
I contributed mainly by coding the backend of the project. I integrated the APIs and connected the project to an SQL database. I also coded functions to reset the stats daily. I created the app routing system in Flask, to allow multiple routes for loading different webpages or processing data. I also coded the interactions between the types of code, to send and receive data. Finally, I also helped a little with the HTML and CSS, implementing the accordions in the activity page.
### Jonathan Kong
I contributed mainly by playtesting with the code and working on the backend errors. I fixed bugs and added code where nessecary to add to the display. I also created the logo for CalTracker and wrote the descriptions of the project.
### Pi Rogers
I contributed mainly by building the frontend. I wrote html and javascript for the webpage to send data to the server. I also built a simple algorithm in javascript that reccomends activities based on activity history. Finallt, I added simple machine learning algorithms to adapt calorie formulas to become more personalized and accurate over time.
## Challenges we ran into
We had some trouble in the beginning with connecting the lists to our code, but it didn't take long to fix it. It was also difficult to get the machine learning models to work, but we figured it out in the end.
## Accomplishments that we're proud of
We're very proud of spending extra time to create the dark mode theme, because we felt that it would greatly influence how appealing our site would look.
## What we learned
From this project, we learned many things. Firstly, we learned how to host our website on a service, like Glitch. We also learned about using Food APIs, as it was a huge challenge to get a free Food API to link with our project. Finally, we learned to respect everyone's ideas, as without all of our contributions, we would have never come up with this idea or created this website as well as we have now.
## What's next for CalTracker
We plan on trying to add trackers for other ingredients and nutrients, like carbs, protein, and calcium.