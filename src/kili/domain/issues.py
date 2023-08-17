from typing import Literal, NewType

IssueType = Literal["ISSUE", "QUESTION"]
IssueStatus = Literal["OPEN", "SOLVED"]

IssueId = NewType("IssueId", str)
