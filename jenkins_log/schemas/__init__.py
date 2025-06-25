from datetime import datetime
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


class HealthReport(BaseModel):
    description: str


class BuildsList(BaseModel):
    firstBuild: Build
    lastCompletedBuild: Build
    healthReport: List[HealthReport]
    disabled: bool


class ReportJob(BaseModel):
    jobName: str
    url: str


class ReportList(BaseModel):
    jobs: List[ReportJob]
