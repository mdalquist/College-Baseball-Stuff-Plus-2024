# College-Baseball-Stuff-Plus-2024

App to search results, calculate Stuff+ from custom metrics, and calculate Stuff+ from one TrackMan CSV file: https://college-baseball-stuff-plus-2024.streamlit.app/

Welcome to the repository for my Stuff+ model! Stuff+ is a metric that has become exceedingly popular in the baseball world over the last few years. It aims to measure how "nasty" a pitch is based on its velocity, movement, release point, and apporach angles. It is often done by predicting the expected run value or expected whiff rate for a pitch and comparing it to the average for the pitch type. My Stuff+ model predicts expected whiff rate (xWhiff), then converts the xWhiff to Stuff+ by computing its percent above or below average and adding it to 100. So, a fastball with an xWhiff 50% higher than average fastballs has a Stuff+ of 150. Similarly, a slider with an xWhiff 15% below the average breaking ball has a Stuff+ of 85.

More explanation about Stuff+ can be found at this article by Jack Lambert at Driveline Baseball: https://www.drivelinebaseball.com/2024/05/revisiting-stuff-plus/?srsltid=AfmBOop8_HQfAcpNc0AZPdG_npFfDNEFw3JG0n0wIjjh2gYwL6dYQopp

To train the model, I gathered all pitches recorded by a TrackMan at a NCAA Division 1 stadium and split them into 3 groups. The Fastball group contains all Four Seam Fastballs, Sinkers (or Two Seam Fastballs, if you prefer), and Cutters thrown by a pitcher whose primary fastball is a cutter. The Breaking Ball group contains all Curveballs, Sliders, and Cutters thrown by a pitcher whose primary fastball is not a cutter (more on why is explained in the notebook). The Offspeed group contains all Changeups, Splitters, and Knuckleballs. Each group is trained separately and has its own model associated with it. Each model is a Random Forest Classifier that predicts the probability of a whiff using the pitch's velocity, induced vertical break, horizontal break, release height, release side, extension, adjusted vertical approach angle, and adjusted horizontal approach angle. Three additional features, velocity difference, IVB difference, and HB difference are included in the breaking ball and offspeed model to capture movement differences from that pitcher's fastball. 

One thing to note about my Stuff+ model is that since it is based on expected whiff percentages, pitches designed to induce soft contact or takes, like sinkers or slow curveballs, respectively, do not grade out well. Remember, the ability to generate whiffs is only one part of being a good pitcher! My model is designed to isolate that specific quality, so the results should be interpreted as such. If a pitch produces good results, no matter what a Stuff+ model says, throw it!

The notebook in the repository contains all of my code, visualizations, comments, and explanations about why I made certain choices in my model. It is a great resource for anyone looking to build their own Stuff+ model!

Explanation of Features
- RelSpeed (Velocity): The speed of the pitch leaving the pitcher's hand (in MPH)
- InducedVertBreak (Induced Vertical Break, IVB): The amount of spin induced vertical break away from a theoretical zero point if the ball were to have no spin or perfectly inefficient spin (in inches) (perfectly inefficient spin is bullet spin)
- HorzBreak (Horizontal Break, HB): The amount of spin induced horizontal break away from a theoretical zero point if the ball had no spin or perfectly inefficient spin (in inches). Positive is towards a right handed hitter, negative is towards a left handed hitter. Right handed pitchers tend to throw fastballs and changeups with positive HB, and breaking balls with negative HB. Left handed pitchers tend to throw fastballs and changeups with negative HB, and breaking balls with positive HB.
- RelHeight (Release Height): The height off the ground the pitch is released from (in feet)
- RelSide (Release Side): The distance away from the center of the rubber the pitch is released from (in feet). Positive is towards third base and negative is towards first base
- Extension: The distance away from the rubber towards home plate the pitch is released from (in feet)
- VertApprAngle (Vertical Approach Angle, VAA): The angle at which the pitch apporaches the plate vertically (in degrees). Closer to 0 means flatter, the more negative meanse steeper.
- HorzApprAngle (Horizontal Approach Angle, HAA): The angle at which the pitch approaches the plate horizontally (in degrees). Positive is towards a left handed hitter, negative is towards a right handed hitter. The larger the absolute value, the steeper the angle.
- VeloDiff: The difference in velocity of a breaking ball or offspeed pitch from the pitcher's primary fastball velocity (in MPH).
- IVBDiff: The difference in induced vertical break of a breaking ball or offspeed pitch from the pitcher's primary fastball induced vertical break (in inches).
- HBDiff: The difference in horizontal break of a breaking ball or offspeed pitch from the pitcher's primary fastball horizontal break (in inches).
