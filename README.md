# Zulip-Voting-Bot

Demo examples for Zulip VotingBot
====

*All examples are in one message, using Shift-Enter*


**To open a vote, post in the public stream:**


VotingBot \<Poll Title\>  
\<Option 1>  
\<Option 2>  
\<...Option N>  
*(note: 1,2,...N are the indices)*

**To cast a vote, in a public message:**

VotingBot \<Poll Title>  
\<Option Index>

**To cast a vote, in a private message:**

\<Poll Title>  
\<Option Index>  
*VotingBot then confirms you have voted, repeating your choice*

**To add a new voting option (only in a public message)
**

VotingBot \<Poll Title>  
Add: \<Option N+1>

*VotingBot will resend all voting options, including latest addition*

**To end the vote and get results (only in a public message)**

VotingBot \<Poll Title>  
results  
*VotingBot publish the results of the voting*

****

**Example:**  
VotingBot Karaoke  
Go to Karaoke Bar  
Go to Hopper room  
Let's do it tomorrow

*From VotingBot*
> Karaoke  
0. Go to Karaoke Bar   
1. Go to Hopper room   
2. Let's do it tomorrow  

*(in public stream)*  
VotingBot Karaoke    
2   
*(in private message to Zulip Voting Bot)*   
Karaoke   
2

>You just voted for 'Let's do it tomorrow'

VotingBot Karaoke  
results

>The results are in!!!!  
Topic: Karaoke  
Go to Karaoke Bar has 0 votes.  
Go to Hopper room has 0 votes.  
Let's do it tomorrow has 1 votes.  