REPORT OF 3 TECHNICAL ELEMENTS OF SUPERPY:

1. PARENT PARSER
I added a parent parser for the date entries so that the report parsers can
use this parent to avoid unnecessary repitition of code.

2. TRY EXCEPT FOR DATE AND ANSWER
I used try except and raise ValueError to make sure my program won't stop running
when an incorrect character is received.

3. TEMP FILE
To adjust information in the bought.csv file I added a temp file.
First the bought file is copied and the new information is adjusted and saved
to the temp file. Then the temp file is copied to the bought file.