# nbu-analyzer
## Description
Module provides simple methods to parse and analyze .nbu file with VMSG messages only. 
.nbu file is a standard format for Nokia mobile phones data backup. A message from such file may look like (indentation mine):
```
BEGIN:VMSG
	VERSION:1.1
	X-IRMC-STATUS:READ
	X-IRMC-BOX:INBOX
	X-NOK-DT:19700000T000000Z
	X-MESSAGE-TYPE:DELIVER
	BEGIN:VCARD
		VERSION:3.0
		N:
		TEL:+48XXXXXXXXX
	END:VCARD
	BEGIN:VENV
		BEGIN:VBODY
			Date:01.01.1970 00:00:00
			there goes message
		END:VBODY
	END:VENV
END:VMSG
```

## Features
* **regex search**
    you can use regular expressions to search phrase in stored messages and group results into buckets with given date 
    format following `strftime` standard

## Example
Examples are based on `example.nbu`.
Let's say we want to check how many times phrase 'python' appears in our sent messages each year. 
```python
from nbu import Analyzer

analyzer = Analyzer("example.nbu")
occurs = analyzer.search_regex(Analyzer.MessageType.SENT, r"python", datefmt="%Y")
for bucket in sorted(occurs):
    print("bucket: {0}".format(bucket))
    print("count:  {0}".format(occurs[bucket]["count"]))
```
will produce results:
```
bucket: 2013
count:  1
bucket: 2014
count:  1
```
We may also want to see those messages, then just edit `for` loop:
```python
for bucket in sorted(occurs):
    print("bucket:  {0}".format(bucket))
    for msg in occurs[bucket]["messages"]:
        print("message: {0}".format(msg.content))
```
which will result in:
```
bucket:  2013
message: Python is powerful.
bucket:  2014
message: Meh, this module isn't even pythonic.
```