The PostgreSQL account where your database on our server resides
- postgresql://hw2735:5438@35.231.103.173/proj1part2"

The URL of your web application.
- http://35.237.135.30:8111/

A description of the parts of your original proposal in Part 1 that you implemented, 
the parts you did not (which hopefully is nothing or something very small),
and possibly new features that were not included in the proposal and that you implemented anyway.
If you did not implement some part of the proposal in Part 1, explain why.
- Our original proposal called for obtaining statistics of horses, jockey and trainer. which we have finished in part 3.
- We implemented a menu for user to query the winning rate, and first three rate of the 3 entities.
- Also we can define the time horizon to be within the previous x days or x races.
- We also added a custom form where user can input SQL command directly for more complex interactions.

Briefly describe two of the web pages that require the most interesting database operations in terms of what the pages are used for, 
how the page is related to the database operations (e.g., inputs on the page are used in such and such way to produce database operations that do such and such), 
and why you think they are interesting.
- The page integrates two possible DB interactions one via predetermined blanks and another direct SQL entry.
- The most interesting two parts will be the predetermined blanks, it output the rate of winning for each entities (horse, jockey, trainer).
- This operation utilize many subqueries and temporary tables to perform the data slicing and statistics.
- The process is described as a syntax below:
The
winning rate / first three rate (drop down menu)
of
jockey / horse / trainer (drop down menu)
in last N (a number field)
races / days (drop down menu)
- The user will choose each option and a prepared query is used to complete the query
- The prepared query first join the relevant tables (enter_race, race_result, and user selected entity) and use WHERE operation to slice the rows in relevant time frame.
The result is stored in a temporary table
- Two more temporary tables will be created to count the number of first three and total number of races repspectively.
- A final table is generated be dividing the two counts and select the relevant columns.
- This allows use to obtain statistics about the winning / first 3 rate and let betters to know the chances of each entities.