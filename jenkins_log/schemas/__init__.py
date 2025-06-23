from typing import List
from pydantic import BaseModel


class Job(BaseModel):
    _class: str
    name: str
    url: str


class JobsList(BaseModel):
    jobs: List[Job]


class Build(BaseModel):
    number: int


class BuildsList(BaseModel):
    firstBuild: Build
    lastCompletedBuild: Build
